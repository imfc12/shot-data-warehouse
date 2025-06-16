-- Stored procedure to retrieve all players from a given team
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

/* Example Call
CALL TeamPlayers('PHI');
*/
