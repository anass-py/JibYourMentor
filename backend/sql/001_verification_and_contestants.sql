-- Run once in Supabase: Project -> SQL Editor -> New query -> paste -> Run.

alter table applications
  add column if not exists track_record_verified boolean not null default false,
  add column if not exists trading_privileges_verified boolean not null default false,
  add column if not exists balance_verified boolean not null default false,
  add column if not exists balance_public boolean not null default false,
  add column if not exists balance_usd numeric,
  add column if not exists last_checked_at timestamptz;

create table if not exists contestants (
  id uuid primary key default gen_random_uuid(),
  application_id uuid references applications(id) unique,
  name text,
  email text,
  myfxbook text,
  broker text,
  platform text,
  handle text,
  city text,
  created_at timestamptz not null default now()
);
-- contestants has no RLS policy for anon: only the backend (service_role key) writes to it.

create or replace function public.get_application_status(lookup_id uuid)
returns table (
  name text,
  status text,
  track_record_verified boolean,
  trading_privileges_verified boolean,
  balance_verified boolean,
  balance_public boolean,
  last_checked_at timestamptz
)
language sql security definer set search_path = public as $$
  select name, status, track_record_verified, trading_privileges_verified,
         balance_verified, balance_public, last_checked_at
  from applications
  where id = lookup_id
  limit 1;
$$;

grant execute on function public.get_application_status(uuid) to anon;
