-- =====================================================================
-- Migration: 004_create_symptoms_table.sql
-- Purpose: Create symptoms table for storing structured symptom data
-- =====================================================================

USE stellarx;

CREATE TABLE IF NOT EXISTS symptoms (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    case_id VARCHAR(36) NOT NULL UNIQUE,
    
    -- Basic Symptoms (checkboxes)
    redness BOOLEAN DEFAULT FALSE,
    scaling BOOLEAN DEFAULT FALSE,
    ring_shaped BOOLEAN DEFAULT FALSE,
    itching BOOLEAN DEFAULT FALSE,
    pain BOOLEAN DEFAULT FALSE,
    
    -- Duration & Severity
    duration_value INT NULL,
    duration_unit VARCHAR(20) NULL,
    itch_severity INT NULL,
    
    -- Lesion Characteristics
    lesion_size_cm FLOAT NULL,
    lesion_border VARCHAR(50) NULL,
    lesion_shape VARCHAR(50) NULL,
    lesion_color VARCHAR(50) NULL,
    lesion_locations VARCHAR(255) NULL,
    
    -- Additional Clinical Signs
    central_clearing BOOLEAN DEFAULT FALSE,
    previous_treatment VARCHAR(50) NULL,
    nail_changes BOOLEAN DEFAULT FALSE,
    
    -- Notes
    notes TEXT NULL,
    
    -- Audit
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign key
    CONSTRAINT fk_symptoms_case
        FOREIGN KEY (case_id) REFERENCES patient_cases(id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_symptoms_case_id (case_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Verify
SHOW TABLES;
DESCRIBE symptoms;