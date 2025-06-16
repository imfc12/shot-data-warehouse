# Column Mapping Staging Table to Star Schema

## Overview
This document maps staging table fields to star schema tables.

## Tables mapped
- fact_shots
- dim_game
- dim_shots
- dim_time
- dim_players
- dim_teams


#### Mapping 
###### stg_shots -> dim_shots
* STAGING col -> STAR SCHEMA col
(Generated) AUTO_INCREMENT -> shot_key
action_type -> action_type
shot_type -> shot_type
shot_zone_basic -> shot_zone_basic
shot_zone_area -> shot_zone_area
shot_zone_range -> shot_zone_range
event_type -> event_type
game_event_id -> game_event_id
game_id -> game_id

###### stg_shots -> dim_time
* STAGING col -> STAR SCHEMA col
(Generated) AUTO_INCREMENT -> time_key
season_segment -> season_segment
game_event_id -> game_event_id
game_id -> game_id
game_date -> game_date
period -> period
min_left -> min_left
sec_left -> sec_left

###### stg_shots -> dim_players
* STAGING col -> STAR SCHEMA col
(Generated) AUTO_INCREMENT -> player_key
player_id -> player_id
player_name -> player_name
team_id -> team_id

###### stg_shots -> dim_teams
* STAGING col -> STAR SCHEMA col
(Generated) AUTO_INCREMENT -> team_key
team_id -> team_id
team_name -> team_name
team_abbrev -> team_abbrev

###### stg_shots -> dim_game
* STAGING col -> STAR SCHEMA col
(Generated) AUTO_INCREMENT -> game_key
matchup -> matchup
game_id -> game_id
htm -> htm
vtm -> vtm


###### stg_shots -> fact_shots
* STAGING col -> STAR SCHEMA col
FK lookup from dim_time -> time_key
FK lookup from dim_shots -> shot_key
FK lookup from dim_game -> game_key
FK lookup from dim_teams -> team_key
FK lookup from dim_players -> player_key
shot_made_flag -> is_bucket
loc_x -> loc_x
loc_y -> loc_y
