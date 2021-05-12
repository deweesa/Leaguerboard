from flask import (Blueprint, render_template, request)
from sqlalchemy import select, text, func
from sqlalchemy.orm import sessionmaker
from Leaguerboard.models import (Summoner, MatchStat, Match)
import json
from . import database

bp = Blueprint('summoner', __name__)

@bp.route('/summoners', methods=('GET', 'POST'))
def summoner():
    """Get a list of the primary summoners and dispaly them with links to their 
       stat page
    """

    summoners = Summoner.query.filter_by(is_primary=True).all()
    summoners = [x.name for x in summoners]

    return render_template('summoner/summoner.html', summoners=summoners)

@bp.route('/summoner/<string:summoner>')
def summoner_stats(summoner):
    """Get the Match history for a summoner and dispaly them, as well 
       as liftime game/win count and calculated win percentage
    """
    summoner_info = Summoner.query.filter_by(name=summoner).first()

    match_history = database.session.query(MatchStat, Match).\
            join(Match, MatchStat.game_id==Match.game_id).\
            filter(MatchStat.account_id==summoner_info.account_id).all()

    champ_games = database.session.query(MatchStat.champ, 
            func.count(MatchStat.game_id).label('count')).\
            filter(MatchStat.account_id == summoner_info.account_id).\
            group_by(MatchStat.champ).order_by(text('champ DESC')).all()

    champ_wins = database.session.query(MatchStat.champ,
            func.count(MatchStat.game_id).label('count')).\
            filter(MatchStat.account_id == summoner_info.account_id,
                    MatchStat.win == True).group_by(MatchStat.champ).\
            order_by(text('champ DESC')).all()

    favorite_champ = {
                        'key': -1,
                        'games': -1,
                        'wins': -1,
                      }

    best_champ =      {
                        'key': -1,
                        'games': -1,
                        'wins': 0,
                      }

    champ_stats = []
    games_index = 0
    wins_index = 0

    while games_index < len(champ_games):
        champ = {'key': champ_games[games_index].champ}

        if champ_wins[wins_index].champ != champ['key']:
            champ['wins'] = 0
        else:
            champ['wins'] = champ_wins[wins_index].count
            wins_index += 1

        champ['games'] = champ_games[games_index].count

        games_index += 1
        
        if champ['games'] > favorite_champ['games']:
            favorite_champ = champ

        if champ['wins']/champ['games'] > best_champ['wins']/best_champ['games'] \
                and champ['games'] >= 15:
            best_champ = champ

    win_count = 0
    game_count = 0

    favorite_lane = database.session.query(MatchStat.lane, func.count(MatchStat.lane).label('count')).\
                        filter(MatchStat.champ == favorite_champ['key'], 
                               MatchStat.account_id == summoner_info.account_id).\
                        group_by(MatchStat.lane).order_by(text('count DESC')).all()

    best_lane = database.session.query(MatchStat.lane, func.count(MatchStat.lane).label('count')).\
                        filter(MatchStat.champ == best_champ['key'],
                               MatchStat.account_id == summoner_info.account_id).\
                        group_by(MatchStat.lane).order_by(text('count DESC')).all()

    favorite_role = database.session.query(MatchStat.role, func.count(MatchStat.role).label('count')).\
                        filter(MatchStat.champ == favorite_champ['key'],
                               MatchStat.account_id == summoner_info.account_id).\
                        group_by(MatchStat.role).order_by(text('count DESC')).all()

    best_role = database.session.query(MatchStat.role, func.count(MatchStat.role).label('count')).\
                        filter(MatchStat.champ == best_champ['key'],
                               MatchStat.account_id == summoner_info.account_id).\
                        group_by(MatchStat.role).order_by(text('count DESC')).all()
    
    favorite_lane = favorite_lane[0]
    best_lane = best_lane[0]
    favorite_role = favorite_role[0]
    best_role = best_role[0]

    for match in match_history:
        game_count += 1
        if match.MatchStat.win: win_count += 1
    
    with open('Leaguerboard/static/json/champion_full.json') as f:
        champ_full = json.load(f)
    
    champ_names = champ_full['keys']

    match_history = sorted(match_history, key = lambda x:x.Match.game_id, 
            reverse=True)
    
    return render_template('summoner/summoner_stat.html', summoner=summoner, 
                            win_count=win_count, game_count=game_count, 
                            matches=match_history, 
                            favorite_champ=favorite_champ,
                            best_champ=best_champ,
                            favorite_lane=favorite_lane,
                            favorite_role=favorite_role,
                            best_lane=best_lane,
                            best_role=best_role,
                            champ_names=champ_names, champ_full=champ_full['data'])

