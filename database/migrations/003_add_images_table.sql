-- =====================================================================
-- Migration: 003_add_images_table.sql
-- Purpose: Create images table for storing multiple images per case
-- =====================================================================

-- 1. Create images table
CREATE TABLE images (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    case_id VARCHAR(36) NOT NULL,
    s3_key VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INT NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    image_index INT DEFAULT 0,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key
    FOREIGN KEY (case_id) REFERENCES patient_cases(id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_images_case_id (case_id),
    INDEX idx_images_case_id_index (case_id, image_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Verify
SHOW TABLES;
DESCRIBE images;