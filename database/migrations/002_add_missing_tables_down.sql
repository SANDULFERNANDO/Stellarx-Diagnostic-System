-- =====================================================================
-- Migration: 002_add_missing_tables_down.sql
-- Branch:    feature/database-setup
-- Purpose:   Rollback for 002_add_missing_tables.sql
--            Reverses changes in strict opposite order of the "up"
--            migration so it can be re-applied cleanly if needed.
-- Engine:    MySQL 8.0+
-- =====================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ---------------------------------------------------------------------
-- 5. Remove account locking columns from healthcare_workers
--    (Reverse of: ALTER TABLE healthcare_workers ADD COLUMN ...)
-- ---------------------------------------------------------------------
ALTER TABLE healthcare_workers
    DROP COLUMN locked_until,
    DROP COLUMN failed_attempts,
    DROP COLUMN is_active;

-- ---------------------------------------------------------------------
-- 4. Remove model_version and processing_time from analysis_results
--    (Reverse of: ALTER TABLE analysis_results ADD COLUMN ...)
-- ---------------------------------------------------------------------
ALTER TABLE analysis_results
    DROP COLUMN processing_time,
    DROP COLUMN model_version;

-- ---------------------------------------------------------------------
-- 3. Remove status column from patient_cases
--    (Reverse of: ALTER TABLE patient_cases ADD COLUMN status ...)
--    MySQL automatically drops idx_patient_cases_status along with the
--    column since the index is defined solely on this column.
-- ---------------------------------------------------------------------
ALTER TABLE patient_cases
    DROP COLUMN status;

-- ---------------------------------------------------------------------
-- 2. Drop images table
--    (Reverse of: CREATE TABLE images ...)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS images;

-- ---------------------------------------------------------------------
-- 1. Drop sessions table
--    (Reverse of: CREATE TABLE sessions ...)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS sessions;

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================================
-- Verification Queries (For Testing)
-- =====================================================================

-- Show all tables (should now have 4 tables: healthcare_workers, patient_cases, symptoms, analysis_results)
SHOW TABLES;

-- Verify healthcare_workers columns (should NOT have is_active, failed_attempts, locked_until)
SHOW COLUMNS FROM healthcare_workers;

-- Verify patient_cases columns (should NOT have status)
SHOW COLUMNS FROM patient_cases;

-- Verify analysis_results columns (should NOT have model_version, processing_time)
SHOW COLUMNS FROM analysis_results;

-- =====================================================================
-- END OF ROLLBACK MIGRATION
-- =====================================================================