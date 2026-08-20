-- Run once in Supabase: Project -> SQL Editor -> New query -> paste -> Run.
-- Optional email on the survey, so the traders who answer "yes" can be
-- told when Edition One opens. Run BEFORE the site goes out, or any
-- submission that includes an email will fail.

alter table responses
  add column if not exists email text;


-- ---------------------------------------------------------------
-- The list to mail when Edition One opens — everyone who said yes
-- and left an address:
--
--   select email, who, created_at
--   from responses
--   where answer = 'yes' and email is not null and email <> ''
--   order by created_at;
--
-- Everyone who left an address, whatever they answered:
--
--   select answer, email, who from responses
--   where email is not null and email <> '';
-- ---------------------------------------------------------------
