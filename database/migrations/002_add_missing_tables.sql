-- =====================================================================
-- Migration: 002_add_missing_tables.sql
-- Branch:    feature/database-setup
-- Purpose:   Add missing tables and columns for production-ready system
--            - sessions table (JWT token storage)
--            - images table (S3 storage reference)
--            - status column in patient_cases
--            - model_version, processing_time in analysis_results
--            - account locking columns in healthcare_workers
-- Engine:    MySQL 8.0+
-- Dependencies: 001_create_schema.sql (must run first)
-- =====================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================================
-- 1. Add account locking columns to healthcare_workers
--    (Must run first before sessions table references it)
-- =====================================================================

ALTER TABLE healthcare_workers
    ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN failed_attempts INT UNSIGNED NOT NULL DEFAULT 0,
    ADD COLUMN locked_until DATETIME NULL;

-- =====================================================================
-- 2. Create sessions table (JWT Token Storage)
--    Relationship: healthcare_workers (1) --has--> (M) sessions
-- =====================================================================

CREATE TABLE sessions (
    session_id      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id         CHAR(36) NOT NULL,
    token           VARCHAR(500) NOT NULL,
    expires_at      DATETIME NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key to healthcare_workers
    CONSTRAINT fk_sessions_worker
        FOREIGN KEY (user_id) REFERENCES healthcare_workers (user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    -- Performance indexes
    INDEX idx_sessions_token (token(255)),
    INDEX idx_sessions_expires_at (expires_at),
    INDEX idx_sessions_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- 3. Create images table (AWS S3 Storage Reference)
--    Relationship: patient_cases (1) --has--> (M) images
-- =====================================================================

CREATE TABLE images (
    image_id        CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    case_id         CHAR(36) NOT NULL,
    s3_key          VARCHAR(500) NOT NULL,          -- Unique S3 path
    file_name       VARCHAR(255) NOT NULL,          -- Original filename
    file_size       INT UNSIGNED NOT NULL,           -- In bytes
    content_type    VARCHAR(100) NOT NULL,           -- image/jpeg, etc.
    uploaded_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key to patient_cases
    CONSTRAINT fk_images_case
        FOREIGN KEY (case_id) REFERENCES patient_cases (case_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    -- Performance indexes
    INDEX idx_images_case_id (case_id),
    INDEX idx_images_uploaded_at (uploaded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- 4. Add status column to patient_cases
--    Enables workflow: DRAFT → READY_FOR_ANALYSIS → COMPLETED → REVIEWED
-- =====================================================================

ALTER TABLE patient_cases
    ADD COLUMN status ENUM('DRAFT', 'READY_FOR_ANALYSIS', 'COMPLETED', 'REVIEWED')
        NOT NULL DEFAULT 'DRAFT';

-- Add index for faster status queries
CREATE INDEX idx_patient_cases_status ON patient_cases (status);

-- =====================================================================
-- 5. Add model tracking columns to analysis_results
--    - model_version: Which AI model produced this result
--    - processing_time: How long the AI took (in milliseconds)
-- =====================================================================

ALTER TABLE analysis_results
    ADD COLUMN model_version VARCHAR(50) NOT NULL DEFAULT 'v1.0.0',
    ADD COLUMN processing_time INT UNSIGNED NOT NULL DEFAULT 0;

-- =====================================================================
-- 6. Verification Queries (For Testing)
-- =====================================================================

-- Show all tables (should now have 6 tables)
SHOW TABLES;

-- Check sessions table structure
DESCRIBE sessions;

-- Check images table structure
DESCRIBE images;

-- Check healthcare_workers new columns
SHOW COLUMNS FROM healthcare_workers LIKE 'is_active';
SHOW COLUMNS FROM healthcare_workers LIKE 'failed_attempts';
SHOW COLUMNS FROM healthcare_workers LIKE 'locked_until';

-- Check patient_cases status column
SHOW COLUMNS FROM patient_cases LIKE 'status';

-- Check analysis_results new columns
SHOW COLUMNS FROM analysis_results LIKE 'model_version';
SHOW COLUMNS FROM analysis_results LIKE 'processing_time';

-- Show all foreign keys
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM
    INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE
    REFERENCED_TABLE_SCHEMA = 'stellarx'
    AND REFERENCED_TABLE_NAME IS NOT NULL;

-- =====================================================================
-- END OF MIGRATION
-- =====================================================================