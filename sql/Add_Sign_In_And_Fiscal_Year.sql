-- =====================================================
-- Migration Script: Add Sign-In Table and Fiscal Year Tracking
-- =====================================================
-- This script adds:
-- 1. A new 'sign_ins' table for tracking Makerspace visitors
-- 2. A 'fiscal_year' column to the print_jobs table
--
-- Run this script on your existing makerspace_db_final database
-- =====================================================

USE `makerspace_db_final`;

-- =====================================================
-- 1. Add fiscal_year column to print_jobs table
-- =====================================================
ALTER TABLE `print_jobs`
ADD COLUMN `fiscal_year` INT NULL DEFAULT NULL AFTER `upload_path`;

-- =====================================================
-- 2. Create sign_ins table for visitor tracking
-- =====================================================
CREATE TABLE IF NOT EXISTS `sign_ins` (
  `sign_in_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(200) NOT NULL,
  `email` VARCHAR(200) NOT NULL,
  `sign_in_time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `fiscal_year` INT NULL DEFAULT NULL,
  `fiscal_quarter` INT NULL DEFAULT NULL,
  PRIMARY KEY (`sign_in_id`),
  INDEX `idx_sign_in_time` (`sign_in_time` ASC),
  INDEX `idx_fiscal_year` (`fiscal_year` ASC),
  INDEX `idx_email` (`email` ASC)
) ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci
COMMENT = 'Tracks visitor sign-ins to the Makerspace for involvement reporting';

-- =====================================================
-- Optional: Update existing print_jobs with calculated fiscal year
-- (Fiscal year is July 1 - June 30, labeled by end year)
-- =====================================================
UPDATE `print_jobs`
SET `fiscal_year` = CASE
    WHEN MONTH(created_at) >= 7 THEN YEAR(created_at) + 1
    ELSE YEAR(created_at)
END
WHERE `fiscal_year` IS NULL;

-- =====================================================
-- Verification queries (optional - comment out if not needed)
-- =====================================================
-- SELECT * FROM sign_ins LIMIT 10;
-- SELECT job_id, job_name, created_at, fiscal_year FROM print_jobs LIMIT 10;
