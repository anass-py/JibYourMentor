-- Run once in Supabase: Project -> SQL Editor -> New query -> paste -> Run.
-- Adds the reason chips to the "Would you join?" survey.
-- Must be run BEFORE the site goes out to traders, or submissions fail.

alter table responses
  add column if not exists reasons text[] not null default '{}';


-- ---------------------------------------------------------------
-- Reading the results. Paste this into the SQL editor any time to
-- see which objections are actually coming up, most common first:
--
--   select reason, count(*) as times
--   from responses, unnest(reasons) as reason
--   group by reason
--   order by times desc;
--
-- Gives you exactly: "3x not-enough-to-gain, 2x wont-share-myfxbook".
--
-- And to read the free-text alongside the answer:
--
--   select answer, reasons, why, who, created_at
--   from responses
--   order by created_at desc;
-- ---------------------------------------------------------------
