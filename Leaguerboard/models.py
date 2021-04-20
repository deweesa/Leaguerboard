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
    
    match_history = db.relationship("MatchStat", order_by="desc(MatchStat.game_id)")

    def __init__(self, response, is_primary=False):
        self.account_id = response['accountId']
        self.summoner_level = response['summonerLevel']
        self.profile_icon_id = response['profileIconId']
        self.revision_date = response['revisionDate']
        self.name = response['name']
        self.summoner_id = response['id']
        self.puuid = response['puuid']
        self.is_primary = is_primary

    def __str__(self):
        return '[' + self.name + '|' + self.sumoner_level + ']'

class Match(db.Model):
    game_id = db.Column(db.BigInteger, primary_key=True)
    queue = db.Column(db.Integer)
    season_id = db.Column(db.Integer)
    game_version = db.Column(db.String)
    timestamp = db.Column(db.BigInteger, nullable=False)

    def __init__(self, response):
        self.game_id = response['gameId']
        self.queue = response['queue']
        self.season_id = response['season']
        self.timestamp = response['timestamp']
        #game_version is not available in matchlist method.



class MatchStat(db.Model):
    game_id = db.Column(db.BigInteger, db.ForeignKey('match.game_id'), primary_key=True)
    account_id = db.Column(db.String(56), db.ForeignKey('summoner.account_id'), primary_key=True)
    win = db.Column(db.Boolean)
    champ = db.Column(db.Integer)
    role = db.Column(db.String)
    lane = db.Column(db.String)
    items = db.Column(db.String)
    runes = db.Column(db.String)
    stat_perks = db.Column(db.String)
    kills = db.Column(db.Integer)
    deaths = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    
    def __init__(self, game_id, account_id, stats, champ, timeline):
        self.game_id = game_id
        self.account_id = account_id
        self.win = stats['win']
        self.champ = champ
        self.role = timeline['role']
        self.lane = timeline['lane']
        self.items = self.__serialize_items(stats)
        self.runes = self.__serialize_runes(stats)
        self.stat_perks = self.__serialize_stat_perks(stats)
        self.kills = stats['kills']
        self.deaths = stats['deaths']
        self.assists = stats['assists']
    
    def __serialize_items(self, stats):
        return self.__serialize_base(stats, 'item', 6)
       
    def __serialize_runes(self, stats):
        return self.__serialize_base(stats, 'perk', 6)

    def __serialize_stat_perks(self, stats):
        return self.__serialize_base(stats, 'statPerk', 3)
        
    def __serialize_base(self, stats, name, count):
        serialized = ''
        for i in range(count-1):
            serialized += str(stats['{}{}'.format(name, i)]) + ':'

        serialized += str(stats['{}{}'.format(name, count-1)])
        return serialized



    
