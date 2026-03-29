import requests
import os
import json
import time

API_KEY = os.getenv("ODDS_API_KEY")
WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

CACHE_FILE = "sent_cache.json"

SPORT_PROPS = {
    'basketball_nba': ['player_points', 'player_rebounds', 'player_assists'],
    'americanfootball_nfl': ['player_pass_yds', 'player_rush_yds'],
    'baseball_mlb': ['player_hits', 'player_home_runs']
}

# SETTINGS
MIN_EV = 0.03        # Lower = more plays
STRONG_EV = 0.07     # Only send stronger plays
MIN_ODDS = -200      # Avoid heavy favorites

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

# ------------------ EV LOGIC ------------------ #

def american_to_prob(odds):
    if odds is None:
        return None
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)

def calculate_ev(prob, payout=1.0):
    return (prob * payout) - (1 - prob)

def is_plus_ev(price):
    prob = american_to_prob(price)

    if prob is None:
        return False, 0, 0

    ev = calculate_ev(prob)

    return ev > MIN_EV, prob, ev

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

def process_game(game, sport, market, cache):
    for book in game.get("bookmakers", []):
        for m in book.get("markets", []):
            for outcome in m.get("outcomes", []):

                player = outcome.get("description") or outcome.get("name")
                price = outcome.get("price")
                line = outcome.get("point", "N/A")

                if not player or price is None:
                    continue

                # ✅ FILTER BAD ODDS
                if price < MIN_ODDS:
                    continue

                is_ev, prob, ev = is_plus_ev(price)

                # ✅ REQUIRE STRONGER PLAYS
                if not is_ev or ev < STRONG_EV:
                    continue

                match_id = f"{player}_{market}_{line}"

                if match_id in cache:
                    continue

                pp_link, ud_link = build_links(player)

                msg = (
                    f"🔥 STRONG +EV PROP ({sport.upper()})\n"
                    f"Player: {player}\n"
                    f"Prop: {market.replace('player_', '').title()} | Line: {line}\n"
                    f"Odds: {price}\n"
                    f"Win Prob: {round(prob * 100, 1)}%\n"
                    f"EV: {round(ev * 100, 1)}%\n\n"
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

# ------------------ MAIN ------------------ #

def main():
    print("Bot started")
    print("API KEY LOADED:", bool(API_KEY))
    print("WEBHOOK LOADED:", bool(WEBHOOK))

    try:
        run_engine()
        print("Run complete.")

    except Exception as e:
        print(f"Critical error: {e}")

if __name__ == "__main__":
    main()
