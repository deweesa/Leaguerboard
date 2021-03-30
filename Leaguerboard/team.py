from flask import (Blueprint, render_template, request, flash, redirect, url_for)
#from Leaguerboard.db import get_db
from sqlalchemy import text
from . import database

bp = Blueprint('team', __name__)

@bp.route('/team', methods=('GET', 'POST'))
def team():
    #db = get_db()

    if request.method == 'POST':
        team_selection = request.form.getlist('summoner')
        error = None
        if(len(team_selection) > 5):
            return "Invalid team: More than 5 players (assuming a lot about potential games played)"
        if(len(team_selection) < 2):
            return "Invalid team: Please check more than one player"
        
        with database.engine.begin() as conn:
            conn.execute('drop table if exists team_stat')
            conn.execute('''create table team_stat (
                                gameId BigInt,
                                win Boolean
                            )''')

            conn.execute(text('insert into team_stat select gameid, win from match where summonername = :sum_name'), sum_name = team_selection[0])

            for teammate in team_selection[1:]:
                conn.execute(text('delete from team_stat where gameid not in (select gameid from match where summonername = :sum_name)'), sum_name=teammate)
                
            conn.execute(text('delete from team_stat where gameid in (select distinct gameid from match where summonername not in :team)'), team  = tuple(team_selection))

            game_count = conn.execute(text('select count(gameid) from team_stat')).fetchone()[0]
            win_count = conn.execute(text('select count(gameid) from team_stat where win = true')).fetchone()[0]

        return render_template('team/team_stats.html', game_count=game_count, win_count=win_count, team_selection=team_selection)

    with database.engine.begin() as conn:
        summoners = conn.execute('select summonername from summoner').fetchall()

    return render_template('team/team.html', summoners=summoners)
