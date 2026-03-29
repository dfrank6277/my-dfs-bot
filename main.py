import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CACHE_FILE = "sent_matches.json"

# All major NBA props
NBA_PROPS = ['player_points', 'player_rebounds', 'player_assists', 'player_threepointers']

def send_alert(message):
    if not DISCORD_WEBHOOK: return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_dfs_engine():
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
    except:
        cache = {}

    print("--- SCANNING NBA PROPS ---")
    for prop in NBA_PROPS:
        # ABSOLUTE URL FIX: No room for mashing errors
        url = f"https://api.the-odds-api.com"
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': prop,
            'oddsFormat': 'american'
        }
        
        try:
            print(f"DEBUG: Checking {prop}...")
            res = requests.get(url, params=params, timeout=15)
            
            if res.status_code == 200:
                data = res.json()
                print(f"✅ Found data for {prop}")
                for game in data:
                    for book in game.get('bookmakers', []):
                        for market in book.get('markets', []):
                            for outcome in market.get('outcomes', []):
                                player = outcome.get('description')
                                line = outcome.get('point')
                                price = outcome.get('price')
                                
                                # DFS EDGE LOGIC: Alert if price is -140 or better
                                if price and price <= -140:
                                    m_id = f"{player}_{prop}_{line}"
                                    if m_id not in cache:
                                        msg = (f"🏀 **NBA PROP EDGE**\n"
                                               f"Player: **{player}**\n"
                                               f"Prop: {prop.replace('player_', '').capitalize()}\n"
                                               f"Line: {line}\n"
                                               f"Odds: {price} (Vegas Favorite ✅)")
                                        send_alert(msg)
                                        cache[m_id] = time.time()
            else:
                print(f"❌ API Error {res.status_code} for {prop}")
        except Exception as e:
            print(f"❌ Connection Error for {prop}: {e}")

    # Save Cache
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

if __name__ == "__main__":
    print("--- 24/7 NBA & ESPORTS ENGINE ONLINE ---")
    send_alert("🤖 **NBA Prop Scanner is Active** - Scanning Points, Rebounds, Assists, and Threes.")
    run_val_bot()
