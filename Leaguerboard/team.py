from flask import (Blueprint, render_template, request)
from Leaguerboard.db import get_db

bp = Blueprint('team', __name__)

@bp.route('/team', methods=('GET', 'POST'))
def team():
    db = get_db()

    if request.method == 'POST':
        if(len(request.form.getlist('summoner')) > 5):
            return "Invalid team: More than 5 players (assuming a lot about potential games played)"
        if(len(request.form.getlist('summoner')) < 2):
            return "Invalid team: Please check more than one player"

        

        return str(request.form.getlist('summoner'))

    summoners = db.execute('select summonerName from summoner').fetchall()

    return render_template('team/team.html', summoners=summoners)
