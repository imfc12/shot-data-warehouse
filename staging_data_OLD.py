from nba_api.stats.endpoints.shotchartdetail import ShotChartDetail
from typing import Union, NoReturn
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor, MySQLCursorDict
import mysql.connector as connector
from datetime import datetime
import time
from dotenv import load_dotenv
import os
from tqdm import tqdm

# Load environment for mysql password
load_dotenv()

class DatabaseControl:
    pw = os.getenv('mysql_pw')
    # Connect to db
    connection = connector.connect(host='localhost', user='root', 
                                   password=pw, port=3306, database='shot_eff_whse')
    # Create cursor and start the database, close the cursor immediately as a new one will be created
    cursor = connection.cursor()
    cursor.execute("""USE shot_eff_whse""")
    # Dictionary cursor to return table in dictionary format (team_abbrev, player_id, team_id, player_name), for stored procedure 'TeamPlayers' in get_team()
    cursor_dict = connection.cursor(dictionary=True)

# Holds map of team name -> team abbreviation
team_names_map = {
    'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Charlotte Hornets':'CHA',
    'Chicago Bulls':'CHI', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN',
    'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND',
    'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA',
    'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK',
    'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX',
    'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR',
    'Utah Jazz':'UTA', 'Washington Wizards':'WAS'
}

# Date format received from API is string of 'yyyymmdd', convert to string representation of datetime object 'yyyy-mm-dd'
def get_date_format(date_str: str) -> str:
    return datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')

# Get team abbreviation of player as it's not received from API, also create matchup str for the game eg 'CHI vs. PHI'/ 'HOU @ MIN'
def get_team_and_matchup(team: str, h_team: str, v_team: str) -> tuple[str, str]:
    # Retrieve team abbreviation from the mapped dictionary
    player_team_abbrev = team_names_map[team]
    # If the player's team is the home team...
    if h_team == player_team_abbrev:
        matchup = f'{h_team} vs. {v_team}'
    # Redundant elif but wanted to be clear about the logic. Could also just use 'else'
    elif v_team == player_team_abbrev:
        matchup = f'{v_team} @ {h_team}'
    return player_team_abbrev, matchup

# Function to take in player in ShotChartDetail API
# Returns list of dictionaries, each dictionary is individual player's shot data
def player_shots(p_id: int, t_id: int, season_segment: str) -> list[dict]:
    # API call
    raw = ShotChartDetail(player_id=p_id,
                          team_id=t_id,
                          season_type_all_star=season_segment,
                          clutch_time_nullable='Last 1 Minute', # Used for testing only and retrieve small sample size
                          season_nullable='2024-25',
                          # Ensures made and missed goals are returned
                          context_measure_simple='FGA')

    # Get data in dictionary form
    raw_shots = raw.shot_chart_detail.get_dict()
    # Retrieve headers from the data set
    headers = raw_shots['headers']
    # lowercase each header
    new_headers = [hdr.lower() for hdr in headers]
    # Retrieve result sets from data set
    result_sets = raw_shots['data']
    # list which will contain tuples of each shot data of the player
    player_shots = []
    for r in result_sets:
        # Map the headers and results into dict
        # Each 'r' is a different shot
        current_dict = dict(zip(new_headers, r))
        # Add team_abbrev, matchup from get_team_and_matchup() function
        current_dict['team_abbrev'], current_dict['matchup'] = get_team_and_matchup(current_dict['team_name'], current_dict['htm'], current_dict['vtm'])
        # Change game date to formatted style
        current_dict['game_date'] = get_date_format(current_dict['game_date'])
        # Add season segment 'Playoffs' or 'Regular Season'
        current_dict['season_segment'] = season_segment
        # Remove 'grid_type', 'shot_attempted_flag', unnecessary elements
        current_dict.pop('grid_type', None)
        current_dict.pop('shot_attempted_flag', None)
        # Append the current_dict (r/shot) to the player's total shots in tuple format
        # player_shots.append(tuple(current_dict.values()))
        player_shots.append(current_dict)
    # Return player_shots and use '.extend()' on the team's overall list 'team_shots'
    return player_shots


# Function to retrieve a single team's players from reference table 'ref_teams' JOIN 'ref_players'
# Returns dict with team_id, list of player id's, list of player name
def get_team(team_abbrev: str) -> dict[str, Union[int, list]]:
    # Call stored procedure to receive all players in the given team
    DatabaseControl.cursor_dict.callproc(procname='TeamPlayers', args=[team_abbrev])
    # Empty dict to include team's id, list of each player's id and list of each player's name (debugging)
    team = {}
    # Retrieve stored procesdure results and loop over each row (player)
    for result in DatabaseControl.cursor_dict.stored_results():
        players = result.fetchall()
        for num, player in enumerate(players, start=1):
            # Retrieve the team's id once only, by any player (Whoever is first)
            if num == 1:
                team['team_id'] = player['team_id']
                # And create the structure for the id's and player names
                team['player_ids'] = []
                team['player_names'] = []
            # Append each player's id and name to respective 'team{}' element
            team['player_ids'].append(player['player_id'])
            team['player_names'].append(player['player_name'])
            # TEST debug
            # print(f'Team: {player['team_abbrev']} - P_ID: {player['player_id']} - T_ID: {player['team_id']} - Name: {player['player_name']}')
    return team

# Returns list of dictionaries where values are strings or integers
def nba_team_shots(nba_team: str, season_segment: str) -> list[dict[str | int]]:
    # Call function to retrieve dict of given team
    team_details = get_team(nba_team)
    # Will hold all player shots of team, one dict for each shot
    team_shots = []
    # Loop over the players (id's) of the team
    for pid in tqdm(team_details['player_ids'], desc='Loading Players..'):
        # Contains all shots of a given player
        shots = player_shots(p_id=pid, t_id=team_details['team_id'] ,season_segment=season_segment)
        # Add the shots to the current team's shots
        team_shots.extend(shots)
        # Avoid overloading the API
        time.sleep(1)

    return team_shots

def stage_shots(nba_team: str, nba_season_segment: str) -> NoReturn:
    current_team_shots = nba_team_shots(nba_team, nba_season_segment)
    # Insert into database
    insert_player_shots_query = """
                                INSERT INTO stg_shots (game_id, game_event_id, player_id, player_name, team_id, team_name, team_abbrev, period, minutes_remaining, seconds_remaining, 
                                event_type, action_type, shot_type, shot_zone_basic, shot_zone_area, shot_zone_range, shot_distance, loc_x, loc_y, shot_made_flag, game_date, htm, vtm, matchup, season_segment) 
                                VALUES (%(game_id)s, %(game_event_id)s, %(player_id)s, %(player_name)s, %(team_id)s, %(team_name)s, %(team_abbrev)s, %(period)s, %(minutes_remaining)s, %(seconds_remaining)s, 
                                %(event_type)s, %(action_type)s, %(shot_type)s, %(shot_zone_basic)s, %(shot_zone_area)s, %(shot_zone_range)s, %(shot_distance)s, %(loc_x)s, %(loc_y)s, %(shot_made_flag)s, 
                                %(game_date)s, %(htm)s, %(vtm)s, %(matchup)s, %(season_segment)s)
                                """
    print('Inserting players...')
    DatabaseControl.cursor.executemany(insert_player_shots_query, current_team_shots)
    # Insert into ref_teams.last_updated with '' timestamp

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    update_timestamp_query = "UPDATE ref_teams SET last_updated = %s WHERE team_abbrev = %s"
    DatabaseControl.cursor.execute(update_timestamp_query, (timestamp, nba_team))

    DatabaseControl.cursor.execute("SELECT * FROM ref_teams")
    tms = DatabaseControl.cursor.fetchall()
    for tm in tms:
        print(tm)

    
    # DatabaseControl.connection.commit()


def stage_shots_main(team, season_segment):
    stage_shots(team, season_segment)
    DatabaseControl.connection.close()

if __name__ == "__main__":
    stage_shots_main('HOU', 'Playoffs') # Test arguments














