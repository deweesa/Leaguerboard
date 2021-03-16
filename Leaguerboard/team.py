from flask import (Blueprint, render_template, request)
from Leaguerboard.db import get_db

bp = Blueprint('team', __name__)

@bp.route('/team', methods=('GET', 'POST'))
def team():
    db = get_db()

    if request.method == 'POST':
        team_selection = request.form.getlist('summoner')
        if(len(team_selection) > 5):
            return "Invalid team: More than 5 players (assuming a lot about potential games played)"
        if(len(team_selection) < 2):
            return "Invalid team: Please check more than one player"

        db.execute('drop table if exists team_stat') 
        db.execute('''create table team_stat ( 
                        gameId integ,
                        win integer
                    );''')

        db.execute('insert into team_stat select gameId, win from match where summonerName = ?', (team_selection[0],))

        for teammate in team_selection[1:]:
            db.execute('delete from team_stat where gameId not in (select gameId from match where summonerName = ?)', (teammate,)) 

        db.execute('delete from team_stat where gameId in (select distinct gameId from match where summonerName not in (%s))' % ('?,' *len(team_selection))[:-1],
            tuple(team_selection))

        db.commit()

        game_count = db.execute('select count(gameId) from team_stat').fetchone()[0]

        win_count = db.execute('select count(gameId) from team_stat where win = 1').fetchone()[0]
    
        db.close()

        result = str(team_selection)
        result += '\n Games won: ' + str(win_count)
        result += '\n Games played: ' + str(game_count)

        return render_template('team/team_stats.html', game_count=game_count, win_count=win_count, team=team_selection)

    summoners = db.execute('select summonerName from summoner').fetchall()

    return render_template('team/team.html', summoners=summoners)
