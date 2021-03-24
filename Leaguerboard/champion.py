from flask import (Blueprint, render_template, request)
from Leaguerboard.db import get_db
import json

bp = Blueprint('champions', __name__)

@bp.route('/champions', methods=('GET',))
def champions():
    #Right now this is going to spit out champions, but I think it should be limited 
    #   to who has been played, ranked by how much they have been played

    with open('Leaguerboard/static/json/champion_full.json') as f:
        champ_dict = json.load(f)['data']

        champ_list = champ_dict.values()
    
    return render_template('champion/champions.html', champions=champ_list)

@bp.route('/champion/<string:champ>')
def champion(champ):
    with open('Leaguerboard/static/json/champion_full.json') as f:
        champ_full = json.load(f)['data']

    champ_dict = champ_full[champ]
    key = champ_dict['key']

    db = get_db()

    game_count = db.execute('select count(*) from match where champion = ?', (key,)).fetchone()[0] 
    win_count = db.execute('select count(*) from match where champion = ? and win = 1', (key,)).fetchone()[0]

    return render_template('champion/champion.html', champ = champ_dict, game_count = game_count, win_count = win_count)


def champ_winrate(champ_dict):
    db = get_db()
    key = champ_dict['key']
    game_count = db.execute('select count(*) from match where champion = ?', (key,)).fetchone()[0]

    if game_count == 0:
        return 0

    win_count = db.execute('select count(*) from match where champion = ? and win = 1', (key,)).fetchone()[0]

    return 100.0 * win_count / game_count
