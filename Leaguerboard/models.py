from sqlalchemy import (Table, MetaData)
from . import database as db

class Summoner(db.Model):
    account_id = db.Column(db.String(56), primary_key=True) 
    summoner_level = db.Column(db.BigInteger, nullable=False)
    profile_icon_id = db.Column(db.Integer, nullable=False)
    revision_date = db.Column(db.BigInteger)
    name = db.Column(db.String, nullable=False)
    summoner_id = db.Column(db.String(63), nullable=False)
    puuid = db.Column(db.String(78))
    is_primary = db.Column(db.Boolean, nullable=False)
    
    match_history = db.relationship("SumMatch", order_by="desc(SumMatch.game_id)")

    def __init__(self, response, is_primary=False):
        self.account_id = response['accountId']
        self.summoner_level = response['summonerLevel']
        self.profile_icon_id = response['profileIconId']
        self.revision_date = response['revisionDate']
        self.name = response['name']
        self.summoner_id = response['id']
        self.puuid = response['puuid']
        self.is_primary = is_primary

class Match(db.Model):
    game_id = db.Column(db.Integer, primary_key=True)
    queue = db.Column(db.Integer)
    season_id = db.Column(db.Integer)
    game_version = db.Column(db.String)
    timestamp = db.Column(db.Integer)

    def __inti__(self, response):




class SumMatch(db.Model):
    game_id = db.Column(db.Integer, db.ForeignKey('match.game_id'), primary_key=True)
    account_id = db.Column(db.String(56), db.ForeignKey('summoner.account_id'), primary_key=True)
    win = db.Column(db.Boolean)
    champ = db.Column(db.Integer)
    role = db.Column(db.String)
    lane = db.Column(db.String)
    
    
