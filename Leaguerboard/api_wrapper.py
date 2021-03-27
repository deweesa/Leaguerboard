import requests
import time
import sqlite3
import json
import os

API_KEY = os.getenv('SECRET_KEY')
PARAMS = {'api_key': API_KEY}

def get_summoner_info(summonerName: str) -> json:
    response = requests.get('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + summonerName.strip(), params = PARAMS)

    while(response.status_code == 429):
        time.sleep(int(response.headers['retry-after']))
        response = requests.get('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + summonerName.strip(), params = PARAMS)

    #TODO 5XX errors seem more likely during match requests, do I want to add 
    #     here?

    return response.json()

def get_matchlist(accountId: str, beginIndex: int = 0) -> json:
    local_params = {}
    local_params['api_key'] = PARAMS['api_key']
    local_params['beginIndex'] = beginIndex

    response = requests.get('https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + accountId.strip(), params = local_params)

    while(response.status_code == 429):
        time.sleep(int(response.header['retry-after']))
        response = requests.get('https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + accountId.strip(), params = loc_params)

    return response.json()

#Old database refrence
def get_match_details(matchId, db) -> json:
    response = requests.get('https://na1.api.riotgames.com/lol/match/v4/matches/' + str(matchId), params = PARAMS)

    while(response.status_code == 429):
        time.sleep(int(response.headers['retry-after']))
        response = requests.get('https://na1.api.riotgames.com/lol/match/v4/matches/' + str(matchId), params = PARAMS)

    if(response.status_code >= 500):
        db.execute('insert into failed_match_lookup values (?)', (matchId,)) 
        return None

    return response.json()
