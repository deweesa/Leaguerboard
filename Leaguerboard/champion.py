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

    with database.engine.connect() as conn:
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
    return render_template('champion/champion.html', champ = champ_dict, game_count = game_count, win_count = win_count, player_stats = player_stats)


'''def champ_winrate(champ_dict):
    db = get_db()
    key = champ_dict['key']

    #game_count = db.execute('select count(*) from match where champion = ?', (key,)).fetchone()[0]
    with database.engine.connect() as conn:
        game_count = db.execute(text('select count(1) from match where champion = :champ'), champ=key)

    if game_count == 0:
        return 0

    win_count = db.execute('select count(*) from match where champion = ? and win = 1', (key,)).fetchone()[0]

    return 100.0 * win_count / game_count
'''
