-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Name-id mappings
create table players (id int primary key, name text);
-- ID, 0 for loss and 1 for win.
create table standings (id int references players (id), outcome int check (outcome = 0 or outcome = 1));