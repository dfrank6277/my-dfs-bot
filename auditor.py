import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CACHE_FILE = "sent_matches.json"

# Major NBA/NFL Props
PROP_MARKETS = 'player_points,player_pass_tds,player_assists,player_rebounds'

def send_alert(message):
    if not WEBHOOK: return
    try:
        requests.post(WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_dfs_engine():
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
    except:
        cache = {}

    # Official Sport Keys from your list
    sports = ['basketball_nba', 'americanfootball_nfl', 'baseball_mlb']
    
    for sport in sports:
        print(f"Scanning {sport}...")
        # DEFINITIVE URL FIX: Absolute path with forced slashes
        url = f"https://api.the-odds-api.com{sport}/odds/"
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': PROP_MARKETS,
            'oddsFormat': 'american',
            'bookmakers': 'fanduel,draftkings'
        }
        
        try:
            res = requests.get(url, params=params, timeout=15)
            if res.status_code == 200:
                data = res.json()
                for game in data:
                    for book in game.get('bookmakers', []):
                        for market in book.get('markets', []):
                            for outcome in market.get('outcomes', []):
                                player = outcome.get('description', outcome['name'])
                                price = outcome.get('price')
                                line = outcome.get('point', 'N/A')
                                
                                # CONSENSUS LOGIC: Alert if Vegas favorite (-145 or better)
                                if price and price <= -145:
                                    m_id = f"{player}_{market['key']}_{line}"
                                    if m_id not in cache:
                                        msg = (f"🎯 **DFS PROP ALERT ({sport.upper()})**\n"
                                               f"Player: **{player}**\n"
                                               f"Prop: {market['key']}\n"
                                               f"Line: {line} | Odds: {price} ✅")
                                        send_alert(msg)
                                        cache[m_id] = time.time()
            else:
                print(f"❌ API Error {res.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

if __name__ == "__main__":
    send_alert("🚀 **DFS MASTER BOT ONLINE** - Scanning NBA, NFL, and MLB Props...")
    run_dfs_engine()
