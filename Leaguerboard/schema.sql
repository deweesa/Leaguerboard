drop table if exists summoner;
drop table if exists match;
drop table if exists gamers;

create table summoner (
    accountid text primary key,
    profileIconId integer,
    revisionDate integer, 
    summonerName text,
    id text,
    puuid text, 
    summonerLevel integer
);

create table match (
    gameId integer,
    summonerName text,
    win integer,
    champion integer, 
    role text,
    lane text,
    queue integer,
    seasonId integer,
    timestamp integer,
    gameVersion text
);

create table gamers (
    summonerName text
);

insert into gamers values ("Amon Byrne");
insert into gamers values ("BluffMountain");
insert into gamers values ("BluffMountain72");
insert into gamers values ("FocusK");
insert into gamers values ("ForeseenBison");
insert into gamers values ("Moisturiser");
insert into gamers values ("Pasttugboat");
insert into gamers values ("stumblzzz");
insert into gamers values ("JasaD15");
