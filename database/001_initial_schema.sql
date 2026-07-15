-- =====================================================================
-- Migration: 001_create_schema.sql
-- Branch:    feature/database-setup
-- Purpose:   Initial schema for skin-lesion / tinea diagnosis tracking
--            system (Health Care Worker -> PatientCase -> Symptom /
--            AnalysisResult)
-- Engine:    MySQL 8.0+
-- =====================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ---------------------------------------------------------------------
-- Drop tables (reverse dependency order) -- safe for repeatable local dev
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS analysis_results;
DROP TABLE IF EXISTS symptoms;
DROP TABLE IF EXISTS patient_cases;
DROP TABLE IF EXISTS healthcare_workers;

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================================
-- Table: healthcare_workers
-- Entity: "Health Care worker"
-- Attributes: UserID (PK), username, password, email, phone,
--             full_name (composite -> first_name, last_name)
-- =====================================================================
CREATE TABLE healthcare_workers (
    user_id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,          -- always store a hash, never plaintext
    email           VARCHAR(100) NOT NULL,
    phone           VARCHAR(20)  NULL,
    first_name      VARCHAR(50)  NOT NULL,
    last_name       VARCHAR(50)  NOT NULL,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                   ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_healthcare_workers_username UNIQUE (username),
    CONSTRAINT uq_healthcare_workers_email    UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =====================================================================
-- Table: patient_cases
-- Entity: "PatientCase"
-- Relationship: healthcare_workers (1) --creates--> (M) patient_cases
-- Attributes: case_id (PK), case_date, patient_age, patient_gender,
--             patient_location, worker_id (FK)
-- =====================================================================
CREATE TABLE patient_cases (
    case_id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    worker_id           INT UNSIGNED NOT NULL,       -- FK -> healthcare_workers
    case_date           DATE         NOT NULL,
    patient_age         TINYINT UNSIGNED NULL,
    patient_gender      ENUM('male', 'female', 'other', 'unspecified')
                                     NOT NULL DEFAULT 'unspecified',
    patient_location    VARCHAR(255) NULL,
    created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                       ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_patient_cases_worker
        FOREIGN KEY (worker_id) REFERENCES healthcare_workers (user_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    INDEX idx_patient_cases_worker_id (worker_id),
    INDEX idx_patient_cases_case_date (case_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =====================================================================
-- Table: symptoms
-- Entity: "Symptom"
-- Relationship: patient_cases (1) --has--> (1) symptoms
-- Attributes: form_id (PK), itchinessLevel, previousTreatment,
--             isCircular, durationDays, notes, lesionLocation, scaling
-- =====================================================================
CREATE TABLE symptoms (
    form_id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    case_id             INT UNSIGNED NOT NULL,       -- FK -> patient_cases, 1:1
    itchiness_level     TINYINT UNSIGNED NULL,        -- e.g. scale 0-10
    previous_treatment  VARCHAR(255) NULL,
    is_circular         BOOLEAN      NULL,
    duration_days       SMALLINT UNSIGNED NULL,
    notes               TEXT         NULL,
    lesion_location     VARCHAR(255) NOT NULL,
    scaling             BOOLEAN      NULL,
    created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                       ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_symptoms_case
        FOREIGN KEY (case_id) REFERENCES patient_cases (case_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    -- Enforces the 1:1 cardinality shown in the diagram
    CONSTRAINT uq_symptoms_case_id UNIQUE (case_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =====================================================================
-- Table: analysis_results
-- Entity: "AnalysisResult"
-- Relationship: patient_cases (1) --has--> (1) analysis_results
-- Attributes: result_id (PK), diagnosis_label, confidence_score,
--             tinea_probability
-- =====================================================================
CREATE TABLE analysis_results (
    result_id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    case_id             INT UNSIGNED NOT NULL,       -- FK -> patient_cases, 1:1
    diagnosis_label     VARCHAR(100) NOT NULL,
    confidence_score    DECIMAL(5,4) NOT NULL,        -- 0.0000 - 1.0000
    tinea_probability   DECIMAL(5,4) NOT NULL,        -- 0.0000 - 1.0000
    created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                       ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_analysis_results_case
        FOREIGN KEY (case_id) REFERENCES patient_cases (case_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    -- Enforces the 1:1 cardinality shown in the diagram
    CONSTRAINT uq_analysis_results_case_id UNIQUE (case_id),

    CONSTRAINT chk_confidence_score_range
        CHECK (confidence_score BETWEEN 0 AND 1),
    CONSTRAINT chk_tinea_probability_range
        CHECK (tinea_probability BETWEEN 0 AND 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;