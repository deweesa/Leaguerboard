from flask import (Blueprint, render_template, request)
from sqlalchemy import select, text
from Leaguerboard.models import (Summoner, MatchStat)
import json
from . import database

bp = Blueprint('summoner', __name__)

@bp.route('/summoners', methods=('GET', 'POST'))
def summoner():
    summoners = Summoner.query.filter_by(is_primary=True).all()
    summoners = [x.name for x in summoners]

    return render_template('summoner/summoner.html', summoners=summoners)

@bp.route('/summoner/<string:summoner>')
def summoner_stats(summoner):

    #with database.engine.begin() as conn:
    #    game_count = conn.execute(text('select count(1) from match where summonername = :x'), x=summoner).fetchone()[0]
    #    win_count = conn.execute(text('select count(1) from match where summonername = :x and win = true'), x = summoner).fetchone()[0]
    #    matches = conn.execute(text('select * from match where summonername = :x'), x=summoner).fetchall()

    summoner_info = Summoner.query.filter_by(name=summoner).first()
    match_history = MatchStat.query.\
            filter_by(account_id=summoner_info.account_id).all()

    win_count = 0
    game_count = 0

    for match in match_history:
        game_count += 1
        if match.win: win_count += 1
    
    with open('Leaguerboard/static/json/champion_full.json') as f:
        champ_full = json.load(f)
    
    champ_names = champ_full['keys']

    match_history = sorted(match_history, key = lambda x:x.game_id, 
            reverse=True)
    
    return render_template('summoner/summoner_stat.html', summoner=summoner, 
                            win_count=win_count, game_count=game_count, 
                            matches=match_history, 
                            champ_names=champ_names)

