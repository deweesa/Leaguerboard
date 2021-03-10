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
    ).fetchone()

    win_count = db.execute(
        'select count(1) from match where summonerName = ? and win = 1', (summoner,)
    ).fetchone()

    return 'games: ' + str(game_count[0]) + '\nwins: ' + str(win_count[0]) + "\npercentage: " + "%.2f%%" % (100 * win_count[0]*1.0/game_count[0])
