import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CACHE_FILE = "sent_matches.json"

# Major NBA props
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

    print("--- 🏀 SCANNING NBA PROPS ---")
    for prop in NBA_PROPS:
        # ABSOLUTE URL
        url = "https://api.the-odds-api.com"
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': prop,
            'oddsFormat': 'american',
            'bookmakers': 'fanduel,draftkings' # FORCES a valid data structure
        }
        
        try:
            print(f"DEBUG: Checking {prop}...")
            res = requests.get(url, params=params, timeout=15)
            data = res.json()
            
            # CRITICAL FIX: Ensure we are looking at a LIST of games
            if isinstance(data, list):
                print(f"✅ SUCCESS: Found {len(data)} games for {prop}")
                for game in data:
                    for book in game.get('bookmakers', []):
                        for market in book.get('markets', []):
                            for outcome in market.get('outcomes', []):
                                player = outcome.get('description')
                                line = outcome.get('point')
                                price = outcome.get('price')
                                
                                if price and price <= -145:
                                    m_id = f"{player}_{prop}_{line}"
                                    if m_id not in cache:
                                        msg = f"🔥 **NBA PROP**\n**{player}**\n{prop.replace('player_', '')}: {line}\nOdds: {price} ✅"
                                        send_alert(msg)
                                        cache[m_id] = time.time()
            else:
                # This will print the actual error if it's not a list
                print(f"⚠️ API Info: {data}")

        except Exception as e:
            print(f"❌ Error on {prop}: {e}")

    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

if __name__ == "__main__":
    run_dfs_engine()
