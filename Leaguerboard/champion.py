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

#    return json.dumps(champ_dict['Aatrox'], indent=4)
    
