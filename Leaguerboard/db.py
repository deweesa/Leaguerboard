import sqlite3
import time
import os
import requests
import json

import click
from flask import current_app, g
from flask.cli import with_appcontext
from Leaguerboard.api_wrapper import (get_summoner_info, get_matchlist, get_match_details)
from . import database
from Leaguerboard.models import Summoner, Match, MatchStat
from sqlalchemy import text

API_KEY = os.getenv('SECRET_KEY')
PARAMS = {'api_key': API_KEY}

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(pop_db_command)
    app.cli.add_command(clear_summoner)
    app.cli.add_command(clear_match)
    app.cli.add_command(update_match)

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    
    
    click.echo('Initialized the database.')



@click.command('pop-db')
@with_appcontext
def pop_db_command():
    populate_db()
    click.echo('Populated the database.')


@click.command('clear-sum')
@with_appcontext
def clear_summoner():
    with database.engine.begin() as conn:
        conn.execute(text('delete from summoner'))


@click.command('clear-match')
@with_appcontext
def clear_match():
    with database.engine.begin() as conn:
        conn.execute(text('delete from match'))


def populate_db():
    #with database.engine.begin() as conn:
    #    gamers = conn.execute(text('select * from gamers')).fetchall()

    populate_summoner()
    click.echo('Summoner table populated.')

    populate_match()
    click.echo('Match table populated.')


def populate_summoner():
    #primary_summoners = ['Amon Byrne', 'BluffMountain', 'BluffMountain72', 'FocusK',
    #        'ForeseenBison', 'Moisturiser', 'Pasttugboar', 'stumblzzz', 'JasaD15']
    primary_summoners = ['JasaD15']
    for summoner in primary_summoners:
        exists = Summoner.query.filter_by(name=summoner).first()

        if exists: continue

        response = get_summoner_info(summoner)
        
        if response is None: continue

        new_summoner = Summoner(response, True)

        database.session.add(new_summoner)
        database.session.commit()

    
def populate_match():
    summoners = Summoner.query.filter_by(is_primary=True).all()
    for summoner in summoners:
        response = get_matchlist(summoner.account_id)
        begin_index = 0

        while(response['matches']):
            insert_matches(response['matches'])     

            begin_index += 100
            response = get_matchlist(summoner.account_id, begin_index)

    for match in Match.query.all():
        insert_match_details(match)


def insert_matches(matchlist):
    for match in matchlist:
        exists = Match.query.filter_by(game_id=match['gameId']).first()
        if exists: continue

        if match['queue'] == 0 or match['queue'] >= 2000: continue
        
        database.session.add(Match(match))
        database.session.commit()


@click.command('update_match')
@with_appcontext
def update_match():
    with database.engine.begin() as conn:
        summoners = conn.execute(text('select * from summoner')).fetchall()

    most_recent_games = []

    for summoner in summoners:
        with database.engine.begin() as conn:
            most_recent_in_db = conn.execute(text('select max(gameid) from match where summonername = :sum_name'), sum_name=summoner['summonername']).fetchone()[0]
        
        pair = {}
        pair['accountid'] = summoner['accountid']
        pair['gameid'] = most_recent_in_db
        most_recent_games.append(pair)        

    beginIndex = 0
    for game_account_pair in most_recent_games:
        response = get_matchlist(game_account_pair['accountid'])
        
        #the first game from this is older than the most recent game in the db, so 
        #go to next game/account pair
        print(response['matches'])
        if response['matches'][0]['gameId'] <= game_account_pair['gameid']:
            beginIndex = 0
            continue

        insert_match_details(response['matches'])
        beginIndex += 100

        
def insert_match_details(match):
    response = get_match_details(match.game_id)
    
    if response is None: return

    primary_participants = {}

    participant_ids = response['participantIdentities']

    for participant_id_dto in participant_ids:
        player_dto = participant_id_dto['player']
        
        if Summoner.query.filter_by(account_id=player_dto['accountId'], is_primary=True).first():
            p_id = participant_id_dto['participantId']
            primary_participants[p_id] = player_dto['accountId']
    
    participants = response['participants']
    for participant_dto in participants:
        p_id = participant_dto['participantId']
        if p_id not in primary_participants.keys(): continue

        account_id = primary_participants[p_id]
        match_stats = MatchStat(match.game_id, account_id, participant_dto['stats'], 
                participant_dto['championId'], participant_dto['timeline'])

        database.session.add(match_stats)
        database.session.commit()
     
    ''' 
    for match in matchlist:

        with database.engine.begin() as conn:
            row = conn.execute(text('select 1 from match where gameid = :game_id'), 
                    game_id=match['gameId'])
            
        existence = row.fetchone()  

        if existence:
            print('skipping, game already in')
            continue

        if(match['queue'] == 0 or match['queue'] >= 2000):
            continue


        response = get_match_details(match['gameId'])
        if(response is None):
            continue

        print(match['gameId'])
        
        summoners = {}
        team_win = {}

        try:
            participant_ids = response['participantIdentities']
        except KeyError:
            print(response)
            input("Press any key to continue")

        for participant in participant_ids:
            with database.engine.begin() as conn:
                row = conn.execute(text('select 1 from summoner where summonername = :sum_name'),
                        sum_name=participant['player']['summonerName'])

            if(row.fetchone()):
                print('are summoners being added')
                summoners[participant['participantId']] = participant['player']['summonerName']

        teams = response['teams']

        for team in teams:
            team_win[team['teamId']] = team['win']

        participants = response['participants']

        gameId = match['gameId']
        timestamp = match['timestamp']
        gameVersion = response['gameVersion']
        queue = response['queueId']
        seasonId = response['seasonId']

        for participant in participants:
            if participant['participantId'] not in summoners.keys():
                continue

            summonerName = summoners[participant['participantId']]
            
            if(team_win[participant['teamId']] == "Fail"): win = False
            else: win = True

            champion = participant['championId']

            role = participant['timeline']['role']
            lane = participant['timeline']['lane']

            match_tuple = (gameId, summonerName, win, champion, role,
                           lane, queue, seasonId, timestamp, gameVersion)

            with database.engine.begin() as conn:
                print('this is the insert ' +str(gameId))
                conn.execute(text('insert into match values :match_tuple'), 
                        match_tuple=match_tuple)
        '''


def get_db():
    if 'db' not in g:
        #g.db = create_engine(current_app.config['DATABASE_URI'])
        print('this is no more')
    return 'g.db'



def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
