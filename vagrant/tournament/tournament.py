#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import datetime



def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("delete from standings;")
    connection.commit()
    connection.close()



def deletePlayers():
    """Remove all the player records from the database."""
    deleteMatches()
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("delete from players;")
    connection.commit()
    connection.close()



def countPlayers():
    """Returns the number of players currently registered."""
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("select count(*) from players;")
    rows = cursor.fetchall()
    connection.close()
    return int(rows[0][0])


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("insert into players values ({0}, %s);".format(countPlayers()), (name,))
    connection.commit()
    connection.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("select players.id, name, sum(outcome) as wins, count(outcome) as matches from players, standings where players.id = standings.id group by players.id order by wins desc;")
    rows = cursor.fetchall()
    if num_matches() == 0:
        cursor.execute("select id, name, 0 as wins, 0 as matches from players;")
        rows = cursor.fetchall()
    connection.close()
    return rows

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("insert into standings values ({0}, 0);".format(loser))
    cursor.execute("insert into standings values ({0}, 1);".format(winner))
    connection.commit()
    connection.close()
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    pairings = []
    connection = connect()
    cursor = connection.cursor()
    standings = playerStandings()
    i = 0
    while i < len(standings) - 1:
        a = standings[i]
        b = standings[i + 1]
        pairings.append((a[0], a[1], b[0], b[1]))
        i += 2
    connection.close()
    return pairings

def num_matches():
    """Returns the number of players currently registered."""
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("select count(*) from standings;")
    rows = cursor.fetchall()
    connection.close()
    return int(rows[0][0])





