-- 1. Enable the pg_net extension to make HTTP requests
create extension if not exists pg_net;

-- 2. Create a function that calls the Edge Function
create or replace function public.handle_new_partner_application()
returns trigger as $$
declare
  -- TODO: Replace with your actual Project URL and Service Role Key
  -- You can find these in Supabase Dashboard -> Project Settings -> API
  project_url text := 'https://YOUR_PROJECT_REF.supabase.co';
  service_role_key text := 'YOUR_SERVICE_ROLE_KEY'; 
begin
  -- Make a POST request to the Edge Function
  perform net.http_post(
    url := project_url || '/functions/v1/send-email',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || service_role_key
    ),
    body := jsonb_build_object('record', new)
  );
  return new;
end;
$$ language plpgsql security definer;

-- 3. Create the trigger on "partner application" table
-- Note: We use quotes because the table name has a space
drop trigger if exists on_new_partner_application on "partner application";

create trigger on_new_partner_application
after insert on "partner application"
for each row
execute function public.handle_new_partner_application();
