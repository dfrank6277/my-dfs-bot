import requests
import os
import json
import time

# --- 1. CONFIGURATION (GitHub Secrets) ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CACHE_FILE = "sent_matches.json"

# ALL DFS PROPS INCLUDING COMBOS (PRA)
NBA_PROPS = [
    'player_points', 
    'player_rebounds', 
    'player_assists', 
    'player_threepointers',
    'player_points_rebounds_assists', # The "Big Combo" (PRA)
    'player_points_rebounds',
    'player_points_assists',
    'player_rebounds_assists'
]

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

    print("--- 🏀 STARTING FULL NBA PROP SCAN ---")
    for prop in NBA_PROPS:
        # BULLETPROOF URL: Absolute path with slashes included
        url = "https://api.the-odds-api.com"
        params = {'apiKey': API_KEY, 'regions': 'us', 'markets': prop, 'oddsFormat': 'american'}
        
        try:
            print(f"DEBUG: Checking {prop}...")
            res = requests.get(url, params=params, timeout=15)
            
            if res.status_code == 200:
                data = res.json()
                print(f"✅ SUCCESS: Found data for {prop}")
                for game in data:
                    for book in game.get('bookmakers', []):
                        for market in book.get('markets', []):
                            for outcome in market.get('outcomes', []):
                                player = outcome.get('description')
                                line = outcome.get('point')
                                price = outcome.get('price')
                                
                                # EDGE LOGIC: Alert if price is -145 or better (Pro Confidence)
                                if price and price <= -145:
                                    m_id = f"{player}_{prop}_{line}"
                                    if m_id not in cache:
                                        prop_name = prop.replace('player_', '').replace('_', '+').upper()
                                        msg = (f"🔥 **NBA COMBO EDGE** 🔥\n"
                                               f"Player: **{player}**\n"
                                               f"Prop: {prop_name}\n"
                                               f"Line: {line}\n"
                                               f"Odds: {price} (Vegas Lock ✅)")
                                        send_alert(msg)
                                        cache[m_id] = time.time()
            else:
                print(f"❌ API Error {res.status_code} for {prop}")
        except Exception as e:
            print(f"❌ System Error for {prop}: {e}")

    # Save Memory
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

if __name__ == "__main__":
    print("--- 🚀 FINAL SYSTEM TEST: BOT IS ONLINE ---")
    send_alert("🤖 **DFS MASTER BOT ONLINE** - Scanning all NBA Props + Combos (PRA).")
    run_dfs_engine()
