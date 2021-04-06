from flask import (Blueprint, render_template, request)
#from Leaguerboard.db import get_db
#from Leaguerboard.models import (Summoner, Match)
from sqlalchemy import select, text
import json
from . import database

bp = Blueprint('summoner', __name__)

@bp.route('/summoners', methods=('GET', 'POST'))
def summoner():
    with database.engine.begin() as conn:
        summoners = conn.execute('select summonername from summoner').fetchall()

    return render_template('summoner/summoner.html', summoners=summoners)

@bp.route('/summoner/<string:summoner>')
def summoner_stats(summoner):

    with database.engine.begin() as conn:
        game_count = conn.execute(text('select count(1) from match where summonername = :x'), x=summoner).fetchone()[0]
        win_count = conn.execute(text('select count(1) from match where summonername = :x and win = true'), x = summoner).fetchone()[0]
        matches = conn.execute(text('select * from match where summonername = :x'), x=summoner).fetchall()

    with open('Leaguerboard/static/json/champion_full.json') as f:
        champ_full = json.load(f)
    
    champ_names = champ_full['keys']

    matches = sorted(matches, key = lambda x:x[8], reverse=True)

    return render_template('summoner/summoner_stat.html', summoner=summoner, win_count=win_count, game_count=game_count, matches=matches, champ_names=champ_names)


