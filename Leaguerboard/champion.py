from flask import (Blueprint, render_template, request)
from sqlalchemy import text
import json
from . import database

bp = Blueprint('champions', __name__)

@bp.route('/champions', methods=('GET',))
def champions():
    #Right now this is going to spit out champions, but I think it should be limited 
    #   to who has been played, ranked by how much they have been played

    with open('Leaguerboard/static/json/champion_full.json') as f:
        champ_dict = json.load(f)['data']
        f.close()

        champ_list = champ_dict.values()
    
    return render_template('champion/champions.html', champions=champ_list)

@bp.route('/champion/<string:champ>')
def champion(champ):
    with open('Leaguerboard/static/json/champion_full.json') as f:
        champ_full = json.load(f)['data']

    champ_dict = champ_full[champ]
    key = champ_dict['key']

    with database.engine.begin() as conn:
        game_count = conn.execute(text('select count (1) from match where champion = :champ'), champ=key).fetchone()[0]
        win_count = conn.execute(text('select count (1) from match where champion = :champ and win = true'), champ=key).fetchone()[0]

        players = conn.execute(text('select distinct(summonername) from match where champion = :champ'), champ=key)
        
        player_stats = []

        for player in players:
            stat_line = {}
            stat_line['summonername'] = player['summonername']
            stat_line['game_count'] = conn.execute(text('''select count(1) from match 
                                                           where champion = :champ 
                                                                 and summonername = :sum_name'''), 
                                                   champ=key, sum_name=player['summonername']).fetchone()[0]

            stat_line['win_count'] = conn.execute(text('''select count(1) from match 
                                                          where champion = :champ 
                                                                 and summonername = :sum_name 
                                                                 and win = true'''), 
                                                   champ=key, sum_name=player['summonername']).fetchone()[0]

            player_stats.append(stat_line)
            
    player_stats.sort(reverse=True, key=lambda stat_line: stat_line['game_count'])
    
    role_count = get_role_count(key)
    lane_count = get_lane_count(key)

    return render_template('champion/champion.html', champ = champ_dict, game_count = game_count, win_count = win_count, player_stats = player_stats, role_count=role_count, lane_count=lane_count)


def get_role_count(champ_key):
    with database.engine.connect() as conn:
        roles = conn.execute(text('select distinct(role) from match where champion = :champ_key'), champ_key=champ_key).fetchall()
        
        role_stmt = text('select count(1) from match where champion = :champ_key and role = :role')
        
        role_count = {}
        
        for role in roles:
            role_count[role[0]] = conn.execute(role_stmt, champ_key=champ_key, role=role[0]).fetchone()[0]

        return role_count
        
def get_lane_count(champ_key):
    with database.engine.connect() as conn:
        lanes = conn.execute(text('select distinct(lane) from match where champion = :champ_key'), champ_key=champ_key).fetchall()

        lane_stmt = text('select count(1) from match where champion = :champ_key and lane = :lane')
        
        lane_count = {}

        for lane in lanes:
            lane_count[lane[0]] = conn.execute(lane_stmt, champ_key=champ_key, lane=lane[0]).fetchone()[0]

        if 'NONE' in lane_count:
            del lane_count['NONE']

        return lane_count

'''def champ_winrate(champ_dict):
    db = get_db()
    key = champ_dict['key']

    #game_count = db.execute('select count(*) from match where champion = ?', (key,)).fetchone()[0]
    with database.engine.conect() as conn:
        game_count = db.execute(text('select count(1) from match where champion = :champ'), champ=key)

    if game_count == 0:
        return 0

    win_count = db.execute('select count(*) from match where champion = ? and win = 1', (key,)).fetchone()[0]

    return 100.0 * win_count / game_count
'''
