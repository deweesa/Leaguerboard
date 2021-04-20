from flask import (Blueprint, render_template, request)
from sqlalchemy import text
import json
from . import database
from Leaguerboard.db import (Summoner, Match, MatchStat)

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

    #match_history = database.session.query(MatchStat, Match, Summoner).\
    #        join(Match, MatchStat.game_id==Match.game_id).all()
    
    #join = database.session.query(MatchStat, Match.timestamp, Summoner.name).\
    #        join(MatchStat.game_id == Match.game_id).\
    #        join(MatchStat.account_id == Summoner.account_id).all()

    matches = database.session.query(MatchStat, Summoner.name, Match.timestamp, 
                                  Match.queue).\
            join(Summoner, MatchStat.account_id == Summoner.account_id).\
            join(Match, MatchStat.game_id == Match.game_id).\
            filter(MatchStat.champ==key).\
            order_by(Match.timestamp.desc()).\
            all()

    print(matches[0].timestamp)
    print(matches[0].MatchStat.win)

    # TODO: Do we care about one for all?
    game_count = len(matches)
    win_count = 0 

    player_stats = {}
    role_count = {}
    lane_count = {}

    for match in matches:
        #if match.MatchStat.win: win_count += 1

        if match.name not in player_stats.keys():
            player_stats[match.name] = {'game_count': 0, 'win_count': 0, 
                    'kills': 0, 'deaths': 0, 'assists': 0}
        
        player_stats[match.name]['game_count'] += 1

        if match.MatchStat.win:
            win_count += 1 #add to global win count for the champion
            player_stats[match.name]['win_count'] += 1 # add to win count for
                                                      # specifc player given
                                                      # this champion
        player_stats[match.name]['kills'] += match.MatchStat.kills
        player_stats[match.name]['deaths'] += match.MatchStat.deaths
        player_stats[match.name]['assists'] += match.MatchStat.assists

        if match.MatchStat.role not in role_count.keys():
            role_count[match.MatchStat.role] = 1
        else:
            role_count[match.MatchStat.role] += 1

        if match.MatchStat.lane not in lane_count.keys():
            lane_count[match.MatchStat.lane] = 1
        else:
            lane_count[match.MatchStat.lane] += 1

    del lane_count['NONE']

    player_stats = player_stats.items()
    player_stats = sorted(player_stats, 
            key=lambda stat_line: stat_line[1]['game_count'], reverse=True)


    return render_template('champion/champion.html', champ=champ_dict, 
            game_count=game_count, win_count=win_count, 
            player_stats=player_stats, role_count=role_count, 
            lane_count=lane_count, match_history=matches)


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
