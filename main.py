import requests
import os
import json
import time

# --- 1. CONFIGURATION ---
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CACHE_FILE = "sent_matches.json"

# All major NBA props offered by DFS apps
NBA_PROPS = [
    'player_points', 
    'player_rebounds', 
    'player_assists', 
    'player_threepointers', 
    'player_blocks', 
    'player_steals'
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

    # --- NBA PROP SCANNER ---
    print("Scanning NBA Player Props...")
    for prop in NBA_PROPS:
        # Fixed URL path to prevent mashing
        url = f"https://api.the-odds-api.com"
        params = {
            'apiKey': ODDS_API_KEY,
            'regions': 'us',
            'markets': prop,
            'oddsFormat': 'american'
        }
        
        try:
            res = requests.get(url, params=params, timeout=15)
            if res.status_code == 200:
                data = res.json()
                for game in data:
                    for book in game.get('bookmakers', []):
                        for market in book.get('markets', []):
                            for outcome in market.get('outcomes', []):
                                player = outcome['description']
                                line = outcome.get('point')
                                price = outcome['price']
                                
                                # Logic: Alert if a player is a heavy favorite (-140+) to hit their line
                                if price <= -140:
                                    m_id = f"{player}_{prop}_{line}"
                                    if m_id not in cache:
                                        msg = (f"🏀 **NBA PROP EDGE**\n"
                                               f"Player: **{player}**\n"
                                               f"Prop: {prop.replace('player_', '').capitalize()}\n"
                                               f"Line: {line}\n"
                                               f"Odds: {price} (High Confidence ✅)")
                                        send_alert(msg)
                                        cache[m_id] = time.time()
        except:
            continue

    # --- ESPORTS SCANNER (CS2/LoL) ---
    esports = {'cs2': 'csgo_esl', 'lol': 'leagueoflegends_lck'}
    for title, slug in esports.items():
        url = f"https://api.the-odds-api.com{slug}/odds/"
        try:
            res = requests.get(url, params={'apiKey': ODDS_API_KEY, 'regions': 'us', 'markets': 'h2h'}, timeout=15)
            if res.status_code == 200:
                for match in res.json():
                    # Logic: Standard game winner alerts
                    pass
        except: pass

    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

if __name__ == "__main__":
    print("--- 24/7 NBA & ESPORTS ENGINE ONLINE ---")
    run_dfs_engine()
