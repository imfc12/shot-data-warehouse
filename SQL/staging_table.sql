-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema shot_eff_whse
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Table `shot_eff_whse`.`stg_shots`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `shot_eff_whse`.`stg_shots` (
  `game_id` VARCHAR(12) NULL,
  `game_event_id` INT NULL,
  `player_id` INT NULL,
  `player_name` VARCHAR(45) NULL,
  `team_id` INT NULL,
  `team_name` VARCHAR(45) NULL,
  `team_abbrev` CHAR(3) NULL,
  `period` TINYINT NULL,
  `minutes_remaining` TINYINT NULL,
  `seconds_remaining` TINYINT NULL,
  `event_type` VARCHAR(45) NULL,
  `action_type` VARCHAR(45) NULL,
  `shot_type` VARCHAR(45) NULL,
  `shot_zone_basic` VARCHAR(45) NULL,
  `shot_zone_area` VARCHAR(45) NULL,
  `shot_zone_range` VARCHAR(45) NULL,
  `shot_distance` TINYINT NULL,
  `loc_x` INT NULL,
  `loc_y` INT NULL,
  `shot_made_flag` TINYINT NULL,
  `game_date` DATE NULL,
  `htm` CHAR(3) NULL,
  `vtm` CHAR(3) NULL,
  `matchup` VARCHAR(45) NULL,
  `season_segment` VARCHAR(20) NULL,
  `shot_id` VARCHAR(25) NULL,
  `time_id` VARCHAR(25) NULL)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

