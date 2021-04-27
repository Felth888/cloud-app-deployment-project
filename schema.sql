DROP TABLE IF EXISTS games;

CREATE TABLE games(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR NOT NULL,
    genre VARCHAR NOT NULL,
    platform VARCHAR NOT NULL,
    progress INTEGER NOT NULL DEFAULT 0.0,
    status TEXT NOT NULL DEFAULT "Unplayed",
    playing BOOLEAN NOT NULL DEFAULT FALSE,
    added DATE NOT NULL DEFAULT CURRENT_DATE,
    beaten DATE,
    completed DATE,
    last_modified DATE NOT NULL DEFAULT CURRENT_DATE);


INSERT INTO games (title, genre, platform, progress, status, added)
    VALUES ("Final Fantasy VI", "JRPG", "PS3", 48, "Unfinished", '2012-09-23');
INSERT INTO games (title, genre, platform, progress, status, added, beaten)
    VALUES ("Assasin's Creed: Origins", "Action RPG", "PS4", 83, "Beaten", '2019-06-12', '2020-01-28');
INSERT INTO games (title, genre, platform, added)
    VALUES ("Final Fantasy IX", "JRPG", "PS1", '2014-12-26');
INSERT INTO games (title, genre, platform)
    VALUES ("Cuphead", "Platformer", "PC");
INSERT INTO games (title, genre, platform, progress, status, added, completed)
    VALUES ("Chrono Cross", "JRPG", "PS3", 100, "Completed", '2010-01-15', '2017-10-22');
INSERT INTO games (title, genre, platform, progress, status)
    VALUES ("Aria", "Action", "PS4", 35, "Abandoned");
INSERT INTO games (title, genre, platform, progress, playing, status)
    VALUES ("God of War", "Action", "PS4", 17, TRUE, "Unfinished");
INSERT INTO games (title, genre, platform, progress, status, added)
    VALUES ("Rayman Legends", "Platformer", "PS4", 76, "Unfinished", '2014-11-14')


