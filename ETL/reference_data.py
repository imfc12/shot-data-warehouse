from nba_api.stats.endpoints.playerindex import PlayerIndex
from nba_api.stats.static import teams
from typing import Union
import mysql.connector as connector
from mysql.connector.cursor import MySQLCursor
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Retrieve player details: team, abbreviation, player_id, team_id, first_name, last_name
class ReferencePlayers:
    # Class variable to cache PlayerIndex data across all instances
    _index = PlayerIndex()
    # Class Method retrieves PlayerIndex data from nba_api
    @classmethod
    def _data(cls) -> dict[str, Union[str, int, float]]:
        return cls._index.player_index.get_dict()
    
    def __init__(self):
        # class instance holds raw PlayerIndex data
        self.player_data = self.__class__._data()
        # Empty dictionary to temporary hold restructured player data with '_structure_data'
        self.players_dict = {}
        self._structure_data()

    def _structure_data(self) -> None:
        # Loop over the data and extract only what is needed
        for plyr in self.player_data['data']:
            if plyr[4] == 0:
                continue
            self.players_dict[f'{plyr[2]} {plyr[1]}'] = {
            'player_id': plyr[0],
            'player_name': f'{plyr[2]} {plyr[1]}',
            'team_id': plyr[4]}

    # Method to return the structured players dictionary
    def get_nba_players(self) -> dict[str, dict[str, Union[str, int]]]:
        return self.players_dict
            
    # For debugging
    def insert_into_json(self, path) -> None:
        # Place the restructured data in JSON for later use
        with open(path, 'w') as f:
            json.dump(self.players_dict, f, indent=3)   

    # Count the amount of players returned by the API
    def count_players(self) -> int:
        return len(self.players_dict.keys())
    

class ReferenceTeams:
    # Retrieve team details: team_id, abbreviation, nickname, city, state
    def __init__(self):
        # class instance holds raw PlayerIndex data
        self.teams = teams.get_teams()
        # Empty dictionary to temporary hold restructured player data with '_structure_data'
        self.nba_teams = {}
        self._structure_data()

    def _structure_data(self):
        # Iterate over team data and restructure into 'self.nba_teams' dict
        for team in self.teams:
            self.nba_teams[team['full_name']] = {
                'team_id': team['id'],
                'team_abbrev': team['abbreviation'],
                'team_name': f'{team['full_name']}'
            }
    
    # Method to return the structured players dictionary
    def get_nba_teams(self) -> dict[str, dict[str, Union[str, int]]]:
        return self.nba_teams

    # Debugging use
    def insert_into_json(self, path):
        # Place the restructured data in JSON for later use
        with open(path, 'w') as f:
            json.dump(self.nba_teams, f, indent=3)   

    # Count the amount of players returned by the API
    def count_teams(self) -> None:
        return len(self.nba_teams.keys())    


def insert_players(c: MySQLCursor) -> None:
    ref_players = ReferencePlayers()
    nba_players = ref_players.get_nba_players()

    placeholder_players = []
    for pl in nba_players:
        player_id = nba_players[pl]['player_id']
        player_name = nba_players[pl]['player_name']
        team_id = nba_players[pl]['team_id']
        placeholder_players.append((player_id, player_name, team_id))

    # Create query to insert players
    player_insert_query = f"""INSERT INTO ref_players (player_id, player_name, team_id)
                              VALUES (%s, %s, %s)"""
    # Execute the query
    c.executemany(player_insert_query, placeholder_players)

# Function that holds query to update the players table, for players that may have moved teams
def update_players(c: MySQLCursor) -> None:
    # Create Temp Table to compare to ref_players and then update new records
    c.execute("""CREATE TEMPORARY TABLE temp_players(
                 player_id INT,
                 player_name VARCHAR(45),
                 team_id INT
                 )""")
    
    ref_players = ReferencePlayers()
    nba_players = ref_players.get_nba_players()

    # Holds tuples of players to be passed in the execution query
    placeholder_players = []
    for pl in nba_players:
        player_id = nba_players[pl]['player_id']
        player_name = nba_players[pl]['player_name']
        team_id = nba_players[pl]['team_id']
        placeholder_players.append((player_id, player_name, team_id))

    # Create query to insert players
    temp_player_insert_query = f"""INSERT INTO temp_players (player_id, player_name, team_id)
                              VALUES (%s, %s, %s)"""
    # Execute the query
    c.executemany(temp_player_insert_query, placeholder_players)

    # Updates ref_players with updated player records eg. team_id, player_name (Jimmy Butler -> Jimmy Butler III)
    update_ref_players_query = """
                               UPDATE ref_players AS rp
                               JOIN temp_players AS tp ON rp.player_id = tp.player_id
                               SET rp.team_id = tp.team_id,
                                   rp.player_name = tp.player_name
                               WHERE rp.team_id != tp.team_id OR
                                     rp.player_name != tp.player_name
                               """
    
    # Inserts new player records into ref_players
    insert_ref_players_query = """
                               INSERT INTO ref_players (player_id, player_name, team_id)
                               SELECT tp.player_id, tp.player_name, tp.team_id
                               FROM temp_players tp
                               LEFT JOIN ref_players rp ON tp.player_id = rp.player_id
                               WHERE rp.player_id IS NULL
                               """

    c.execute(update_ref_players_query)
    c.execute(insert_ref_players_query)

def insert_teams(c: MySQLCursor) -> None:
    # Instantiate ReferenceTeams to load teams from stats API
    ref_teams = ReferenceTeams()
    # Get in organise dictionary
    nba_teams = ref_teams.get_nba_teams()
    # Variable contains tuples of each nba team data which will be used for bulk insert
    placeholder_teams = []
    for tm in nba_teams:
        team_id = nba_teams[tm]['team_id']
        team_abbrev = nba_teams[tm]['team_abbrev']
        team_name = nba_teams[tm]['team_name']
        placeholder_teams.append((team_id, team_abbrev, team_name))

    # Create query to insert teams
    team_insert_query = f"""INSERT INTO ref_teams (team_id, team_abbrev, team_name) 
                       VALUES (%s, %s, %s)"""
    # Execute the query
    c.executemany(team_insert_query, placeholder_teams)

# Test function to ensure data is properly loaded
def testing_function(c: MySQLCursor) -> None:
    '''# PLAYERS TEST
    c.execute("""SELECT COUNT(*) FROM ref_players""")
    player_count = c.fetchall()
    print(player_count)
    c.execute("""SELECT player_name FROM ref_players ORDER BY RAND() LIMIT 10""")
    players = c.fetchall()
    for player in players:
        print(player[0])'''
    
    '''# PLAYERS UPDATE TEST
    c.execute("""SELECT * FROM ref_players WHERE player_id IN(1, 2, 2544, 101108)""")
    players = c.fetchall()
    print(players)
    c.execute("""SELECT COUNT(*) FROM ref_players""")
    player_count = c.fetchall()
    print(player_count)'''

    '''
    # TEAMS TEST
    c.execute("""SELECT team_name FROM ref_teams ORDER BY team_name""")
    teams = c.fetchall()
    for team in teams:
        print(team[0])
    '''

# Main database control
def ref_data(first_insert: bool = False) -> None:
    pw = os.getenv('mysql_pw')
    connection = connector.connect(
        host='localhost', user='root', password=pw, port=3306, database='shot_eff_whse'
    )
    cursor = connection.cursor()
    cursor.execute("""USE shot_eff_whse""")
    
    # Indicate first ever insert of player data in ref_players. If so, we don't want to run update_players() unnecessarily
    # Default is False as update_players() will be run only after the first insert
    # First insert must take argument as True
    if first_insert:
        insert_players(c=cursor)
        # If not first insert, we do not want to re-insert teams
        insert_teams(c=cursor)
    else:        
        update_players(c=cursor)

    # testing_function(c=cursor)

    connection.commit()
    connection.close()

if __name__ == "__main__":
    ref_data(True)


