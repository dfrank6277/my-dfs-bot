import requests
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("ODDS_API_KEY")
WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

CACHE_FILE = "sent_cache.json"
SCAN_INTERVAL = 900  # 15 minutes

SPORT_PROPS = {
    'basketball_nba': ['player_points', 'player_rebounds', 'player_assists'],
    'americanfootball_nfl': ['player_pass_yds', 'player_rush_yds'],
    'baseball_mlb': ['player_hits', 'player_home_runs']
}

# ------------------ UTIL ------------------ #

def send_alert(message):
    if not WEBHOOK:
        print("No webhook set.")
        return
    try:
        requests.post(WEBHOOK, json={"content": message}, timeout=10)
    except Exception as e:
        print(f"Webhook error: {e}")

def load_cache():
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def build_links(player):
    q = player.replace(" ", "%20")
    return (
        f"https://app.prizepicks.com/?search={q}",
        f"https://underdogfantasy.com/search?q={q}"
    )

# ------------------ CORE ENGINE ------------------ #

def fetch_odds(sport, market):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"

    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": market,
        "oddsFormat": "american",
        "bookmakers": "draftkings,fanduel"
    }

    try:
        res = requests.get(url, params=params, timeout=15)

        if res.status_code != 200:
            print(f"API error {res.status_code}: {res.text}")
            return []

        return res.json()

    except Exception as e:
        print(f"Fetch error: {e}")
        return []

def is_strong_line(price):
    # Simple filter (can upgrade later)
    return price is not None and price <= -300

def process_game(game, sport, market, cache):
    for book in game.get("bookmakers", []):
        for m in book.get("markets", []):
            for outcome in m.get("outcomes", []):

                player = outcome.get("description") or outcome.get("name")
                price = outcome.get("price")
                line = outcome.get("point", "N/A")

                if not player or not is_strong_line(price):
                    continue

                match_id = f"{player}_{market}_{line}"

                if match_id in cache:
                    continue

                pp_link, ud_link = build_links(player)

                msg = (
                    f"🎯 DFS PROP ALERT ({sport.upper()})\n"
                    f"Player: {player}\n"
                    f"Prop: {market.replace('player_', '').title()} | Line: {line}\n"
                    f"Odds: {price}\n\n"
                    f"PrizePicks: {pp_link}\n"
                    f"Underdog: {ud_link}"
                )

                send_alert(msg)
                cache[match_id] = time.time()

def run_engine():
    cache = load_cache()

    for sport, markets in SPORT_PROPS.items():
        for market in markets:

            print(f"Scanning {sport} - {market}")

            games = fetch_odds(sport, market)

            for game in games:
                process_game(game, sport, market, cache)

    save_cache(cache)

# ------------------ MAIN LOOP ------------------ #

def main():
    send_alert("DFS BOT LIVE - scanning props")

    while True:
        try:
            run_engine()
            print("Cycle complete. Sleeping...\n")
            time.sleep(SCAN_INTERVAL)

        except Exception as e:
            print(f"Critical error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
