from flask import (Blueprint, render_template, request)
from sqlalchemy import text
import json
from . import database
from Leaguerboard.db import (Summoner, Match, MatchStat)

bp = Blueprint('champions', __name__)

@bp.route('/champions', methods=('GET',))
def champions():
    """Retrieve List of champions with profile icons for display"""
    # Right now this is going to spit out champions, but I think it should be 
    # limited to who has been played, ranked by how much they have been played

    # Retrieve json object full of the champ details
    # FIXME: Might want to add the smaller json file from datadragon because
    #        this the full file is pretty big for just getting the names
    with open('Leaguerboard/static/json/champion_full.json') as f:
        champ_dict = json.load(f)['data']
        f.close()

        champ_list = champ_dict.values()
    
    return render_template('champion/champions.html', champions=champ_list)

@bp.route('/champion/<string:champ>')
def champion(champ):
    """Retrieve the stats for a champion

    Get all the matches this champion has participated in. Stats that are 
    currently displayed are:
       1. Map with the percentage of games played in each lane. Important to 
          note that right now we just remove 'NONE' lane games from % 
          calculation
       2. Table of the players who have played the given champion, their
          win count, game count, win percentage, and lifetime K/D/A
       3. Table of Matches played with the champion with W/L, who played
          it, the lane/role played, K/D/A, and the date/time of the match

    Args:
        champ:
            Integer representing a champion. (223 represents Tahm Kench for 
            example)
    """

    with open('Leaguerboard/static/json/champion_full.json') as f:
        champ_full = json.load(f)['data']

    champ_dict = champ_full[champ]
    key = champ_dict['key']
    
    # We get all the matches where the given champion has been played and 
    # then collect different stats looking through each match in this query
    matches = database.session.query(MatchStat, Summoner.name, Match.timestamp, 
                                  Match.queue).\
            join(Summoner, MatchStat.account_id == Summoner.account_id).\
            join(Match, MatchStat.game_id == Match.game_id).\
            filter(MatchStat.champ==key).\
            order_by(Match.timestamp.desc()).\
            all()

    # TODO: Do we care about One For All?
    #       This implementation could cause issues for One For All
    #       But I don't know if we care about One For ALL
    game_count = len(matches)
    win_count = 0 


    player_stats = {} # Dictionary to keep track of individual player stats
    role_count = {}   
    lane_count = {}   

    # Take a look at every match, and on the individiaul level keep track
    # of someone's game/win count and K/D/A. Also keep track of the lane
    # and role count for the champion as a whole
    for match in matches:
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

    if 'NONE' in lane_count:
        del lane_count['NONE'] # Don't know what to do with NONE lane, so trashing
                               # it for now

    # Convert dictionary to list of tuples, so that we can sort the player
    # stats by number of games played with the given champion.
    player_stats = player_stats.items()
    player_stats = sorted(player_stats, 
            key=lambda stat_line: stat_line[1]['game_count'], reverse=True)


    return render_template('champion/champion.html', champ=champ_dict, 
            game_count=game_count, win_count=win_count, 
            player_stats=player_stats, role_count=role_count, 
            lane_count=lane_count, match_history=matches)


def get_role_count(champ_key):
    """This method is no longer used

    We might want to rewrite this to simplify the champion method
    """
    with database.engine.connect() as conn:
        roles = conn.execute(text('select distinct(role) from match where champion = :champ_key'), champ_key=champ_key).fetchall()
        
        role_stmt = text('select count(1) from match where champion = :champ_key and role = :role')
        
        role_count = {}
        
        for role in roles:
            role_count[role[0]] = conn.execute(role_stmt, champ_key=champ_key, role=role[0]).fetchone()[0]

        return role_count

        
def get_lane_count(champ_key):
    """This method is no longer used

    We might want to rewrite this to simplify the champion method
    """

    with database.engine.connect() as conn:
        lanes = conn.execute(text('select distinct(lane) from match where champion = :champ_key'), champ_key=champ_key).fetchall()

        lane_stmt = text('select count(1) from match where champion = :champ_key and lane = :lane')
        
        lane_count = {}

        for lane in lanes:
            lane_count[lane[0]] = conn.execute(lane_stmt, champ_key=champ_key, lane=lane[0]).fetchone()[0]

        if 'NONE' in lane_count:
            del lane_count['NONE']

        return lane_count
