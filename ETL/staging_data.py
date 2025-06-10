from nba_api.stats.endpoints.shotchartdetail import ShotChartDetail
from staging_utils import Month, ClutchTime, DatabaseControl
from typing import Union, NoReturn
# from mysql.connector.connection import MySQLConnection
# from mysql.connector.cursor import MySQLCursor, MySQLCursorDict
from datetime import datetime
from tqdm import tqdm
import time


class StageTeamShotData(ClutchTime, Month, DatabaseControl):
# Holds map of team name -> team abbreviation
    team_names_map = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Charlotte Hornets':'CHA',
                      'Chicago Bulls':'CHI', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN',
                      'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND',
                      'LA Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA',
                      'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK',
                      'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX',
                      'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR',
                      'Utah Jazz':'UTA', 'Washington Wizards':'WAS'}
    # Team name abbreviations used throughout the code
    team_names = [abbrev for abbrev in team_names_map.values()]
    # Set season segments
    allowed_season_segments = ['Regular Season', 'Playoffs']
    # Set clutch times allowed
    allowed_clutch_times = [val for key, val in vars(ClutchTime).items() if not key.startswith('__')]
    # Set allowed month values
    allowed_months = [key for key in Month.months.keys()]
    # Allow visualisation of month:int map
    month_map = Month.months

    def __init__(self, team: str = None, season_segment: str = None):
        # Check if team name is correct (abbreviation)
        self._team = team if team in self.__class__.team_names else None
        # Check if season segment is correct
        self._season_segment = season_segment if season_segment in self.__class__.allowed_season_segments else None
        # clutch_time_setting for testing purposes only
        self._clutch_time_setting = self.__class__.none_clutch
        # Month for testing purposes only
        self._month_setting: int = self.__class__.months['all months']

    # Getter for team: allows access to the current team
    @property
    def team(self) -> str:
        return self._team
    # Setter for team: allows updating the team
    @team.setter
    def team(self, new_team) -> None:
        if new_team in self.__class__.team_names:
            self._team = new_team
        else:
            raise ValueError(f'Invalid team: {new_team}. Must be one of: {self.__class__.team_names}')

    # Getter for season_segment: allows access to the current season segment
    @property
    def season_segment(self) -> str:
        return self._season_segment
    # Setter for season_segment: allows updating the season segment
    @season_segment.setter
    def season_segment(self, segment) -> None:
        if segment in self.__class__.allowed_season_segments:
            self._season_segment = segment
        else:
            raise ValueError(f'Invalid season segment: {segment}. Must be one either: "Regular Season" or "Playoffs"')
    # Getter for clutch_time: allows access to the clutch time setting. Default set at initialisation

    @property
    def clutch_time_setting(self) -> str:
        return self._clutch_time_setting
    # Setter for season_segment: allows updating the season segment
    @clutch_time_setting.setter
    def clutch_time_setting(self, clutch_setting) -> None:
        if clutch_setting not in self.__class__.allowed_clutch_times:
            raise ValueError(f'Invalid Clutch Time. Must be one of either: {self.__class__.allowed_clutch_times}')
        else:
            self._clutch_time_setting = clutch_setting

    @property
    def month_setting(self) -> int:    
        return self._month_setting
    
    @month_setting.setter
    def month_setting(self, new_month: str) -> NoReturn:
        if new_month in self.__class__.allowed_months:
            self._month_setting = self.__class__.months[new_month]
        else:
            raise ValueError(f'Invalid Month. Must be one of either: {self.__class__.allowed_months}')

    # Date format received from API is string of 'yyyymmdd', convert to string representation of datetime object 'yyyy-mm-dd'
    @staticmethod
    def _get_date_format(date_str: str) -> str:
        return datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')

    # Get team abbreviation of player as it's not received from API, also create matchup str for the game eg 'CHI vs. PHI'/ 'HOU @ MIN'
    def _get_team_and_matchup(self, team: str, h_team: str, v_team: str) -> tuple[str, str]:
        # Retrieve team abbreviation from the mapped dictionary
        player_team_abbrev = self.team_names_map[team]
        # If the player's team is the home team...
        if h_team == player_team_abbrev:
            matchup = f'{h_team} vs. {v_team}'
        # Redundant elif but wanted to be clear about the logic. Could also just use 'else'
        elif v_team == player_team_abbrev:
            matchup = f'{v_team} @ {h_team}'
        return player_team_abbrev, matchup

    # Function to take in player in ShotChartDetail API
    # Returns list of dictionaries, each dictionary is individual player's shot data
    # Could use this function externally if you have player_id and team_id handy, good for debugging
    def player_shots(self, p_id: int, t_id: int) -> list[dict]:
        # API call
        raw = ShotChartDetail(player_id=p_id, team_id=t_id,
                            season_type_all_star=self.season_segment,
                            clutch_time_nullable=self.clutch_time_setting, # Used for testing, default is empty string meaning NO clutch time parameters
                            month=self.month_setting,
                            season_nullable='2024-25',
                            # Ensures made and missed goals are returned
                            context_measure_simple='FGA')

        # Get data in dictionary form
        raw_shots = raw.shot_chart_detail.get_dict()
        # Retrieve headers from the data set
        headers: list[str] = raw_shots['headers']
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
            current_dict['team_abbrev'], current_dict['matchup'] = self._get_team_and_matchup(current_dict['team_name'], current_dict['htm'], current_dict['vtm'])
            # Change game date to formatted style
            current_dict['game_date'] = self._get_date_format(current_dict['game_date'])
            # Add season segment 'Playoffs' or 'Regular Season'
            current_dict['season_segment'] = self.season_segment
            # Remove 'grid_type', 'shot_attempted_flag', unnecessary elements
            current_dict.pop('grid_type', None)
            current_dict.pop('shot_attempted_flag', None)
            # Append the current_dict (r/shot) to the player's total shots in tuple format
            # player_shots.append(tuple(current_dict.values()))
            player_shots.append(current_dict)
        # Return player_shots and use '.extend()' on the team's overall list 'team_shots'
        return player_shots


    # Function to retrieve a single team's players from MySQL reference table 'ref_teams' JOIN 'ref_players'
    # Returns dict with team_id, list of player id's, list of player name
    # Can use this function externally for debugging etc.
    def get_team(self) -> dict[str, Union[int, list]]:
        with DatabaseControl.get_connection() as conn:
            # Dictionary cursor to return table in dictionary format (team_abbrev, player_id, team_id, player_name), for stored procedure 'TeamPlayers' in get_team()
            with conn.cursor(dictionary=True) as c:
                # Call stored procedure to receive all players in the given team
                c.callproc(procname='TeamPlayers', args=[self.team])
                # Empty dict to include team's id, list of each player's id and list of each player's name (debugging)
                team = {}
                # Retrieve stored procedure results and loop over each row (player)
                for result in c.stored_results():
                    players = result.fetchall()
                    for num, player in enumerate(players, start=1):
                        # Retrieve the team's id once only, by any player (Whoever is first)
                        if num == 1:
                            team['team_id'] = player['team_id']
                            # And create the structure for the id's and player names
                            team['player_ids'] = []
                            team['player_names'] = [] # Player id's useful for debugging
                        # Append each player's id and name to respective 'team{}' element
                        team['player_ids'].append(player['player_id'])
                        team['player_names'].append(player['player_name'])
                return team

    # Returns list of dictionaries where values are strings or integers
    # Can use this function externally for debugging etc.
    def team_shots(self) -> list[dict[str | int]]:
        # Call function to retrieve dict of given team
        team_details = self.get_team()
        # Will hold all player shots of team, one dict for each shot
        team_shots = []
        # Loop over the players (id's) of the team
        for pid in tqdm(team_details['player_ids'], desc=f'Loading: {self.team} -> {self.season_segment}'):
            # Contains all shots of a given player
            shots = self.player_shots(p_id=pid, t_id=team_details['team_id'])
            # Add the shots to the current team's shots
            team_shots.extend(shots)
            # Avoid overloading the API
            time.sleep(2)

        return team_shots

    def stage_shots(self) -> NoReturn:
        if self.team is None or self.season_segment is None:
            return f'Invalid values in team:({self.team}) or season_segment({self.season_segment})'
        current_team_shots = self.team_shots()
        # Insert into database
        insert_player_shots_query = """ INSERT INTO stg_shots (game_id, game_event_id, player_id, player_name, team_id, team_name, team_abbrev, period, minutes_remaining, seconds_remaining, 
                                    event_type, action_type, shot_type, shot_zone_basic, shot_zone_area, shot_zone_range, shot_distance, loc_x, loc_y, shot_made_flag, game_date, htm, vtm, matchup, season_segment) 
                                    VALUES (%(game_id)s, %(game_event_id)s, %(player_id)s, %(player_name)s, %(team_id)s, %(team_name)s, %(team_abbrev)s, %(period)s, %(minutes_remaining)s, %(seconds_remaining)s, 
                                    %(event_type)s, %(action_type)s, %(shot_type)s, %(shot_zone_basic)s, %(shot_zone_area)s, %(shot_zone_range)s, %(shot_distance)s, %(loc_x)s, %(loc_y)s, %(shot_made_flag)s, 
                                    %(game_date)s, %(htm)s, %(vtm)s, %(matchup)s, %(season_segment)s)
                                    """
        update_timestamp_query = "UPDATE ref_teams SET last_updated = %s WHERE team_abbrev = %s"
        
        try:
            with DatabaseControl.get_connection() as conn:
                with conn.cursor() as c:
                    try:
                        # No need to manually start transaction. Transaction starts automatically and autocommit = 0 (False) by default. Will cause error: 'Transaction already in progress'
                        print('Inserting player shots...')
                        c.executemany(insert_player_shots_query, current_team_shots)
                        # Get current time to insert into ref_teams.team to show latest update
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        c.execute(update_timestamp_query, (timestamp, self.team))
                        conn.commit()
                    except Exception as e:
                        conn.rollback()
                        print('Transaction Failed: ', e)
        except Exception as e:
            print('Connection Failed: ', e)

    
    # No tuple return value, just printing
    def testing(self) -> tuple:
        with DatabaseControl.get_connection() as conn:
            with conn.cursor() as c:
                c.execute("SELECT * FROM stg_shots")
                players = c.fetchall()
                for player in players:
                    print(player)

# Function to run the StageTeamShotData instance
def stg_data(stack: int) -> NoReturn:
    team_stack = {1: ['ATL', 'BOS', 'BKN'], 2: ['CHA', 'CHI', 'CLE'], 3: ['DAL', 'DEN', 'DET'],
                4: ['GSW', 'HOU', 'IND'], 5: ['LAC', 'LAL', 'MEM'], 6: ['MIA', 'MIL', 'MIN'],
                7: ['NOP', 'NYK', 'OKC'], 8: ['ORL', 'PHI', 'PHX'], 9: ['POR', 'SAC', 'SAS'],
                10: ['TOR', 'UTA', 'WAS']}
    # Create instance for each team
    team_instance = StageTeamShotData()
    # Loop over the list of teams determined by stack argument
    for team in team_stack[stack]:
        # Loop over Regular Season and Playoffs
        for season in StageTeamShotData.allowed_season_segments:
            # Set current team and season for instance
            team_instance.team = team
            team_instance.season_segment = season
            team_instance.clutch_time_setting = ''
            team_instance.month_setting = 'all months'
            team_instance.stage_shots()
            # Perform a check to see if we are at the end of the player/season iteration, if so, execute testing query.
            # if team_stack[stack].index(team) == 2 and StageTeamShotData.allowed_season_segments.index(season) == 1:
            #     team_instance.testing()

# Run the class for just one team/season segment
def stg_one(team_name: str, season: str) -> NoReturn:
    StageTeamShotData(team=team_name, season_segment=season).stage_shots()



# Retrieve updates for each team, when each team was last updated
# Ordered by last_updated ASC (earliest update first)
def get_updates():
    with DatabaseControl.get_connection() as conn:
        with conn.cursor() as c:
            c.execute("""SELECT team_abbrev, last_updated 
                         FROM ref_teams
                         ORDER BY last_updated""")
            team_updates = c.fetchall()
            for team in team_updates:
                print(team)
