# Notes

## What we built (Aug 14, 2026)

- Merged the apply form into `index.html` with an animated submit flow (checkmark, staggered text, auto-dismiss).
- `backend/verify_applications.py`: checks each applicant's Myfxbook link for track record verified, trading privileges verified, and balance >= $500 (converted to USD with simple static rates for non-USD/cent accounts).
- Applicants who pass all three get added to a new `contestants` table and emailed. Others get an email explaining what's missing.
- `docs/status.html`: a page applicants can check anytime for their own live verification status.
- Repo split into `docs/` (the public site, safe to deploy) and `backend/` (private tooling, holds real credentials, never deployed).

## Future features

- Verify balance only once the competition start date arrives (badges checked at apply-time, balance later) — needs a stored competition date.
- A way for applicants stuck in "needs_review" to trigger a recheck once they fix something, instead of waiting indefinitely.
- Run `verify_applications.py --watch` as a real background service instead of a terminal someone has to leave open.
- Connect the `contestants` table to the live leaderboard once the competition starts.
- Real FX rates instead of the current static/simple conversion table.
- UI showing verification is actively running, with an animation each time a badge gets verified.
