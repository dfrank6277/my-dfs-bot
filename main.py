import requests
import os
import json
import time

API_KEY = os.getenv("ODDS_API_KEY")
WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

CACHE_FILE = "sent_cache.json"

SPORT_PROPS = {
    'basketball_nba': ['player_points'],
}

MIN_EV = 0.01
STRONG_EV = 0.02

# ---------------- UTIL ---------------- #

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

# ---------------- EV ---------------- #

def american_to_prob(odds):
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    return 100 / (odds + 100)

def calculate_ev(prob):
    return (prob * 1.0) - (1 - prob)

# ---------------- API ---------------- #

def fetch_events(sport):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/events"
    params = {"apiKey": API_KEY}

    res = requests.get(url, params=params)
    if res.status_code != 200:
        print("Event fetch failed:", res.text)
        return []

    return res.json()

def fetch_event_props(sport, event_id, market):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/events/{event_id}/odds"

    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": market,
        "oddsFormat": "american",
        "bookmakers": "draftkings,fanduel"
    }

    res = requests.get(url, params=params)

    if res.status_code != 200:
        print("Props fetch failed:", res.text)
        return None

    return res.json()

# ---------------- CORE ---------------- #

def process_event(event, sport, market, cache, found_flag):
    event_id = event["id"]
    home = event["home_team"]
    away = event["away_team"]

    data = fetch_event_props(sport, event_id, market)
    if not data:
        return

    for book in data.get("bookmakers", []):
        for m in book.get("markets", []):
            for outcome in m.get("outcomes", []):

                player = outcome.get("description") or outcome.get("name")
                price = outcome.get("price")
                line = outcome.get("point", "N/A")

                if not player or price is None:
                    continue

                prob = american_to_prob(price)
                ev = calculate_ev(prob)

                print(f"{player} | Odds {price} | EV {round(ev*100,2)}%")

                if ev < STRONG_EV:
                    continue

                key = f"{player}_{market}_{line}"

                if key in cache:
                    continue

                msg = (
                    f"🔥 +EV PROP\n"
                    f"{away} @ {home}\n"
                    f"{player}\n"
                    f"{market} | Line: {line}\n"
                    f"Odds: {price}\n"
                    f"EV: {round(ev*100,1)}%"
                )

                send_alert(msg)
                cache[key] = time.time()
                found_flag[0] = True

def run():
    cache = load_cache()
    found_flag = [False]

    for sport, markets in SPORT_PROPS.items():
        events = fetch_events(sport)

        for event in events:
            for market in markets:
                process_event(event, sport, market, cache, found_flag)

    save_cache(cache)

    if not found_flag[0]:
        send_alert("⚠️ No props found this run.")

# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    print("Bot starting...")
    print("Webhook:", bool(WEBHOOK))

    run()
