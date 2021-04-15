from flask import (Blueprint, render_template, request, flash, redirect, url_for)
#from Leaguerboard.db import get_db
from sqlalchemy import text
from . import database
from Leaguerboard.models import Summoner

bp = Blueprint('team', __name__)

@bp.route('/team', methods=('GET', 'POST'))
def team():
    if request.method == 'POST':
        team_selection = request.form.getlist('summoner')
        error = None

        # TODO: These errors should probably be flashed
        if(len(team_selection) > 5):
            return "Invalid team: More than 5 players (assuming a lot about potential games played)"
        if(len(team_selection) < 2):
            return "Invalid team: Please check more than one player"
        

        # TODO: - [ ] Get the games the teammates have played togehter 
        #             (not exlusive)
        #       - [ ] Take the games out that other primary summoners have
        #             participated in
        return render_template('team/team_stats.html', game_count=game_count, win_count=win_count, team_selection=team_selection)

    # Get all the primary summoners and display them for team selection
    else:
        summoners = Summoner.query.filter_by(is_primary=True).all()
        return render_template('team/team.html', summoners=summoners)
