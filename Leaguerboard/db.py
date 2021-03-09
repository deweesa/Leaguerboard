import sqlite3
import time
import os
import requests
import json

import click
from flask import current_app, g
from flask.cli import with_appcontext

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
    db = get_db()

    db.execute(
        'delete from summoner'
    )

    db.commit()

    db.execute(
        'vacuum'
    )

    db.commit()


@click.command('clear-match')
@with_appcontext
def clear_match():
    db = get_db()

    db.execute(
        'delete from match'
    )

    db.commit()

    db.execute(
        'vacuum'
    )

    db.commit()



def populate_db():
    db = get_db()

    gamers = db.execute(
        'select * from gamers'
    ).fetchall()

    populate_summoner(db, gamers)
    click.echo('Summoner table populated.')

    populate_match(db)
    click.echo('Match table populated.')


def populate_summoner(db, gamers):
    for row in gamers:
        response = requests.get('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + row['summonerName'], params = PARAMS)
        

        while(response.status_code == 429):
            time.sleep(int(response.headers['retry-after']))
            response = requests.get('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + row['summonerName'], params = PARAMS)

        if(response.status_code != 200):
            click.echo(response.json())
            click.echo(row['summonerName'])
            break

        response = response.json()            

        db.execute(
            'insert into summoner values (?,?,?,?,?,?,?)',
            (response['accountId'], response['profileIconId'], response['revisionDate'], 
             response['name'], response['id'], response['puuid'], response['summonerLevel'])
        )
        db.commit()


def populate_match(db):
    summoners = db.execute(
        'select summonerName, accountId from summoner'
    ).fetchall()

    loc_params = {}
    loc_params['api_key'] = PARAMS['api_key']

    for summoner in summoners:
        loc_params['beginIndex'] = 0
        response = requests.get('https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + summoner['accountId'].strip(), params = loc_params)

        while(response.status_code == 429):
            time.sleep(int(response.header['retry-after']))
            response = requests.get('https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + summoner['accountId'], params = loc_params)

        response = response.json()

        while(response['matches']):
            get_match_details(response['matches'], db)

            loc_params['beginIndex'] += 100
            response = requests.get('https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + summoner['accountId'], params = loc_params)

            while(response.status_code == 429):
                time.sleep(int(response.headers['retry-after']))
                response = requests.get('https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + summoner['accountId'], params = loc_params)

            response = response.json()


def get_match_details(matchlist, db):
    for match in matchlist:
        print(match['gameId'])
        row = db.execute('select 1 from match where gameId = ?', (match['gameId'],))
        if(row.fetchone()):
            continue

        if(match['queue'] == 0 || match['queue'] >= 2000):
            continue

        response = requests.get('https://na1.api.riotgames.com/lol/match/v4/matches/' + str(match['gameId']), params = PARAMS)

        while(response.status_code == 429):
            time.sleep(int(response.headers['retry-after']))
            response = requests.get('https://na1.api.riotgames.com/lol/match/v4/matches/' + str(match['gameId']), params = PARAMS)

        #TODO make it so that errors serverside of the api are tried again at a later time
        if(response.status_code >= 500): continue

        if(response.status_code != 200): print(response.json())

        response = response.json()
        
        summoners = {}
        team_win = {}

        participant_ids = response['participantIdentities']

        for participant in participant_ids:
            row = db.execute(
                'select 1 from summoner where summonerName = ?', (participant['player']['summonerName'],)
            )

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
            
            if(team_win[participant['teamId']] == "Fail"): win = 0
            else: win = 1

            champion = participant['championId']

            role = participant['timeline']['role']
            lane = participant['timeline']['lane']

            db.execute(
                'insert into match values (?,?,?,?,?,?,?,?,?,?)',
                (gameId, summonerName, win, champion, role, lane,
                 queue, seasonId, timestamp, gameVersion)
            )
            db.commit()

   
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
