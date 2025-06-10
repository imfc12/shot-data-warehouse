-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema shot_eff_whse
-- -----------------------------------------------------


-- -----------------------------------------------------
-- Table `shot_eff_whse`.`ref_teams`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `shot_eff_whse`.`ref_teams` (
  `team_id` INT NOT NULL,
  `team_abbrev` CHAR(3) NULL,
  `team_name` VARCHAR(45) NULL,
  `last_updated` DATETIME NULL,
  PRIMARY KEY (`team_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `shot_eff_whse`.`ref_players`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `shot_eff_whse`.`ref_players` (
  `player_id` INT NOT NULL,
  `player_name` VARCHAR(45) NULL,
  `team_id` INT NULL,
  PRIMARY KEY (`player_id`),
  INDEX `team_id_fk_idx` (`team_id` ASC) VISIBLE,
  CONSTRAINT `ref_team_id_fk`
    FOREIGN KEY (`team_id`)
    REFERENCES `shot_eff_whse`.`ref_teams` (`team_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
