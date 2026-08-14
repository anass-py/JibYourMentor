import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

import requests
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("MYFXBOOK_EMAIL")
PASSWORD = os.getenv("MYFXBOOK_PASSWORD")

BASE_URL = "https://www.myfxbook.com/api"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = PROJECT_ROOT / "docs" / "leaderboard-data.json"


def require_env(name, value):
    if not value:
        raise RuntimeError(f"Missing {name} in backend/.env")


def as_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def myfxbook_get(endpoint, params=None):
    response = requests.get(
        f"{BASE_URL}/{endpoint}.json",
        params=params or {},
        timeout=20,
    )
    response.raise_for_status()

    data = response.json()
    if data.get("error"):
        raise RuntimeError(data.get("message", "Myfxbook API error"))

    return data


def login():
    require_env("MYFXBOOK_EMAIL", EMAIL)
    require_env("MYFXBOOK_PASSWORD", PASSWORD)

    data = myfxbook_get(
        "login",
        {
            "email": EMAIL,
            "password": PASSWORD,
        },
    )

    return unquote(data["session"])


def logout(session):
    try:
        myfxbook_get("logout", {"session": session})
    except Exception as exc:
        print("Logout failed:", exc)


def normalize_account(account):
    return {
        "id": str(account.get("id", "")),
        "name": account.get("name") or "Unnamed account",
        "gain": as_float(account.get("gain")),
        "drawdown": as_float(account.get("drawdown")),
        "change": as_float(account.get("change")),
        "demo": bool(account.get("demo")),
        "verified": True,
    }


def build_leaderboard(accounts):
    live_accounts = [account for account in accounts if not account["demo"]]
    ranked = sorted(live_accounts, key=lambda account: account["gain"], reverse=True)

    for index, account in enumerate(ranked, start=1):
        account["rank"] = index

    return ranked


def main():
    session = login()

    try:
        watched = myfxbook_get("get-watched-accounts", {"session": session})
        accounts = [normalize_account(account) for account in watched.get("accounts", [])]
        ranked_accounts = build_leaderboard(accounts)

        payload = {
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "source": "myfxbook-watched-accounts",
            "rankingMetric": "gain",
            "totalWatchedAccounts": len(accounts),
            "eligibleAccounts": len(ranked_accounts),
            "topFive": ranked_accounts[:5],
            "accounts": ranked_accounts,
        }

        OUTPUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        print(f"Wrote {OUTPUT_FILE}")
        print(f"Watched accounts: {len(accounts)}")
        print(f"Eligible live accounts: {len(ranked_accounts)}")
        print("Top 5:")
        for account in ranked_accounts[:5]:
            print(
                f"  #{account['rank']} {account['name']} | "
                f"gain {account['gain']:.2f}% | drawdown {account['drawdown']:.2f}%"
            )

    finally:
        logout(session)


if __name__ == "__main__":
    main()
