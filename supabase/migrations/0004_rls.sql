-- Enable Row Level Security and define policies
/*
alter table persons enable row level security;

create policy "Users can see their own person record"
on persons for select
using ( auth.uid() = id );
*/