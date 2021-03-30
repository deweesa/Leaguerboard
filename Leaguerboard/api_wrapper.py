import requests
import time
import sqlite3
import json
import inspect
import logging
import os

API_KEY = os.getenv('SECRET_KEY')
PARAMS = {'api_key': API_KEY}
logging.basicConfig(filename='api_log.log')

def get_summoner_info(summonerName: str) -> json:
    url='https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/'
    method_input=summonerName.strip()
    
    return _api_helper(url, method_input, PARAMS)


def get_matchlist(accountId: str, beginIndex: int = 0) -> json:
    local_params = {}
    local_params['api_key'] = PARAMS['api_key']
    local_params['beginIndex'] = beginIndex

    url='https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/'
    method_input=accountId
    
    return _api_helper(url, method_input, local_params)


def get_match_details(matchId, db) -> json:
    url='https://na1.api.riotgames.com/lol/match/v4/matches/'
    method_input=str(matchId)

    return _api_helper(url, method_input, PARAMS)


def _api_helper(url: str, method_input: str, params):
    response = requests.get(url+method_input, params=params)

    while(response.status_code == 429):
        time.sleep(int(response.headers['retry-after']))
        response = requests.get(url+method_input, params=params)

    if(response.status_code == 200):
        return response.json()

    error_type=''  

    if(response.status_code == 400):
        error_type="Bad Request"
    if(response.status_code == 401):
        error_type="Unauthroized"
    if(response.status_code == 403):
        error_type="Forbidden"
    if(response.status_code == 404):
        error_type="Data not found"
    if(response.status_code == 415):
        error_type="Unsupported media type"
    if(response.status_code == 500):
        error_type="Internal Server Error"
    if(response.status_code == 502):
        error_type="Bad gateway"
    if(response.status_code == 503):
        error_type="Service unavailable"
    if(response.status_code == 504):
        error_type="Gateway timeout"

    logging.error("%s - %s\n\tAPI Method: %s\n\tInput: %s\n\tParameters: %s", str(response.status_code), error_type, url, method_input, str(params))

    return None
