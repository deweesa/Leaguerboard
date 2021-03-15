from flask import (Blueprint, render_template, request)
from Leaguerboard.db import get_db

bp = Blueprint('summoner', __name__)

@bp.route('/summoners', methods=('GET', 'POST'))
def summoner():
    if request.method == 'POST':
        return "Stat page is work in progress"
    
    db = get_db()
    summoners = db.execute(
        'select summonerName from summoner'
    ).fetchall()
    
    return render_template('summoner/summoner.html', summoners=summoners)

@bp.route('/summoner/<string:summoner>')
def summoner_stats(summoner):
    db = get_db()    

    game_count = db.execute(
        'select count(1) from match where summonerName = ?', (summoner,)
    ).fetchone()[0]

    win_count = db.execute(
        'select count(1) from match where summonerName = ? and win = 1', (summoner,)
    ).fetchone()[0]

    return render_template('summoner/summoner_stat.html', summoner=summoner, win_count=win_count, game_count=game_count)
