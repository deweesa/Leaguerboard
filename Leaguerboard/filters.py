from jinja2 import evalcontextfilter
from flask import current_app

def readable(value):
    words = value.split('_')

    result = ''
    
    for word in words:
        result += word.capitalize() + ' '
    
    result = result.strip()
    return result

def queue(value):
    queue_mapping = {
            0: "Custom Games",
            72: "1v1 Snowdown Showdown",
            73: "2v2 Snowdown Showdown",
            75: "6v6 Hexakill",
            76: "Ultra Rapid Fire",
            78: "One For All: Mirror Mode",
            83: "Co-op vs AI Ultra Rapid Fire",
            98: "6v6 Hexakill",
            100: "5v5 ARAM",
            310: "Nemesis",
            313: "Black Market brawlers",
            317: "Definitely Not Dominion",
            325: "All Random",
            400: "5v5 Draft Pick",
            420: "5v5 Blind Pick",
            430: "5v5 Blind Pick",
            440: "5v5 Ranked Flex",
            450: "5v5 ARAM",
            460: "3v3 Blind Pick",
            600: "Blood Hunt Assassin",
            610: "Dark Star: Singularity",
            700: "Clash",
            820: "Co-op vs. AI Beginner Bot",
            830: "Co-op vs. AI Intro Bot",
            840: "Co-op vs. AI Beginner Bot",
            850: "Co-op vs. AI Intermediate Bot",
            900: "URF",
            910: "Ascension",
            920: "Legend of the Poro King",
            940: "Nexus Siege",
            950: "Doom Bots Voting",
            960: "Doom Bots Standard",
            980: "Star Guardian Invasion: Normal",
            990: "Star Guardian Invasion: Onslaught",
            1000: "PROJECT: Hunters",
            1010: "Snow ARURF",
            1020: "One for All",
            1030: "Odyssey Extraction: Intro",
            1040: "Odyssey Extraction: Cadet",
            1050: "Odyssey Extraction: Crewmember",
            1060: "Odyssey Extraction: Captain",
            1070: "Odyssey Extraction: Onslaught",
            1090: "Teamfight Tactics",
            1100: "Ranked Teamfight Tactics",
            1110: "Teamfight Tactics Tutorial",
            1111: "Teamfight Tactics test",
            1300: "Nexus Blitz",
    }

    return queue_mapping[value]

