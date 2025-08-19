-- Create triggers for auditing or other automated actions
/*
create function update_modified_column()
returns trigger as $$
begin
    new.modified_at = now();
    return new;
end;
$$ language plpgsql;

create trigger update_person_modtime
before update on persons
for each row execute procedure update_modified_column();
*/