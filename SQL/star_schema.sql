-- DROP TABLE IF EXISTS dim_players;
-- DROP TABLE IF EXISTS dim_teams;

-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema shot_eff_whse
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema shot_eff_whse
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `shot_eff_whse` DEFAULT CHARACTER SET utf8 ;
USE `shot_eff_whse` ;

-- -----------------------------------------------------
-- Table `shot_eff_whse`.`dim_games`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `shot_eff_whse`.`dim_games` (
  `game_key` INT NOT NULL AUTO_INCREMENT,
  `game_id` INT NULL,
  `matchup` VARCHAR(15) NULL,
  `htm` CHAR(3) NULL,
  `vtm` CHAR(3) NULL,
  PRIMARY KEY (`game_key`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `shot_eff_whse`.`dim_teams`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `shot_eff_whse`.`dim_teams` (
  `team_key` INT NOT NULL AUTO_INCREMENT,
  `team_id` INT NOT NULL,
  `team_name` VARCHAR(30) NULL,
  `team_abbrev` CHAR(3) NULL,
  PRIMARY KEY (`team_key`),
  UNIQUE INDEX `team_id_UNIQUE` (`team_id` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `shot_eff_whse`.`dim_players`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `shot_eff_whse`.`dim_players` (
  `player_key` INT NOT NULL AUTO_INCREMENT,
  `player_id` INT NULL,
  `player_name` VARCHAR(45) NULL,
  `team_id` INT NULL,
  PRIMARY KEY (`player_key`),
  INDEX `team_id_fk_idx` (`team_id` ASC) VISIBLE,
  CONSTRAINT `team_id_fk`
    FOREIGN KEY (`team_id`)
    REFERENCES `shot_eff_whse`.`dim_teams` (`team_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `shot_eff_whse`.`dim_time`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `shot_eff_whse`.`dim_time` (
  `time_key` INT NOT NULL AUTO_INCREMENT,
  `time_id` VARCHAR(25) NULL,
  `season_segment` ENUM("Playoffs", "Regular Season") NULL,
  `game_event_id` INT NULL,
  `game_id` INT NULL,
  `game_date` DATE NULL,
  `period` TINYINT NULL,
  `minutes_remaining` TINYINT NULL,
  `seconds_remaining` TINYINT NULL,
  PRIMARY KEY (`time_key`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `shot_eff_whse`.`dim_shots`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `shot_eff_whse`.`dim_shots` (
  `shot_key` INT NOT NULL AUTO_INCREMENT,
  `shot_id` VARCHAR(25) NULL,
  `action_type` VARCHAR(45) NULL,
  `shot_type` VARCHAR(45) NULL,
  `shot_zone_basic` VARCHAR(45) NULL,
  `shot_zone_area` VARCHAR(45) NULL,
  `shot_zone_range` VARCHAR(45) NULL,
  `event_type` VARCHAR(45) NULL,
  `game_event_id` INT NULL,
  `game_id` INT NULL,
  PRIMARY KEY (`shot_key`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `shot_eff_whse`.`fact_shots`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `shot_eff_whse`.`fact_shots` (
  `time_key` INT NOT NULL,
  `shot_key` INT NOT NULL,
  `game_key` INT NULL,
  `team_key` INT NULL,
  `player_key` INT NULL,
  `is_bucket` TINYINT NULL,
  `shot_distance` TINYINT NULL,
  `loc_x` SMALLINT NULL,
  `loc_y` SMALLINT NULL,
  PRIMARY KEY (`time_key`, `shot_key`),
  INDEX `game_key_fk_idx` USING BTREE (`game_key`) VISIBLE,
  INDEX `team_key_fk_idx` USING BTREE (`team_key`) VISIBLE,
  INDEX `player_key_fk_idx` USING BTREE (`player_key`) VISIBLE,
  INDEX `shot_key_fk_idx` USING BTREE (`shot_key`) VISIBLE,
  INDEX `time_key_fk_idx` USING BTREE (`time_key`) VISIBLE,
  CONSTRAINT `game_key_fk`
    FOREIGN KEY (`game_key`)
    REFERENCES `shot_eff_whse`.`dim_games` (`game_key`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `team_key_fk`
    FOREIGN KEY (`team_key`)
    REFERENCES `shot_eff_whse`.`dim_teams` (`team_key`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `player_key_fk`
    FOREIGN KEY (`player_key`)
    REFERENCES `shot_eff_whse`.`dim_players` (`player_key`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `time_key_fk`
    FOREIGN KEY (`time_key`)
    REFERENCES `shot_eff_whse`.`dim_time` (`time_key`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `shot_key_fk`
    FOREIGN KEY (`shot_key`)
    REFERENCES `shot_eff_whse`.`dim_shots` (`shot_key`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;
