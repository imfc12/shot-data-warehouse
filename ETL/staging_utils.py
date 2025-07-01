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

"""This now contains a class method that returns the database connection.
It is a class method because i want to hold 'db_name' inside which can be changed
with another class method 'change_database'.
"""
class DatabaseControl:
    db_name = 'shot_eff_whse'
    @classmethod
    def get_connection(cls):
        pw = os.getenv('mysql_pw')
        connection = connector.connect(host='localhost', user='root',
                                       password=pw, port=3306, 
                                       database=cls.db_name,
                                       autocommit=False)
        return connection

    @classmethod
    def change_database(cls, new_db_name: str):
            if isinstance(new_db_name, str):
                cls.db_name = new_db_name
            else:
                raise ValueError(f'Invalid database name')
