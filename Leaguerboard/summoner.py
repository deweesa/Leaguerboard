from flask import (Blueprint, render_template, request)
from Leaguerboard.db import get_db

bp = Blueprint('summoner', __name__)

@bp.route('/summoner', methods=('GET', 'POST'))
def summoner():
    if request.method == 'POST':
        return "Stat page is work in progress"
    
    db = get_db()
    summoners = db.execute(
        'select summonerName from summoner'
    ).fetchall()
    
    return render_template('summoner/summoner.html', summoners=summoners)
