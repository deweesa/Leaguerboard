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
            group_by(MatchStat.champ).order_by(text('count DESC')).all()

    champ_wins = database.session.query(MatchStat.champ,
            func.count(MatchStat.game_id).label('count')).\
            filter(MatchStat.account_id == summoner_info.account_id,
                    MatchStat.win == True).group_by(MatchStat.champ).\
            order_by(text('count DESC')).all()

    favorite_champ = {
                        'key':champ_games[0].champ, 
                        'games':champ_games[0].count,
                        'wins':champ_wins[0].count,
                      }

    

    win_count = 0
    game_count = 0

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
                            champ_names=champ_names, champ_full=champ_full['data'])

