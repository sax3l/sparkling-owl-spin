-- Create core tables for persons, companies, and vehicles
-- Based on ECaDP platform requirements from Projektbeskrivning.txt

-- Companies table - central registry for all company information
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    organization_number TEXT UNIQUE,
    business_form TEXT,
    industry_code TEXT,
    website TEXT,
    description TEXT,
    founded_date DATE,
    employees_count INTEGER,
    annual_revenue DECIMAL(15,2),
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    source_url TEXT,
    last_scraped_at TIMESTAMPTZ,
    data_quality data_quality_level DEFAULT 'unknown',
    
    CONSTRAINT companies_name_not_empty CHECK (length(trim(name)) > 0)
);

-- Persons table - individual people with company connections
CREATE TABLE persons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name TEXT,
    last_name TEXT,
    full_name TEXT NOT NULL,
    birth_date DATE,
    gender TEXT,
    nationality TEXT,
    profession TEXT,
    biography TEXT,
    linkedin_url TEXT,
    facebook_url TEXT,
    twitter_url TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    source_url TEXT,
    last_scraped_at TIMESTAMPTZ,
    data_quality data_quality_level DEFAULT 'unknown',
    
    CONSTRAINT persons_name_not_empty CHECK (length(trim(full_name)) > 0)
);

-- Vehicles table - comprehensive vehicle information
CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    registration_number TEXT UNIQUE NOT NULL,
    vin_number TEXT UNIQUE,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    variant TEXT,
    year INTEGER,
    color TEXT,
    fuel_type TEXT,
    transmission TEXT,
    engine_size DECIMAL(5,2),
    power_hp INTEGER,
    power_kw INTEGER,
    co2_emissions INTEGER,
    fuel_consumption_city DECIMAL(4,1),
    fuel_consumption_highway DECIMAL(4,1),
    fuel_consumption_combined DECIMAL(4,1),
    price_new DECIMAL(12,2),
    price_current DECIMAL(12,2),
    mileage INTEGER,
    first_registration_date DATE,
    inspection_valid_until DATE,
    insurance_valid_until DATE,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    source_url TEXT,
    last_scraped_at TIMESTAMPTZ,
    data_quality data_quality_level DEFAULT 'unknown',
    
    CONSTRAINT vehicles_year_valid CHECK (year IS NULL OR (year >= 1886 AND year <= EXTRACT(YEAR FROM NOW()) + 2)),
    CONSTRAINT vehicles_mileage_positive CHECK (mileage IS NULL OR mileage >= 0),
    CONSTRAINT vehicles_power_positive CHECK (power_hp IS NULL OR power_hp > 0)
);

-- Vehicle ownership relationship table
CREATE TABLE vehicle_ownership (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    person_id UUID REFERENCES persons(id) ON DELETE SET NULL,
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    ownership_type ownership_type NOT NULL DEFAULT 'owner',
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    source_url TEXT,
    
    CONSTRAINT vehicle_ownership_owner_check CHECK (
        (person_id IS NOT NULL AND company_id IS NULL) OR
        (person_id IS NULL AND company_id IS NOT NULL)
    ),
    CONSTRAINT vehicle_ownership_dates_check CHECK (
        start_date IS NULL OR end_date IS NULL OR start_date <= end_date
    )
);

-- Company roles - people's roles in companies
CREATE TABLE company_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    role company_role NOT NULL,
    title TEXT,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT true,
    salary_range TEXT,
    responsibilities TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    source_url TEXT,
    
    CONSTRAINT company_roles_unique_current UNIQUE (person_id, company_id, role, is_current),
    CONSTRAINT company_roles_dates_check CHECK (
        start_date IS NULL OR end_date IS NULL OR start_date <= end_date
    )
);

-- Person addresses
CREATE TABLE person_addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    address_type address_type NOT NULL DEFAULT 'home',
    street_address TEXT,
    city TEXT,
    postal_code TEXT,
    state_province TEXT,
    country TEXT DEFAULT 'SE',
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    is_current BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    source_url TEXT
);

-- Person contacts
CREATE TABLE person_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    contact_type contact_type NOT NULL,
    contact_value TEXT NOT NULL,
    is_primary BOOLEAN DEFAULT false,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    source_url TEXT,
    
    CONSTRAINT person_contacts_value_not_empty CHECK (length(trim(contact_value)) > 0)
);

-- Company addresses
CREATE TABLE company_addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    address_type address_type NOT NULL DEFAULT 'work',
    street_address TEXT,
    city TEXT,
    postal_code TEXT,
    state_province TEXT,
    country TEXT DEFAULT 'SE',
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    is_headquarters BOOLEAN DEFAULT false,
    is_current BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    source_url TEXT
);

-- Company contacts
CREATE TABLE company_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    contact_type contact_type NOT NULL,
    contact_value TEXT NOT NULL,
    department TEXT,
    is_primary BOOLEAN DEFAULT false,
    is_public BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    source_url TEXT,
    
    CONSTRAINT company_contacts_value_not_empty CHECK (length(trim(contact_value)) > 0)
);

-- Indexes for performance
CREATE INDEX idx_companies_name ON companies USING gin (name gin_trgm_ops);
CREATE INDEX idx_companies_org_number ON companies (organization_number);
CREATE INDEX idx_companies_industry ON companies (industry_code);
CREATE INDEX idx_companies_created_at ON companies (created_at);

CREATE INDEX idx_persons_full_name ON persons USING gin (full_name gin_trgm_ops);
CREATE INDEX idx_persons_first_name ON persons (first_name);
CREATE INDEX idx_persons_last_name ON persons (last_name);
CREATE INDEX idx_persons_created_at ON persons (created_at);

CREATE INDEX idx_vehicles_registration ON vehicles (registration_number);
CREATE INDEX idx_vehicles_vin ON vehicles (vin_number);
CREATE INDEX idx_vehicles_make_model ON vehicles (make, model);
CREATE INDEX idx_vehicles_year ON vehicles (year);
CREATE INDEX idx_vehicles_created_at ON vehicles (created_at);

CREATE INDEX idx_vehicle_ownership_vehicle ON vehicle_ownership (vehicle_id);
CREATE INDEX idx_vehicle_ownership_person ON vehicle_ownership (person_id);
CREATE INDEX idx_vehicle_ownership_company ON vehicle_ownership (company_id);
CREATE INDEX idx_vehicle_ownership_current ON vehicle_ownership (is_current);

CREATE INDEX idx_company_roles_person ON company_roles (person_id);
CREATE INDEX idx_company_roles_company ON company_roles (company_id);
CREATE INDEX idx_company_roles_current ON company_roles (is_current);

CREATE INDEX idx_person_addresses_person ON person_addresses (person_id);
CREATE INDEX idx_person_addresses_current ON person_addresses (is_current);

CREATE INDEX idx_person_contacts_person ON person_contacts (person_id);
CREATE INDEX idx_person_contacts_type ON person_contacts (contact_type);

CREATE INDEX idx_company_addresses_company ON company_addresses (company_id);
CREATE INDEX idx_company_addresses_current ON company_addresses (is_current);

CREATE INDEX idx_company_contacts_company ON company_contacts (company_id);
CREATE INDEX idx_company_contacts_type ON company_contacts (contact_type);

-- Comments
COMMENT ON TABLE companies IS 'Central registry for company information';
COMMENT ON TABLE persons IS 'Registry for individual persons';
COMMENT ON TABLE vehicles IS 'Comprehensive vehicle information database';
COMMENT ON TABLE vehicle_ownership IS 'Relationship between vehicles and their owners';
COMMENT ON TABLE company_roles IS 'Employment and role relationships';
COMMENT ON TABLE person_addresses IS 'Address information for persons';
COMMENT ON TABLE person_contacts IS 'Contact information for persons';
COMMENT ON TABLE company_addresses IS 'Address information for companies';
COMMENT ON TABLE company_contacts IS 'Contact information for companies';