-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema makerspace_db_final
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema makerspace_db_final
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `makerspace_db_final` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `makerspace_db_final` ;

-- -----------------------------------------------------
-- Table `makerspace_db_final`.`patrons`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `makerspace_db_final`.`patrons` (
  `patron_id` INT NOT NULL AUTO_INCREMENT,
  `netid` VARCHAR(64) NOT NULL,
  `name` VARCHAR(200) NOT NULL,
  `email` VARCHAR(200) NOT NULL,
  `phone` VARCHAR(30) NULL DEFAULT NULL,
  `affiliation` VARCHAR(100) NULL DEFAULT NULL,
  `status` ENUM('student', 'faculty', 'staff', 'alumni', 'visitor', 'other') NULL DEFAULT 'student',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`patron_id`),
  UNIQUE INDEX `uq_netid` (`netid` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 7
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `makerspace_db_final`.`staff`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `makerspace_db_final`.`staff` (
  `staff_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(200) NOT NULL,
  `email` VARCHAR(200) NULL DEFAULT NULL,
  `role` VARCHAR(100) NULL DEFAULT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`staff_id`))
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `makerspace_db_final`.`print_jobs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `makerspace_db_final`.`print_jobs` (
  `job_id` INT NOT NULL AUTO_INCREMENT,
  `job_number` INT NULL DEFAULT NULL,
  `patron_id` INT NULL DEFAULT NULL,
  `staff_id` INT NULL DEFAULT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `start_datetime` DATETIME NULL DEFAULT NULL,
  `finish_datetime` DATETIME NULL DEFAULT NULL,
  `job_name` VARCHAR(255) NULL DEFAULT NULL,
  `num_items` INT NULL DEFAULT NULL,
  `filament_desc` VARCHAR(200) NULL DEFAULT NULL,
  `filament_color` VARCHAR(50) NULL DEFAULT NULL,
  `est_filament_g` DECIMAL(10,3) NULL DEFAULT NULL,
  `support_material_type` VARCHAR(100) NULL DEFAULT NULL,
  `est_support_g` DECIMAL(10,3) NULL DEFAULT NULL,
  `resin_color` VARCHAR(50) NULL DEFAULT NULL,
  `est_resin_ml` DECIMAL(10,3) NULL DEFAULT NULL,
  `est_time` TIME NULL DEFAULT NULL,
  `actual_time` TIME NULL DEFAULT NULL,
  `weight_g` DECIMAL(10,3) NULL DEFAULT NULL,
  `amount_charged` DECIMAL(10,2) NULL DEFAULT NULL,
  `fund_org_id` VARCHAR(100) NULL DEFAULT NULL,
  `notes` TEXT NULL DEFAULT NULL,
  `is_class_assign` TINYINT(1) NULL DEFAULT '0',
  `dimensions_mm` VARCHAR(100) NULL DEFAULT NULL,
  `upload_path` VARCHAR(500) NULL DEFAULT NULL,
  `special_instructions` TEXT NULL DEFAULT NULL,
  `patron_paid_materials` TINYINT(1) NULL DEFAULT '0',
  `support_needed` TINYINT(1) NULL DEFAULT '0',
  `fiscal_year` INT NULL DEFAULT NULL,
  PRIMARY KEY (`job_id`),
  UNIQUE INDEX `job_number` (`job_number` ASC) VISIBLE,
  INDEX `fk_printjobs_patrons` (`patron_id` ASC) VISIBLE,
  INDEX `fk_printjobs_staff` (`staff_id` ASC) VISIBLE,
  CONSTRAINT `fk_print_jobs_patron`
    FOREIGN KEY (`patron_id`)
    REFERENCES `makerspace_db_final`.`patrons` (`patron_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `fk_print_jobs_staff`
    FOREIGN KEY (`staff_id`)
    REFERENCES `makerspace_db_final`.`staff` (`staff_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `fk_printjobs_patrons`
    FOREIGN KEY (`patron_id`)
    REFERENCES `makerspace_db_final`.`patrons` (`patron_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `fk_printjobs_staff`
    FOREIGN KEY (`staff_id`)
    REFERENCES `makerspace_db_final`.`staff` (`staff_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `makerspace_db_final`.`job_charges`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `makerspace_db_final`.`job_charges` (
  `charge_id` INT NOT NULL AUTO_INCREMENT,
  `job_id` INT NOT NULL,
  `amount` DECIMAL(10,2) NOT NULL,
  `charged_to` VARCHAR(200) NULL DEFAULT NULL,
  `charged_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `notes` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`charge_id`),
  INDEX `fk_jobcharges_jobs` (`job_id` ASC) VISIBLE,
  CONSTRAINT `fk_job_charges_job`
    FOREIGN KEY (`job_id`)
    REFERENCES `makerspace_db_final`.`print_jobs` (`job_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_jobcharges_jobs`
    FOREIGN KEY (`job_id`)
    REFERENCES `makerspace_db_final`.`print_jobs` (`job_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `makerspace_db_final`.`machines`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `makerspace_db_final`.`machines` (
  `machine_id` INT NOT NULL AUTO_INCREMENT,
  `code_name` VARCHAR(100) NOT NULL,
  `display_name` VARCHAR(200) NOT NULL,
  `machine_type` VARCHAR(100) NULL DEFAULT NULL,
  `notes` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`machine_id`),
  UNIQUE INDEX `uq_code` (`code_name` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 7
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `makerspace_db_final`.`job_machines`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `makerspace_db_final`.`job_machines` (
  `job_machine_id` INT NOT NULL AUTO_INCREMENT,
  `job_id` INT NOT NULL,
  `machine_id` INT NOT NULL,
  `role` VARCHAR(100) NULL DEFAULT NULL,
  `notes` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`job_machine_id`),
  UNIQUE INDEX `uq_job_machine` (`job_id` ASC, `machine_id` ASC) VISIBLE,
  INDEX `fk_jobmachines_machines` (`machine_id` ASC) VISIBLE,
  CONSTRAINT `fk_job_machines_job`
    FOREIGN KEY (`job_id`)
    REFERENCES `makerspace_db_final`.`print_jobs` (`job_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_job_machines_machine`
    FOREIGN KEY (`machine_id`)
    REFERENCES `makerspace_db_final`.`machines` (`machine_id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_jobmachines_jobs`
    FOREIGN KEY (`job_id`)
    REFERENCES `makerspace_db_final`.`print_jobs` (`job_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_jobmachines_machines`
    FOREIGN KEY (`machine_id`)
    REFERENCES `makerspace_db_final`.`machines` (`machine_id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 7
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `makerspace_db_final`.`materials`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `makerspace_db_final`.`materials` (
  `material_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(150) NOT NULL,
  `material_type` ENUM('filament', 'resin', 'support', 'other') NOT NULL,
  `color` VARCHAR(50) NULL DEFAULT NULL,
  `unit` VARCHAR(20) NULL DEFAULT 'g',
  `unit_cost` DECIMAL(8,4) NULL DEFAULT NULL,
  PRIMARY KEY (`material_id`))
ENGINE = InnoDB
AUTO_INCREMENT = 16
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `makerspace_db_final`.`job_materials`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `makerspace_db_final`.`job_materials` (
  `job_material_id` INT NOT NULL AUTO_INCREMENT,
  `job_id` INT NOT NULL,
  `material_id` INT NOT NULL,
  `qty` DECIMAL(12,4) NULL DEFAULT NULL,
  `unit` VARCHAR(20) NULL DEFAULT NULL,
  `notes` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`job_material_id`),
  UNIQUE INDEX `uq_job_material` (`job_id` ASC, `material_id` ASC) VISIBLE,
  INDEX `fk_jobmaterials_materials` (`material_id` ASC) VISIBLE,
  CONSTRAINT `fk_job_materials_job`
    FOREIGN KEY (`job_id`)
    REFERENCES `makerspace_db_final`.`print_jobs` (`job_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_job_materials_material`
    FOREIGN KEY (`material_id`)
    REFERENCES `makerspace_db_final`.`materials` (`material_id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_jobmaterials_jobs`
    FOREIGN KEY (`job_id`)
    REFERENCES `makerspace_db_final`.`print_jobs` (`job_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_jobmaterials_materials`
    FOREIGN KEY (`material_id`)
    REFERENCES `makerspace_db_final`.`materials` (`material_id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `makerspace_db_final`.`sign_ins`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `makerspace_db_final`.`sign_ins` (
  `sign_in_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(200) NOT NULL,
  `email` VARCHAR(200) NOT NULL,
  `sign_in_time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `fiscal_year` INT NULL DEFAULT NULL,
  `fiscal_quarter` INT NULL DEFAULT NULL,
  PRIMARY KEY (`sign_in_id`),
  INDEX `idx_sign_in_time` (`sign_in_time` ASC) VISIBLE,
  INDEX `idx_fiscal_year` (`fiscal_year` ASC) VISIBLE,
  INDEX `idx_email` (`email` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci
COMMENT = 'Tracks visitor sign-ins to the Makerspace for involvement reporting';


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
