"""Library of functions used as a wrapper to the Riot API.

Wrapper methods to interact with the Riot API. As of current implementation 
handles errors that occur with querying very quitely. At this point guarnteed 
to run, just not to let you know what's going on super well.

    Typical usage exampe:

    sum_info = get_summoner_info('Bingbong_gaming')
    match_details = get_match_details(12345)
    matchlist = get_matchlist('1ewkdjasdlasd', 100)
                                ^- bingbong's account_id
"""
import requests
import time
import sqlite3
import json
import inspect
import logging
import os
import sys

API_KEY = os.getenv('SECRET_KEY')
PARAMS = {'api_key': API_KEY}
logging.basicConfig(filename='api_log.log')

def get_summoner_info(summonerName: str) -> json:
    """Gets summonerDto from Riot API

    Retrives summonerDto by summoner name from the Riot API. while the summoner
    name is not guaranteed to always be the same, it's the easiest way to get
    the account information for this small group of gamers.

    Args:
        summoner_name:
            A string containing the someone's summoner name.

    Returns:
        a SummonerDto representing a summoner's account infromation.
    """


    url='https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/'
    method_input=summonerName.strip()# name is stripped just in case
    
    return _api_helper(url, method_input, PARAMS)


def get_matchlist(accountId: str, beginIndex: int = 0) -> json:
    """Gets the matchlist from Riot API

    Retrives matchlistDto for an account with up to 100 games in the list. This
    method is the only one that uses more than just the API Key for it's payload
    so we make a new `local_params` dictionary to hold the API Key and 
    begin_index

    Args:
        accountId: 
            A string containing an Account ID for a particular summoner
        beginIndex:
            Starting index for the matchlist, with 0 being the most recent game 
            as the start of the matchlist, and containing 100 or 
            (total games - beginIndex). Whichever is least.

    Returns:
        A matchlistDto if the beginIndex isn't greater than total games 
        avaiable through the API. In which case None is returned.
    """
            
    local_params = {}
    local_params['api_key'] = PARAMS['api_key']
    local_params['beginIndex'] = beginIndex

    url='https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/'
    method_input=accountId
    
    return _api_helper(url, method_input, local_params)


def get_match_details(matchId) -> json:
    """A method to get the details and statistics of a specific match.

    Args:
        MatchId: a long representing a matchId

    Returns:
        A matchDto of the matches statistics.
    """


    url='https://na1.api.riotgames.com/lol/match/v4/matches/'
    method_input=str(matchId)

    return _api_helper(url, method_input, PARAMS)


def _api_helper(url: str, method_input: str, params):
    """A helper method for sending requests to the Riot API.

    This is a method that is used to simplify the public methods in this file.
    Here the timeouts are handled as well as 4xx and 5xx error codes. Any 
    error is logged and handled silently. 

    Note: Longterm it is not intended for 4xx and 5xx errors to be handled so
    quitely. There needs to be a table or queue somewhere to retry requests for
    appropriate error codes.

    Args:
        url:
            What Riot API endpoint are we wanting to access.
        method_input:
            A string that contains the input for the API like account_id,
            game_id, summoner_name, etc.
        params:
            A dicitonary of parameters to sent with the request. This always 
            contains the API Key and optional parameters for the API method if
            needed.

        returns:
            A dictionary of information from whichever endpoint was passed down.
            Currently retuns empty if there was any issue with the request.
    """

    if API_KEY is None:
        sys.exit("Aborting:\n    The API Key has not been set")

    response = requests.get(url+method_input, params=params)

    rCode = response.status_code #status code for response

    while(rCode == 429 or (rcode >= 500 and rcode <= 599):
	if(rcode == 429):
            time.sleep(int(response.headers['retry-after']))
        response = requests.get(url+method_input, params=params)

    if(response.status_code == 200):
        return response.json()

    error_type=''  

    # TODO: maybe change this if block into a dicitionary mapping int->err_type
    # would act a lot like a switch statement instead of this wall of if's
    if(rCode == 400):
        error_type="Bad Request"
    if(rCode == 401):
        error_type="Unauthroized"
    if(rCode == 403):
        sys.exit("Aborting:\n    Please reset the API Key")
        error_type="Forbidden"
    if(rCode == 404):
        error_type="Data not found"
    if(rCode == 415):
        error_type="Unsupported media type"
    if(rCode == 500):
        error_type="Internal Server Error"
    if(rCode == 502):
        error_type="Bad gateway"
    if(rCode == 503):
        error_type="Service unavailable"
    if(rCode == 504):
        error_type="Gateway timeout"

    logging.error("%s - %s\n\tAPI Method: %s\n\tInput: %s\n\tParameters: %s", 
                  str(response.status_code), error_type, url, method_input, 
                  str(params))

    return None
