#!/usr/bin/env python3
"""
steam_owned_free.py
- Loads STEAM_API_KEY from environment or key.env/.env (optional).
- Uses default STEAM_ID 76561199294079348 (override with STEAM_ID env var).
- Fetches owned games for the SteamID and checks which are free via the Storefront API.
- Writes output to output.json.
"""

import json
import os
import time
from pathlib import Path

import requests

# --- Config ---
DEFAULT_STEAM_ID = "76561199294079348"
OWNED_GAMES_URL = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
STOREFRONT_URL = "https://store.steampowered.com/api/appdetails"
REQUEST_TIMEOUT = 10  # seconds
DELAY_BETWEEN_REQUESTS = 0.12  # seconds


# Load key.env or .env from script directory, without overwriting existing env vars
def load_keyfile(preferred_filenames=("key.env", ".env")):
    base = Path(__file__).resolve().parent
    for name in preferred_filenames:
        p = base.joinpath(name)
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
        return


load_keyfile(("key.env", ".env"))

API_KEY = os.environ.get("STEAM_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "STEAM_API_KEY not set. Put STEAM_API_KEY=your_key in key.env or .env next to this script, or export it."
    )

STEAM_ID = os.environ.get("STEAM_ID", DEFAULT_STEAM_ID)


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
        time.sleep(DELAY_BETWEEN_REQUESTS)
    output = {
        "steamid": STEAM_ID,
        "owned_count": len(games),
        "free_owned_count": len(free_owned),
        "free_owned": free_owned,
        "timestamp": int(time.time()),
    }
    Path("output.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Owned games: {len(games)} — Free owned: {len(free_owned)}")


if __name__ == "__main__":
    main()
