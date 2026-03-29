import requests
import os
import json
import time

# --- 1. CONFIGURATION (GitHub Secrets) ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CACHE_FILE = "sent_matches.json"

# NBA props to scan
NBA_PROPS = ['player_points', 'player_rebounds', 'player_assists']

def send_alert(message):
    if not DISCORD_WEBHOOK: return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_dfs_engine():
    # Load Cache to prevent duplicate pings
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.read(f)
    except:
        cache = {}

    print("--- 🏀 NBA PROP SCAN STARTING ---")
    
    for prop in NBA_PROPS:
        # THE FIX: Absolute path from the documentation you provided
        # Format: /v4/sports/{sport}/odds/
        url = f"https://api.the-odds-api.com"
        
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': prop,
            'oddsFormat': 'american',
            'bookmakers': 'fanduel,draftkings'
        }
        
        try:
            print(f"DEBUG: Pulling {prop}...")
            res = requests.get(url, params=params, timeout=15)
            data = res.json()
            
            # If the response is a list, it's successful data
            if isinstance(data, list):
                if len(data) == 0:
                    print(f"ℹ️ No active lines for {prop} right now.")
                    continue
                
                print(f"✅ SUCCESS: Found {len(data)} games for {prop}")
                for game in data:
                    for book in game.get('bookmakers', []):
                        for market in book.get('markets', []):
                            for outcome in market.get('outcomes', []):
                                player = outcome.get('description')
                                line = outcome.get('point')
                                price = outcome.get('price')
                                
                                # UNIQUE ID: Prevents duplicate alerts for the same line
                                m_id = f"{player}_{prop}_{line}"
                                if m_id not in cache:
                                    msg = (f"🏀 **NBA PROP DETECTED**\n"
                                           f"Player: **{player}**\n"
                                           f"Prop: {prop.replace('player_', '').capitalize()}\n"
                                           f"Line: {line}\n"
                                           f"Odds: {price}")
                                    send_alert(msg)
                                    cache[m_id] = time.time()
            else:
                # This will print the specific API error if it's not a list
                print(f"❌ API Error: {data.get('message', 'Unknown Error')}")

        except Exception as e:
            print(f"❌ System Error on {prop}: {e}")

    # Save Cache
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

if __name__ == "__main__":
    # Test Heartbeat
    send_alert("🚀 **NBA SCAN INITIATED** - Scanning Points, Rebounds, and Assists...")
    run_dfs_engine()
