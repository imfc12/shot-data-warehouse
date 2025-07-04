# NBA Shot Data Warehouse
A Python-MySQL pipeline that transforms and loads shot data of all players in a given NBA season from nba_api into a data warehouse, including an OLAP-ready star schema.

## Star Schema Tables 
##### DIMENSIONS
- dim_players
- dim_teams
- dim_games
- dim_shots
- dim_time
##### FACT
- fact_shots
(DB Also includes reference tables and staging table)

### Some of the stats captured (Not all)
- player name, team name, matchup, season segment, game date, game period, minutes remaining, seconds remaining, shot action type, shot type, shot zone area, shot zone range, shot missed or made, event type and more!

# Project Structure (Tree at the bottom)
## MySQL DB Design -> 'Data Models' Directory
1. `Logical Schema.png` 
    - Shows logical-level model of database structure
2. `shot-eff-model.mwb` 
    - Blueprint of database schema and used to forward engineer physical database

## MySQL DDL, DML -> 'SQL' Directory
1. `star_schema.sql`
    - Forward engineered DDL from database model, to create the star schema
2. `staging_table.sql`
    - Forward engineered DDL to create the staging table
3. `reference_tables.sql`
    - Forward engineered DDL to create the reference tables. 
    - This table is used to call nba_api with appropriate team-player pairings
4. `retrieve_team_proc.sql`
    - DML, Creates a stored procedure to retrieve all players from a given team from the reference tables
5. `load_procedures.sql`
    - DML, Stored procedures used to take data from staging to star schema tables

## Python ETL Process -> 'ETL' Directory
1. `reference_data.py`
    - Used to retrieve latest team & player data and load into/update reference tables 'ref_teams' and 'ref_players'
2. `staging_utils.py`
    - Utilities to assist running of 'staging_data.py':
        * Month mapping (month name: number)
        * Clutch time string mapping
        * Database control which handles database connection and db name change
3. `staging_data.py`
    - Used to extract shot data for every team/player and insert into staging table 'stg_shots'
4. `orchestrate_load.py`
    - Orchestrates the load procedures created in 'load_procedures.sql' to transfer data from staging to star schema and truncate staging after operations are finished

## Run all - 'main.py'
1. `reference_data.ref_data(first_insert=False)`
    - Loads data into ref_teams and ref_players
2. `staging_data.stg_data(8)`
    - Extract transform and load data into staging table.
    - Call one team stack at a time, 3 teams in one stack (runs for regular season and playoffs)
    OR
2. `staging_data.stg_one('MIL', 'Regular Season')`
    - Call one team/season segment at a time
3. `rows = LoadOrchestrator().run_all()` -> `print(rows)`
    - Loads data from staging to star schema. 
    - Print output shows current team, load bar, rows loaded into each table

## Docs
- `journal.txt` Where i kept track of updates to the code and changes to be made while working on the project. Also holds ideal future improvements to the project at the bottom
- `column_mapping.md` Used to map and staging table columns to star schema columns for clear understanding of design

##### NOTES:
* Add DB password in .env file
* Performing full load of all players in whole season may take up to 30 minutes ~ 200k+ rows

##### Quick Start
git clone https://github.com/imfc12/shot-data-warehouse.git
cd shot-data-warehouse
pip install -r requirements.txt      # nba_api, mysql-connector-python, python-dotenv …

#### Project Tree

```
shot-data-warehouse/
├── .gitignore
├── environment.yml
├── requirements.txt
├── main.py
├── README.md
├── Data Models/
│   ├── logical_Schema.png
│   ├── schema.drawio
│   └── shot-eff-model.mwb
├── Docs/
│   ├── column_mapping.md
│   └── journal.txt
├── ETL/
│   ├── orchestrate_load.py
│   ├── reference_data.py
│   ├── staging_data.py
│   └── staging_utils.py
└── SQL/
    ├── load_procedures.sql
    ├── reference_tables.sql
    ├── retrieve_team_proc.sql
    ├── staging_table.sql
    └── star_schema.sql
```