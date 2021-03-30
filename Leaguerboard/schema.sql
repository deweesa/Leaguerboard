DROP TABLE IF EXISTS summoner;
DROP TABLE IF EXISTS match;
DROP TABLE IF EXISTS gamers;
/*DROP TABLE IF EXISTS failed_match_lookup;*/

CREATE TABLE summoner (
    accountid varchar(56) primary key,
    profileIconId smallint,
    revisionDate bigint, 
    summonerName text,
    id varchar(63),
    puuid char(78), 
    summonerLevel bigint
);

CREATE TABLE match (
    gameId bigint,
    summonerName text,
    win boolean,
    champion smallint, 
    role text,
    lane text,
    queue integer,
    seasonId integer,
    timestamp bigint,
    gameVersion text
);

/*CREATE TABLE failed_match_lookup (
    gameId integer
);*/

CREATE TABLE gamers (
    summonerName text
);

INSERT INTO gamers VALUES ('Amon Byrne');
INSERT INTO gamers VALUES ('BluffMountain');
INSERT INTO gamers VALUES ('BluffMountain72');
INSERT INTO gamers VALUES ('FocusK');
INSERT INTO gamers VALUES ('ForeseenBison');
INSERT INTO gamers VALUES ('Moisturiser');
INSERT INTO gamers VALUES ('Pasttugboat');
INSERT INTO gamers VALUES ('stumblzzz');
INSERT INTO gamers VALUES ('JasaD15');
