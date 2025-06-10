-- BACKUP

SHOW DATABASES;

USE shot_eff_whse;

SHOW TABLES;

SELECT COUNT(*) FROM stg_shots;

SELECT COUNT(DISTINCT game_id) FROM stg_shots;

SELECT COUNT(DISTINCT matchup, game_id) FROM dim_game;
SELECT * FROM dim_game WHERE game_id = 22400016;

SELECT COUNT(DISTINCT(CONCAT(stg_shots.game_id, stg_shots.game_event_id))) FROM stg_shots;

-- Stored procedure used to retrieve all players from a given team
DESCRIBE ref_teams;
SET SQL_SAFE_UPDATES = 0;
DELIMITER //
CREATE PROCEDURE TeamPlayers(IN team_abbr CHAR(3))
BEGIN
	SELECT t.team_abbrev, p.player_id, p.team_id, p.player_name
	FROM ref_teams AS t
	JOIN ref_players AS p ON t.team_id = p.team_id
	WHERE t.team_abbrev = team_abbr
    ORDER BY p.player_name;
END //
DELIMITER ;

CALL TeamPlayers('ATL');



-- TRANSACTION TO TEST INSERTING INTO STAR SCHEMA
START TRANSACTION;
-- ******* Add teams ******* --
INSERT INTO dim_teams (team_id, team_name, team_abbrev)
SELECT DISTINCT team_id, team_name, team_abbrev
FROM stg_shots
WHERE team_id NOT IN (SELECT team_id FROM dim_teams);

SELECT COUNT(*) FROM dim_teams;
-- ******* --

-- ******* Add players ******* --
INSERT INTO dim_players (player_id, player_name, team_id)
SELECT DISTINCT player_id, player_name, team_id
FROM stg_shots
WHERE player_id NOT IN (SELECT player_id FROM dim_players);

SELECT COUNT(*) FROM dim_players;
-- *******

-- ******* Add game ******* --
INSERT INTO dim_game (matchup, game_id)
SELECT DISTINCT matchup, game_id
FROM stg_shots
WHERE CONCAT(matchup, game_id) NOT IN
(SELECT CONCAT(matchup, game_id) FROM dim_game);

SELECT COUNT(*) FROM dim_game;
-- *******

-- ******* Add shots ******* --
INSERT INTO dim_shots (action_type, shot_type, shot_zone_basic, shot_zone_area, shot_zone_range, event_type, game_event_id, game_id)
SELECT action_type, shot_type, shot_zone_basic, shot_zone_area, shot_zone_range, event_type, game_event_id, game_id
FROM stg_shots
WHERE CONCAT(game_id, game_event_id) NOT IN
(SELECT CONCAT(game_id, game_event_id) FROM dim_game);

SELECT COUNT(*) FROM dim_shots;
-- ******* --

-- ******* Add time ******* --
INSERT INTO dim_time (season_segment, game_event_id, game_id, game_date, period, minutes_remaining, seconds_remaining)
SELECT season_segment, game_event_id, game_id, game_date, period, minutes_remaining, seconds_remaining
FROM stg_shots
WHERE CONCAT(game_id, game_event_id) NOT IN
(SELECT CONCAT(game_id, game_event_id) FROM dim_time);

SELECT COUNT(*) FROM dim_time;
-- ******* --

-- ******* Add into fact_shots ******* --
INSERT INTO fact_shots (time_key, shot_key, game_key, team_key, player_key, is_bucket, shot_distance, loc_x, loc_y)
SELECT t.time_key, s.shot_key, g.game_key, tm.team_key, p.player_key,
	   st.shot_made_flag, st.shot_distance, st.loc_x, st.loc_y
FROM stg_shots AS st
JOIN dim_players AS p ON st.player_id = p.player_id
JOIN dim_teams AS tm ON st.team_id = tm.team_id
JOIN dim_game AS g ON st.game_id = g.game_id
JOIN dim_shots AS s ON st.game_id = s.game_id AND st.game_event_id = s.game_event_id
JOIN dim_time AS t ON st.game_id = t.game_id AND st.game_event_id = t.game_event_id;

SELECT COUNT(*) FROM fact_shots;
SELECT * FROM fact_shots;
-- ******* --

ROLLBACK;

SELECT t.time_key, s.shot_key, g.game_key, tm.team_key, p.player_key, g.matchup, g.game_id, t.game_date,
	   st.shot_made_flag, st.shot_distance, st.loc_x, st.loc_y
FROM stg_shots AS st
JOIN dim_players AS p ON st.player_id = p.player_id
JOIN dim_teams AS tm ON st.team_id = tm.team_id
JOIN dim_game AS g ON st.game_id = g.game_id
JOIN dim_shots AS s ON st.game_id = s.game_id AND st.game_event_id = s.game_event_id
JOIN dim_time AS t ON st.game_id = t.game_id AND st.game_event_id = t.game_event_id
WHERE t.time_key = 262141 AND s.shot_key = 786421;

SELECT t.time_key, s.shot_key, COUNT(*) as cnt
FROM stg_shots AS st
JOIN dim_players AS p ON st.player_id = p.player_id
JOIN dim_teams AS tm ON st.team_id = tm.team_id
JOIN dim_game AS g ON st.game_id = g.game_id
JOIN dim_shots AS s ON st.game_id = s.game_id AND st.game_event_id = s.game_event_id
JOIN dim_time AS t ON st.game_id = t.game_id AND st.game_event_id = t.game_event_id
GROUP BY t.time_key, s.shot_key
HAVING cnt > 1;

SHOW VARIABLES LIKE '%timeout';
SET GLOBAL connect_timeout = 30;














-- OTHER
SELECT DISTINCT matchup, game_id, game_date
FROM stg_shots 
WHERE matchup = 'BOS vs. NYK'
OR matchup = 'NYK vs. BOS'
OR matchup = 'NYK @ BOS'
OR matchup = 'BOS @ NYK'
ORDER BY game_date, game_id;


SELECT COUNT(DISTINCT matchup, game_id, game_date)
FROM stg_shots;


