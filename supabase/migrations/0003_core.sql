-- Create core tables for persons, companies, and vehicles
/*
create table companies (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    created_at timestamptz default now()
);

create table persons (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    company_id uuid references companies(id),
    created_at timestamptz default now()
);
*/