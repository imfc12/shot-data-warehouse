import mysql.connector as connector
from dotenv import load_dotenv
import os

# Load environment for mysql password
load_dotenv()

class Month:
    months = {
        'October': 1,
        'November': 2,
        'December': 3,
        'January': 4,
        'February': 5,
        'March': 6,
        'April': 7,
        'May': 8,
        'June': 9,
        'all months': 0
    }

class ClutchTime:
    last_5_minutes = "Last 5 Minutes"
    last_4_minutes = "Last 4 Minutes"
    last_3_minutes = "Last 3 Minutes"
    last_2_minutes = "Last 2 Minutes"
    last_1_minute = "Last 1 Minute"
    last_30_seconds = "Last 30 Seconds"
    last_10_seconds = "Last 10 Seconds"
    none_clutch = ""

class DatabaseControl:
    print('Starting up database')
    pw = os.getenv('mysql_pw')
    # Connect to db
    connection = connector.connect(host='localhost', user='root',
                                   password=pw, port=3306, database='shot_eff_whse')
    # Create cursor and start the database, close the cursor immediately as a new one will be created
    cursor = connection.cursor()
    # Set default database
    cursor.execute('USE shot_eff_whse')
    # Dictionary cursor to return table in dictionary format (team_abbrev, player_id, team_id, player_name), for stored procedure 'TeamPlayers' in get_team()
    cursor_dict = connection.cursor(dictionary=True)

    # Option to set new database name
    @classmethod
    def set_database(cls, db_name):
        cls.cursor.execute('USE %s', db_name)
