-- ECaDP Platform MySQL Database Schema
-- Creates all tables for the Ethical Crawler & Data Platform

-- Set MySQL specific configurations
SET sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO';
SET innodb_strict_mode = 1;

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS ecadp DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecadp;

-- =============================================
-- CORE ENTITY TABLES
-- =============================================

-- Persons table
CREATE TABLE persons (
    person_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    personal_number_enc BLOB,
    personal_number_hash TEXT,
    first_name TEXT,
    middle_name TEXT,
    last_name TEXT,
    birth_date DATE,
    gender ENUM('unknown', 'female', 'male', 'other') DEFAULT 'unknown',
    civil_status TEXT,
    economy_summary TEXT,
    salary_decimal DECIMAL(15,2),
    has_remarks BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    source_job_id CHAR(36),
    
    INDEX idx_personal_number_hash (personal_number_hash(255)),
    INDEX idx_names (first_name(50), last_name(50)),
    INDEX idx_created_at (created_at),
    INDEX idx_source_job (source_job_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Companies table
CREATE TABLE companies (
    company_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    org_number VARCHAR(20) UNIQUE,
    company_name TEXT,
    company_form VARCHAR(50),
    registration_date DATE,
    deregistration_date DATE,
    status VARCHAR(50),
    address TEXT,
    postal_code VARCHAR(20),
    city VARCHAR(100),
    county VARCHAR(100),
    county_seat TEXT,
    municipal_seat TEXT,
    sni_code VARCHAR(20),
    industry TEXT,
    remark_control TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    source_job_id CHAR(36),
    
    INDEX idx_org_number (org_number),
    INDEX idx_company_name (company_name(100)),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_source_job (source_job_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Vehicles table
CREATE TABLE vehicles (
    vehicle_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    registration_number VARCHAR(20) UNIQUE,
    vehicle_type VARCHAR(50),
    brand VARCHAR(100),
    model TEXT,
    model_year YEAR,
    color VARCHAR(50),
    fuel_type VARCHAR(50),
    owner_kind ENUM('person', 'company'),
    owner_id BIGINT,
    first_registration_date DATE,
    inspection_valid_until DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    source_job_id CHAR(36),
    
    INDEX idx_registration_number (registration_number),
    INDEX idx_brand_model (brand, model(50)),
    INDEX idx_owner (owner_kind, owner_id),
    INDEX idx_created_at (created_at),
    INDEX idx_source_job (source_job_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Scraping jobs
CREATE TABLE scraping_jobs (
    id CHAR(36) PRIMARY KEY,
    job_type ENUM('crawl', 'scrape', 'export', 'diagnostic') NOT NULL,
    status ENUM('pending', 'queued', 'running', 'completed', 'failed', 'cancelled') DEFAULT 'pending',
    url TEXT,
    template_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    error_message TEXT,
    progress_percentage INTEGER DEFAULT 0,
    total_urls INTEGER DEFAULT 0,
    processed_urls INTEGER DEFAULT 0,
    results_count INTEGER DEFAULT 0,
    metadata JSON,
    
    INDEX idx_job_type (job_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_template_name (template_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Templates for data extraction
CREATE TABLE templates (
    template_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    template_name VARCHAR(255) UNIQUE NOT NULL,
    version VARCHAR(20) DEFAULT '1.0',
    entity_type VARCHAR(50),
    template_content JSON NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    description TEXT,
    
    INDEX idx_template_name (template_name),
    INDEX idx_entity_type (entity_type),
    INDEX idx_is_active (is_active),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;