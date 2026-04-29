#!/usr/bin/env python3
"""
steam_owned_free.py
- Loads STEAM_API_KEY from environment or .env (optional).
- Fetches owned games for a SteamID and checks which are free via the Storefront API.
- Writes output to output.json.
- Do NOT commit your .env to source control.
"""

import json
import os
from pathlib import Path

import requests


# Optional: load .env if present (no external dependency required).
# If you prefer python-dotenv, remove this block and use load_dotenv().
def load_dotenv_from_file(dotenv_path: str = ".env"):
    p = Path(dotenv_path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        # Do not overwrite existing environment variables
        if key not in os.environ:
            os.environ[key] = val


# Try to load .env (safe to omit; keeps behavior compatible with env-only deployments)
load_dotenv_from_file()

# Read API key from environment
API_KEY = os.environ.get("STEAM_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "STEAM_API_KEY not set. Set it in the environment or a .env file."
    )

# Config
STEAM_ID = os.environ.get(
    "STEAM_ID", "76561199294079348"
)  # set STEAM_ID in env or default for convenience
OWNED_GAMES_URL = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
STOREFRONT_URL = "https://store.steampowered.com/api/appdetails"
REQUEST_TIMEOUT = 10  # seconds


def get_owned_games(api_key: str, steam_id: str):
    params = {
        "key": api_key,
        "steamid": steam_id,
        "include_appinfo": 1,
        "include_played_free_games": 1,
        "format": "json",
    }
    resp = requests.get(OWNED_GAMES_URL, params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json().get("response", {}).get("games", [])


def is_app_free(appid: int):
    try:
        r = requests.get(
            STOREFRONT_URL,
            params={"appids": appid, "cc": "US", "l": "en"},
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        info = r.json().get(str(appid), {})
        return bool(info.get("success") and info.get("data", {}).get("is_free"))
    except requests.RequestException:
        return False


def main():
    games = get_owned_games(API_KEY, STEAM_ID)
    free_owned = []
    for g in games:
        appid = g.get("appid")
        name = g.get("name")
        if appid is None:
            continue
        if is_app_free(appid):
            free_owned.append({"appid": appid, "name": name})
    output = {
        "steamid": STEAM_ID,
        "owned_count": len(games),
        "free_owned_count": len(free_owned),
        "free_owned": free_owned,
    }
    Path("output.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Owned games: {len(games)} — Free owned: {len(free_owned)}")


if __name__ == "__main__":
    main()
