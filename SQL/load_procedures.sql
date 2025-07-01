USE shot_eff_whse;

-- Stored Procedures that take data from staging into star schema

-- Add teams froms staging to dim_teams
DROP PROCEDURE IF EXISTS DimTeams;
DELIMITER //
CREATE PROCEDURE DimTeams(OUT rows_inserted INT)
BEGIN
    INSERT INTO dim_teams (team_id, team_name, team_abbrev)
    SELECT DISTINCT team_id, team_name, team_abbrev
    FROM stg_shots
    WHERE team_id NOT IN (SELECT team_id FROM dim_teams);
    SET rows_inserted = ROW_COUNT();
END //
DELIMITER ;

-- Add players from staging to dim_players
DROP PROCEDURE IF EXISTS DimPlayers;
DELIMITER //
CREATE PROCEDURE DimPlayers(OUT rows_inserted INT)
BEGIN
    INSERT INTO dim_players (player_id, player_name, team_id)
    SELECT DISTINCT player_id, player_name, team_id
    FROM stg_shots
    WHERE player_id NOT IN (SELECT player_id FROM dim_players);
    SET rows_inserted = ROW_COUNT();
END //
DELIMITER ;


-- Update players from staging to dim_players
DROP PROCEDURE IF EXISTS UpdateDimPlayers;
DELIMITER //
CREATE PROCEDURE UpdDimPlayers(OUT rows_inserted INT)
BEGIN
    UPDATE dim_players AS p
    JOIN (
        SELECT DISTINCT player_id, team_id
        FROM stg_shots
      ) AS st
        ON p.player_id = st.player_id
    SET p.team_id = st.team_id
    WHERE p.team_id <> st.team_id;
    SET rows_inserted = ROW_COUNT();
END //
DELIMITER ;


-- Add games from staging to dim_games
DROP PROCEDURE IF EXISTS DimGames;
DELIMITER //
CREATE PROCEDURE DimGames(OUT rows_inserted INT)
BEGIN
    INSERT INTO dim_games (matchup, game_id, htm, vtm)
    SELECT DISTINCT matchup, game_id, htm, vtm
    FROM stg_shots
    WHERE game_id NOT IN
    (SELECT game_id FROM dim_games);
    SET rows_inserted = ROW_COUNT();
END //
DELIMITER ;


-- Add shots from staging to dim_shots
DROP PROCEDURE IF EXISTS DimShots;
DELIMITER //
CREATE PROCEDURE DimShots(OUT rows_inserted INT)
BEGIN
    INSERT INTO dim_shots (shot_id, action_type, shot_type, shot_zone_basic, shot_zone_area, shot_zone_range, event_type, game_event_id, game_id)
    SELECT DISTINCT shot_id, action_type, shot_type, shot_zone_basic, shot_zone_area, shot_zone_range, event_type, game_event_id, game_id
    FROM stg_shots
    WHERE shot_id NOT IN
    (SELECT shot_id FROM dim_shots);
    SET rows_inserted = ROW_COUNT();
END //
DELIMITER ;


-- Add time from staging to dim_time
DROP PROCEDURE IF EXISTS DimTime;
DELIMITER //
CREATE PROCEDURE DimTime(OUT rows_inserted INT)
BEGIN
    INSERT INTO dim_time (time_id, season_segment, game_event_id, game_id, game_date, period, minutes_remaining, seconds_remaining)
    SELECT time_id, season_segment, game_event_id, game_id, game_date, period, minutes_remaining, seconds_remaining
    FROM stg_shots
    WHERE time_id NOT IN
    (SELECT time_id FROM dim_time);
    SET rows_inserted = ROW_COUNT();
END //
DELIMITER ;




-- Add into fact_shots from dimension tables and staging
DROP PROCEDURE IF EXISTS FactShots;
DELIMITER //
CREATE PROCEDURE FactShots(OUT rows_inserted INT)
BEGIN
    INSERT INTO fact_shots (time_key, shot_key, game_key, team_key, player_key, is_bucket, shot_distance, loc_x, loc_y)
    SELECT DISTINCT t.time_key, s.shot_key, g.game_key, tm.team_key, p.player_key,
                    st.shot_made_flag, st.shot_distance, st.loc_x, st.loc_y
    FROM stg_shots AS st
    JOIN dim_players AS p ON st.player_id = p.player_id
    JOIN dim_teams AS tm ON st.team_id = tm.team_id
    JOIN dim_games AS g ON st.game_id = g.game_id AND st.matchup = g.matchup -- NEEDED TO JOIN ON BOTH!
    JOIN dim_shots AS s ON st.shot_id = s.shot_id
    JOIN dim_time AS t ON st.time_id = t.time_id
    WHERE s.shot_key NOT IN 
    (SELECT shot_key FROM fact_shots);
    SET rows_inserted = ROW_COUNT();
END //
DELIMITER ;


-- Delete all rows from staging (rollback-friendly)
DROP PROCEDURE IF EXISTS DeleteStaging;
DELIMITER //
CREATE PROCEDURE DeleteStaging(OUT rows_removed INT)
BEGIN
    DELETE FROM stg_shots;
    SET rows_removed = ROW_COUNT();
END //
DELIMITER ;
