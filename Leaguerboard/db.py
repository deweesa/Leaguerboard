"""Methods and flask commands used to manage the projects Database. 

This module is used to update and modify the contents of the Leaguerboard
Database. This includes initializing, filling, updating, and clearing data in
the database.

    Typical usage example:

    flask init-db
    flask pop-db
    flask clear-sum

"""
import sqlite3
import time
import os
import requests
import json
import sys

import click
from flask import current_app, g
from flask.cli import with_appcontext
from Leaguerboard.api_wrapper import (get_summoner_info, get_matchlist, get_match_details)
from . import database as db
from Leaguerboard.models import Summoner, Match, MatchStat
from sqlalchemy import text
from sqlalchemy.sql import func


API_KEY = os.getenv('SECRET_KEY')
PARAMS = {'api_key': API_KEY}


def init_app(app):
#    app.cli.add_command(init_db_command)
    app.cli.add_command(pop_db_command)
    app.cli.add_command(clear_summoner)
    app.cli.add_command(clear_match)
    app.cli.add_command(update_match)
    app.cli.add_command(populate_summoner)


@click.command('pop-db')
@with_appcontext
def pop_db_command():
    populate_db()
    click.echo('Populated the database.')


@click.command('clear-sum')
@with_appcontext
def clear_summoner():
    with db.engine.begin() as conn:
        conn.execute(text('delete from summoner'))


@click.command('clear-match')
@with_appcontext
def clear_match():
    with db.engine.begin() as conn:
        conn.execute(text('delete from match'))


def populate_db():
    #with database.engine.begin() as conn:
    #    gamers = conn.execute(text('select * from gamers')).fetchall()

    populate_summoner()
    click.echo('Summoner table populated.')

    populate_match()
    click.echo('Match table populated.')

@click.command('pop-sum')
@with_appcontext
def populate_summoner():
    """Inserts rows into the summoners table.

    Retrieves account information for the summoners based on the SummonerName
    and inserts that data into the summoners table. 
    """
    
    
    # List of summoners who's stats are being tracked for this web app. 
    primary_summoners = ['Amon Byrne', 'BluffMountain', 'BluffMountain72', 
                         'FocusK', 'ForeseenBison', 'Moisturiser', 
                         'Pasttugboat', 'stumblzzz', 'JasaD15']

    # Iterate over the list of summoners and insert their account info into 
    # the summoner table.
    for summoner in primary_summoners:
        exists = Summoner.query.filter_by(name=summoner).first()

        if exists: continue

        response = get_summoner_info(summoner)
        
        if response is None: continue

        new_summoner = Summoner(response, True)

        db.session.add(new_summoner)
        db.session.commit()

    
@click.command('pop-match')
@with_appcontext
def populate_match():
    """Gets match history for each summoner

    Iterate through all the primary summoners from the summoner table and get
    a cumulative match history for the group.
    """
    
    # Get all the primary summoners from the summoner table, and iterate over 
    # them. For each summoner get their entire match history.
    summoners = Summoner.query.filter_by(is_primary=True).all()

    for summoner in summoners:
        response = get_matchlist(summoner.account_id)
        begin_index = 0

        # If the begin_index is greater than the number of matches the API
        # remembers (Matches over 2 years old are not accessible by API) then
        # the response['matches'] is an empty list

        while(response['matches']):
            insert_matches(response['matches'])     

            begin_index += 100
            response = get_matchlist(summoner.account_id, begin_index)

    # For all the matches in the match table, get match details
    #for match in Match.query.all():
    #    insert_match_details(match)


def insert_matches(matchlist, stoping_match=None):
    """Insert matches into match table
    DEPRECATED

    Iterate of the matchlist and insert it's details into the match table.
    Before inserting the match we check if it's already refrenced in the table
    and that it's not a private game or tutorial game. 

    Args:
        matchlist:
            List of (0, 100] matches that a summoner has participated in.
    """

    
    for match in matchlist:
        if stoping_match:
            if match['gameId'] <= stoping_match:
                return []

        exists = Match.query.filter_by(game_id=match['gameId']).first()

        if not exists: 
            if match['queue'] == 0 or match['queue'] >= 2000: continue
        
            db.session.add(Match(match))
            db.session.commit()

        match_details = get_match_details(match['gameId'])
        insert_match_details(match_details)


@click.command('update-match')
@with_appcontext
def update_match():
    """Update the match table

    We go through the table and get the most recent game played from our 
    current match history for each player. We then gather the individual match
    history that haven't been inserted into our tables, then create
    a master list of matches to insert into the tables.
    """
    most_recent_games = []

    sum_ids = db.session.query(Summoner.account_id).\
            filter_by(is_primary=True).all()

    # Get just the account_ids for each of the summoners
    sum_ids = [x[0] for x in sum_ids]

    # Most recent games for each of the summoners in our table.
    most_recent_games = []

    with db.session() as session:
        for sum_id in sum_ids:
            res = session.query(func.max(MatchStat.game_id)).\
                    filter(MatchStat.account_id==sum_id).one()

            # If a summoner in the table doesn't have a match histroy yet, then
            # mark their most recent game as 0. Then thier whole match history
            # is inserted. 
            if res[0] is None:
                most_recent_games.append({"game_id":0, "sum_id":sum_id})
            else:
                most_recent_games.append({"game_id":res[0], "sum_id":sum_id})

    # History_hopper is an array containing arrays of each summoner's match
    # history. Then once we get the history for each of the summoners, we 
    # consolidate each of the arrays into one master history. The match history
    # is iterated through to insert into match and match_stat.
    history_hopper = []
    hop_ix = 0
    for recent_game in most_recent_games:
        response = get_matchlist(recent_game['sum_id'])

        if recent_game['game_id'] >= response['matches'][0]['gameId']:
            continue

        begin_index = 0
        
        history_hopper.append([])
        history_hopper[hop_ix] = []

        while(response['matches']):
            match_list = [x['gameId'] for x in response['matches']]

            if recent_game['game_id'] <= match_list[0] \
               and recent_game['game_id'] >= match_list[-1]:
                index = match_list.index(recent_game['game_id'])
                match_list = match_list[:index]
            elif recent_game['game_id'] >= match_list[0]:
                response['matches'] = None
                continue

            history_hopper[hop_ix] += match_list
            begin_index += 100
            response = get_matchlist(recent_game['sum_id'], begin_index)

        hop_ix += 1

    for i in range(len(history_hopper)):
        history_hopper[i].sort()

    master_list = []

    while history_hopper != []:
        min_game_id = sys.maxsize
        min_game_index = -1

        for i in range(len(history_hopper)):
            if history_hopper[i][0] < min_game_id:
                min_game_id = history_hopper[i][0]
                min_game_index = i

        if len(master_list) == 0: 
            master_list.append(min_game_id)
        elif master_list[-1] != min_game_id: 
            master_list.append(min_game_id)

        history_hopper[min_game_index].remove(min_game_id)
        if history_hopper[min_game_index] == []: 
            del history_hopper[min_game_index]

    print(master_list)
    for match in master_list:
        insert_match_details(match)
        
def insert_match_details(game_id):
    """Inserts rows into match_stat table.

    Inserts basic match details and then more specific match statistics. If a 
    given match is included in the match table, we still iterate through it's 
    participants to check that none of the primary summoners need their match
    details inserted.

    Args:
        game_id: 
            a game_id used to key into the Riot API for match details. 
    """
    

    response = get_match_details(game_id)

    if match['queue'] == 0 or match['queue'] >= 2000: return
    
    # FIXME: None is returned on error from get_match_details. So if there were
    # an error inserting details for match 12345, match 12345 would be absent
    # from records
    if response is None: return

    # Insert into match table if it's not already there
    exists = Match.query.filter_by(game_id=game_id).first()
    print(exists)
    if exists is None:
        match = Match(response['gameId'], response['queueId'], 
                response['seasonId'], response['gameCreation'])
        db.session.add(match)
        db.session.commit()
    

    # Use a dictionary with mapping of participant_id -> account_id to keep 
    # track of the participantId -> PlayerDto mapping in the match response
    # from the API. This is because the MatchDto from the api primarily 
    # refrences participants of that match by a assigned ID.

    primary_participants = {}

    participant_ids = response['participantIdentities']

    for participant_id_dto in participant_ids:
        player_dto = participant_id_dto['player']
        
        # Check to see if the account associated with the p_id is a primary
        # summoner
        if Summoner.query.filter_by(account_id=player_dto['accountId'], 
                                    is_primary=True).first(): 
            p_id = participant_id_dto['participantId']
            primary_participants[p_id] = player_dto['accountId']
   

    # Now that we have the participant_ids mapped to accounts we care about,
    # go through each participant's stat's and insert the details for primary
    # summoners.

    participants = response['participants']

    for participant_dto in participants:
        p_id = participant_dto['participantId']
        if p_id not in primary_participants.keys(): continue # not an account we 
                                                             # care about

        res = MatchStat.query.filter_by(account_id=primary_participants[p_id],
                game_id=game_id).first()

        print(res)
        if res is not None:
            continue

        account_id = primary_participants[p_id]
        match_stats = MatchStat(game_id, account_id,
                                participant_dto['stats'], 
                                participant_dto['championId'],
                                participant_dto['timeline'])

        db.session.add(match_stats)
        db.session.commit()
