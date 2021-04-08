from sqlalchemy import (Table, MetaData)
from . import database as db

class Summoner(db.Model):
    account_id = db.Column(db.String(56), primary_key=True) 
    summoner_level = db.Column(db.Integer, nullable=False)
    profile_icon_id = db.Column(db.Integer, nullable=False)
    revision_date = db.Column(db.Integer)
    summoner_name = db.Column(db.String, nullable=False)
    summoner_id = db.Column(db.String(63), nullable=False)
    puuid = db.Column(db.String(78))
    is_primary = db.Column(db.Boolean, nullable=False)
    
    match_history = db.relationship("SumMatch", order_by="desc(SumMatch.game_id)")


class Match(db.Model):
    game_id = db.Column(db.Integer, primary_key=True)
    queue = db.Column(db.Integer)
    season_id = db.Column(db.Integer)
    game_version = db.Column(db.String)
    timestamp = db.Column(db.Integer)



class SumMatch(db.Model):
    game_id = db.Column(db.Integer, db.ForeignKey('match.game_id'), primary_key=True)
    account_id = db.Column(db.String(56), db.ForeignKey('summoner.account_id'), primary_key=True)
    win = db.Column(db.Boolean)
    champ = db.Column(db.Integer)
    role = db.Column(db.String)
    lane = db.Column(db.String)
    
    
