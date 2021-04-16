from flask import (Blueprint, render_template, request, flash, redirect, url_for)
#from Leaguerboard.db import get_db
from sqlalchemy import (select, join, and_)
from sqlalchemy.orm import aliased
from . import database
from Leaguerboard.models import (Summoner, MatchStat, Match)

bp = Blueprint('team', __name__)

@bp.route('/team', methods=('GET', 'POST'))
def team():
    if request.method == 'POST':
        #get the account_id's of the selected team
        team_selection = request.form.getlist('summoner')
        error = None

        # TODO: These errors should probably be flashed
        if(len(team_selection) > 5):
            return "Invalid team: More than 5 players (assuming a lot about \
                    potential games played)"
        if(len(team_selection) < 2):
            return "Invalid team: Please check more than one player"
        
        filtered_games = get_filtered_games(team_selection)
        return str(team_statistics)
        #return render_template('team/team_stats.html', game_count=game_count, win_count=win_count, team_selection=team_selection)

    # Get all the primary summoners and display them for team selection
    else:
        summoners = Summoner.query.filter_by(is_primary=True).all()
        return render_template('team/team.html', summoners=summoners)


def get_filtered_games(team_selection):
    # TODO: - [x] Get the games the teammates have played together
    #             (not exclusive)
    #       - [x] Take the games out that other primary summoners are in
    #       
    # Notes: - Thought about going back to the schmea and including the team
    #          team_id for each summoner, but realized that as long as they
    #          all won/lost then they were on the same team
    #
    #        - Might want a case for when the team_selection is 5. No need
    #          to go through and culling the leftovers.
    
    team_selection.sort()
    s = select(MatchStat.game_id).where(MatchStat.account_id==team_selection[0])
    
    with database.engine.begin() as conn:
       games = conn.execute(s)

    all_games = [x[0] for x in games]
    filtered_games = []
    
    for game_id in all_games:
        s = select(MatchStat.account_id) \
                .where(MatchStat.game_id==game_id)

        with database.engine.begin() as conn:
            participants = conn.execute(s).fetchall()

        participants = [p[0] for p in participants]
        participants.sort()
        #print("Participants {}".format(participants))

        if participants == team_selection:
            filtered_games.append(game_id)
            continue

    return filtered_games
