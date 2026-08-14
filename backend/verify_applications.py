"""
Reads pending applicants from Supabase and checks three things on their
submitted Myfxbook link, in one headless-browser page load each:
  - Track record verified   (#trackRecordDiv has class "checked")
  - Trading privileges verified (#tradingPrivilegesDiv has class "checked")
  - Balance >= $500 USD      (#statsBalance, only present if the applicant
                               made it public; converts to USD using simple
                               static rates, see FX_TO_USD -- rough on purpose,
                               swap for a real FX source before this needs to
                               be precise)

Myfxbook's API doesn't expose any of this for accounts you don't own
(get-watched-accounts only returns id/name/gain/drawdown/demo/change), and
the public pages sit behind a Cloudflare bot-check that blocks plain HTTP
requests — so this drives a real headless Chromium instead of calling the
API or scraping with requests.

Every applicant gets exactly one outcome per run, written back to
Supabase, and exactly one email:
  - verified        all three passed -> "you're clear" email, added to
                     the `contestants` table
  - balance_pending  both badges passed, balance isn't public yet ->
                     "make your balance public" email
  - needs_review     anything else -> email naming what specifically
                     didn't verify

If sending the email fails, the applicant's status is left as 'new' so
the next run retries rather than silently marking them processed with no
notification ever sent.

NOTE: balance is checked in the same pass as the badges. The eventual
design is track record/trading privileges at apply-time, balance only
once a competition start date arrives — that just needs a stored
COMPETITION_DATE checked each --watch cycle (see the marker in main());
not built yet, deliberately, until there's a real date to use.

Usage:
    python3 verify_applications.py                  # run one pass
    python3 verify_applications.py --dry-run         # one pass, no writes/emails
    python3 verify_applications.py --watch           # loop forever, polling for new rows
    python3 verify_applications.py --watch --interval 30
"""
import argparse
import os
import re
import smtplib
import time
from datetime import datetime, timezone
from email.message import EmailMessage

import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
APPLICATIONS_TABLE = "applications"
CONTESTANTS_TABLE = "contestants"

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD")
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

STATUS_PAGE_URL = os.getenv("STATUS_PAGE_URL", "https://anass-py.github.io/JibYourMentor/status.html")

BALANCE_MIN_USD = 500

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
PAGE_LOAD_TIMEOUT_MS = 20_000
DELAY_BETWEEN_APPLICANTS_S = 1.5
DEFAULT_POLL_INTERVAL_S = 60


def require_env(name, value):
    if not value:
        raise RuntimeError(f"Missing {name} in backend/.env")


def check_required_env():
    require_env("SUPABASE_URL", SUPABASE_URL)
    require_env("SUPABASE_SERVICE_ROLE_KEY", SUPABASE_KEY)
    require_env("SMTP_EMAIL", SMTP_EMAIL)
    require_env("SMTP_APP_PASSWORD", SMTP_APP_PASSWORD)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def supabase_headers(extra=None):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    if extra:
        headers.update(extra)
    return headers


def fetch_pending_applications():
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/{APPLICATIONS_TABLE}",
        params={"status": "eq.new", "select": "*", "order": "created_at.asc"},
        headers=supabase_headers(),
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def update_application(application_id, fields):
    response = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{APPLICATIONS_TABLE}",
        params={"id": f"eq.{application_id}"},
        headers=supabase_headers({"Content-Type": "application/json", "Prefer": "return=minimal"}),
        json=fields,
        timeout=20,
    )
    response.raise_for_status()


def insert_contestant(applicant):
    payload = {
        "application_id": applicant["id"],
        "name": applicant.get("name"),
        "email": applicant.get("email"),
        "myfxbook": applicant.get("myfxbook"),
        "broker": applicant.get("broker"),
        "platform": applicant.get("platform"),
        "handle": applicant.get("handle"),
        "city": applicant.get("city"),
    }
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/{CONTESTANTS_TABLE}",
        headers=supabase_headers({"Content-Type": "application/json", "Prefer": "return=minimal"}),
        json=payload,
        timeout=20,
    )
    response.raise_for_status()


# Static, approximate FX-to-USD rates so a non-USD balance can still clear
# the $500 bar. Deliberately rough ("simple for now") -- not sourced live,
# not fit for anything that needs a precise or current rate. Revisit with
# a real FX source if this ever matters for more than a pass/fail check.
# USC is Myfxbook's own "cent account" label, not a currency -- 100 of it
# is $1, so it's a flat /100, not a market rate.
FX_TO_USD = {
    "USC": 0.01,
    "CHF": 1.12,
    "$": 1.0,
    "€": 1.08,
    "£": 1.27,
    "¥": 0.0067,
}


def parse_balance(raw_text):
    """Returns (usd_value_or_None, currency_recognized). Reads the leading
    currency marker off Myfxbook's balance text (e.g. '$1,234.56',
    'USC81,940.46', '€3,714.93') and converts to an approximate USD value
    via FX_TO_USD. Unrecognized markers return (None, False)."""
    if not raw_text:
        return None, False

    text = raw_text.strip()
    marker = next((m for m in FX_TO_USD if text.upper().startswith(m.upper())), None)
    if marker is None:
        return None, False

    numeric = re.sub(r"[^0-9.]", "", text[len(marker):])
    if not numeric:
        return None, False
    try:
        value = float(numeric)
    except ValueError:
        return None, False

    return value * FX_TO_USD[marker], True


def check_all(page, myfxbook_url):
    page.goto(myfxbook_url, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT_MS)
    page.wait_for_timeout(3000)

    result = page.evaluate(
        """() => {
            const track = document.querySelector('#trackRecordDiv');
            const priv = document.querySelector('#tradingPrivilegesDiv');
            const bal = document.querySelector('#statsBalance');
            return {
                trackFound: !!track,
                trackChecked: track ? track.classList.contains('checked') : false,
                privFound: !!priv,
                privChecked: priv ? priv.classList.contains('checked') : false,
                balFound: !!bal,
                balText: bal ? bal.textContent.trim() : null,
            };
        }"""
    )

    balance_usd, currency_ok = parse_balance(result["balText"]) if result["balFound"] else (None, False)

    return {
        "track_found": result["trackFound"],
        "track_record_verified": result["trackChecked"],
        "priv_found": result["privFound"],
        "trading_privileges_verified": result["privChecked"],
        "balance_public": result["balFound"],
        "balance_raw_text": result["balText"],
        "balance_usd": balance_usd,
        "balance_currency_ok": currency_ok,
    }


def classify(check):
    """Returns (classification, balance_state)."""
    badges_ok = check["track_record_verified"] and check["trading_privileges_verified"]

    if not check["balance_public"]:
        balance_state = "not_public"
    elif not check["balance_currency_ok"] or check["balance_usd"] is None:
        balance_state = "unrecognized_currency"
    elif check["balance_usd"] < BALANCE_MIN_USD:
        balance_state = "too_low"
    else:
        balance_state = "ok"

    if badges_ok and balance_state == "ok":
        return "verified", balance_state
    if badges_ok and balance_state == "not_public":
        return "balance_pending", balance_state
    return "needs_review", balance_state


def compose_email(applicant, check, classification, balance_state):
    name = applicant.get("name") or "there"
    status_link = f"{STATUS_PAGE_URL}?id={applicant['id']}"

    if classification == "verified":
        subject = "You're in — JibYourMentor Edition One"
        body = (
            f"Hi {name},\n\n"
            "Good news — we checked your Myfxbook profile and everything came back "
            "verified: track record, trading privileges, and account balance.\n\n"
            "You're clear to go. See you at the competition.\n\n"
            f"Check your status anytime: {status_link}\n\n"
            "— JibYourMentor"
        )
        return subject, body

    if classification == "balance_pending":
        subject = "Almost there — make your balance public"
        body = (
            f"Hi {name},\n\n"
            "Your Myfxbook track record and trading privileges are both verified. "
            "One thing left: your account balance isn't publicly visible on your "
            "Myfxbook page, so we can't confirm you meet the $500 minimum.\n\n"
            "On Myfxbook, open your account's privacy settings and enable "
            "'Balance/Equity' visibility. We'll pick it up on our next check.\n\n"
            f"Check your status anytime: {status_link}\n\n"
            "— JibYourMentor"
        )
        return subject, body

    problems = []
    if not check["track_record_verified"]:
        problems.append("Track record isn't verified on Myfxbook yet")
    if not check["trading_privileges_verified"]:
        problems.append("Trading privileges aren't verified on Myfxbook yet")
    if check["track_record_verified"] and check["trading_privileges_verified"]:
        if balance_state == "unrecognized_currency":
            problems.append("We couldn't read your account's currency to check the balance")
        elif balance_state == "too_low":
            problems.append(f"Your balance is below the ${BALANCE_MIN_USD} minimum (converted to USD)")

    subject = "About your JibYourMentor application"
    body = (
        f"Hi {name},\n\n"
        "We checked your Myfxbook profile and couldn't clear your application yet:\n\n"
        + "\n".join(f"- {p}" for p in problems)
        + "\n\nFix what applies and we'll pick it up on our next check.\n\n"
        f"Check your status anytime: {status_link}\n\n"
        "— JibYourMentor"
    )
    return subject, body


def send_email(to_email, subject, body):
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"JibYourMentor <{SMTP_EMAIL}>"
    message["To"] = to_email
    message.set_content(body)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        server.send_message(message)


def process_applicant(page, applicant, dry_run):
    name = applicant.get("name", "?")
    email = applicant.get("email", "?")
    link = applicant.get("myfxbook", "")

    try:
        check = check_all(page, link)
    except Exception as exc:
        print(f"[NEEDS_REVIEW ] {name} <{email}>")
        print(f"                error loading {link}: {exc}")
        if not dry_run:
            update_application(applicant["id"], {"status": "needs_review", "last_checked_at": now_iso()})
        return "needs_review"

    classification, balance_state = classify(check)
    subject, body = compose_email(applicant, check, classification, balance_state)

    track_mark = "✓" if check["track_record_verified"] else "✗"
    priv_mark = "✓" if check["trading_privileges_verified"] else "✗"
    bal_mark = "✓" if balance_state == "ok" else ("⚠" if balance_state == "not_public" else "✗")

    print(f"[{classification.upper():14}] {name} <{email}>")
    print(f"                track record {track_mark}  trading privileges {priv_mark}  balance {bal_mark} ({balance_state})")
    print(f"                {link}")
    if check["balance_public"]:
        reading = check["balance_raw_text"]
        parsed = f"${check['balance_usd']:.2f}" if check["balance_usd"] is not None else "unparseable"
        print(f"                balance reading: {reading} -> {parsed}")

    if dry_run:
        print("                dry run — would email:")
        print(f"                subject: {subject}")
        for line in body.splitlines():
            print(f"                | {line}")
        return classification

    try:
        send_email(email, subject, body)
    except Exception as exc:
        print(f"                email failed, leaving status='new' to retry: {exc}")
        return None

    update_application(applicant["id"], {
        "status": classification,
        "track_record_verified": check["track_record_verified"],
        "trading_privileges_verified": check["trading_privileges_verified"],
        "balance_verified": balance_state == "ok",
        "balance_public": check["balance_public"],
        "balance_usd": check["balance_usd"],
        "last_checked_at": now_iso(),
    })

    if classification == "verified":
        insert_contestant(applicant)
        print("                emailed + marked verified + added to contestants")
    else:
        print(f"                emailed + marked {classification}")

    return classification


def run_once(dry_run):
    applicants = fetch_pending_applications()
    if not applicants:
        print("No applications with status='new'.")
        return

    print(f"Checking {len(applicants)} applicant(s){' (dry run)' if dry_run else ''}...\n")

    counts = {"verified": 0, "balance_pending": 0, "needs_review": 0}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=USER_AGENT)

        for i, applicant in enumerate(applicants):
            result = process_applicant(page, applicant, dry_run)
            if result:
                counts[result] += 1

            if i < len(applicants) - 1:
                time.sleep(DELAY_BETWEEN_APPLICANTS_S)

        browser.close()

    print(
        f"\nDone. {counts['verified']} verified, "
        f"{counts['balance_pending']} balance-pending, "
        f"{counts['needs_review']} need review."
    )
    if dry_run:
        print("Dry run — no statuses were written and no emails were sent.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print results only, no writes or emails")
    parser.add_argument("--watch", action="store_true", help="Loop forever, polling for new applicants")
    parser.add_argument("--interval", type=int, default=DEFAULT_POLL_INTERVAL_S, help="Seconds between polls in --watch mode")
    args = parser.parse_args()

    check_required_env()

    if not args.watch:
        run_once(args.dry_run)
        return

    print(f"Watching for new applications every {args.interval}s. Ctrl+C to stop.\n")
    while True:
        try:
            # Future: gate the balance portion of check_all() on a stored
            # COMPETITION_DATE here (skip/neutral until date.today() >= it),
            # once there's a real date to use. Not built yet — see docstring.
            run_once(args.dry_run)
        except Exception as exc:
            print(f"Poll failed: {exc}")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
