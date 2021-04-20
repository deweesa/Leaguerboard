from flask import (Blueprint, render_template, request, flash, redirect, url_for)
from sqlalchemy import (select, join, and_)
from sqlalchemy.orm import aliased
from . import database
from Leaguerboard.models import (Summoner, MatchStat, Match)

bp = Blueprint('team', __name__)

@bp.route('/team', methods=('GET', 'POST'))
def team():
    # TODO: - [ ] Rewrite the template for the page so that there aren't so 
    #             many parameters
    #       - [ ] Document
    if request.method == 'POST':
        team_selection = request.form.getlist('summoner')
        error = None

        # TODO: These errors should probably be flashed
        if(len(team_selection) > 5):
            return "Invalid team: More than 5 players (assuming a lot about \
                    potential games played)"
        if(len(team_selection) < 2):
            return "Invalid team: Please check more than one player"
        
        filtered_games = get_filtered_games(team_selection)
        team_stats = get_stats(filtered_games)
        team_names = get_names(team_selection)        


        return render_template('team/team_stats.html', 
                                game_count=team_stats['total'], 
                                win_count=team_stats['win'], 
                                team_names=team_names)

    # Get all the primary summoners and display them for team selection
    else:
        summoners = Summoner.query.filter_by(is_primary=True).all()
        return render_template('team/team.html', summoners=summoners)


def get_filtered_games(team_selection):
    # TODO: - [x] Get the games the teammates have played together
    #             (not exclusive)
    #       - [x] Take the games out that other primary summoners are in
    #       - [ ] Write documentation 
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

        if participants == team_selection:
            filtered_games.append(game_id)
            continue

    return filtered_games

def get_stats(games):
    team_stats = {}
    won_games = {}

    s = select(MatchStat.game_id, MatchStat.account_id, MatchStat.win) \
            .where(MatchStat.game_id.in_(games))

    with database.engine.begin() as conn:
        game_stats = conn.execute(s).fetchall()

    for game_stat in game_stats:
        if game_stat.game_id in won_games.keys():
            if won_games[game_stat.game_id] != game_stat.win:
                del won_games[game_stat.game_id]
        else:
            won_games[game_stat.game_id] = game_stat.win
    
    team_stats['total'] = len(won_games.values())
    team_stats['win'] = 0
    for result in won_games.values():
        if result: team_stats['win'] += 1

    return(team_stats)

def get_names(selection):
    # TODO: - [ ] Documentation
    s = select(Summoner.name).where(Summoner.account_id.in_(selection))

    with database.engine.begin() as conn:
        names = conn.execute(s).fetchall()

    names = [x[0] for x in names]

    return names
