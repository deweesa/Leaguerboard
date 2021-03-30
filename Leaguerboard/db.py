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
from sqlalchemy import text

API_KEY = os.getenv('SECRET_KEY')
PARAMS = {'api_key': API_KEY}

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(pop_db_command)
    app.cli.add_command(clear_summoner)
    app.cli.add_command(clear_match)

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


@click.command('pop-db')
@with_appcontext
def pop_db_command():
    populate_db()
    click.echo('Populated the database.')


@click.command('clear-sum')
@with_appcontext
def clear_summoner():
    with database.engine.connect() as conn:
        conn.execute(text('delete from summoner'))


@click.command('clear-match')
@with_appcontext
def clear_match():
    with database.engine.connect() as conn:
        conn.execute(text('delete * from match'))
        conn.execute(text('vacuum'))


def populate_db():
    with database.engine.connect() as conn:
        gamers = conn.execute(text('select * from gamers')).fetchall()

    populate_summoner(gamers)
    click.echo('Summoner table populated.')

    populate_match()
    click.echo('Match table populated.')


def populate_summoner(gamers):
    for row in gamers:
        with database.engine.connect() as conn:
            exists_check = conn.execute(text('select 1 from summoner where summonername = :sum_name'), sum_name=row['summonername'])

            if(exists_check.fetchone()):
                continue

            response = get_summoner_info(row['summonername'])
            response_tuple = (response['accountId'], response['profileIconId'], response['revisionDate'], response['name'], response['id'], response['puuid'], response['summonerLevel'])
            conn.execute(text('insert into summoner values :response'), response=response_tuple)


def populate_match():
    with database.engine.connect() as conn:
        summoners = conn.execute(text('select summonername, accountid from summoner')).fetchall()

    for summoner in summoners:
        response = get_matchlist(summoner['accountid'])
        beginIndex = 0

        while(response['matches']):
            insert_match_details(response['matches'])
            beginIndex += 100

            response = get_matchlist(summoner['accountid'], beginIndex)


def insert_match_details(matchlist):
    for match in matchlist:
        print(match['gameId'])

        with database.engine.connect() as conn:
            row = conn.execute(text('select 1 from match where gameid = :game_id'), 
                    game_id=match['gameId'])
            
        if(row.fetchone()):
            continue

        if(match['queue'] == 0 or match['queue'] >= 2000):
            continue

        response = get_match_details(match['gameId'])
        if(response is None):
            continue
        
        summoners = {}
        team_win = {}

        try:
            participant_ids = response['participantIdentities']
        except KeyError:
            print(response)
            input("Press any key to continue")

        for participant in participant_ids:
           with database.engine.connect() as conn:
                row = conn.execute(text('select 1 from summoner where summonername = :sum_name'),
                        sum_name=participant['player']['summonerName'])

        if(row.fetchone()):
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

            with database.engine.connect() as conn:
                conn.execute(text('insert into match values :match_tuple'), 
                        match_tuple=match_tuple)


def get_db():
    if 'db' not in g:
        #g.db = create_engine(current_app.config['DATABASE_URI'])
        print('this is no more')
    return 'g.db'



def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
