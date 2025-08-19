-- Create RPC functions for business logic
/*
create function get_company_employee_count(company_id uuid)
returns int as $$
  select count(*) from persons where persons.company_id = get_company_employee_count.company_id;
$$ language sql stable;
*/