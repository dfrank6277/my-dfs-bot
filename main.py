import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CACHE_FILE = "sent_matches.json"

# All major DFS props
NBA_PROPS = ['player_points', 'player_rebounds', 'player_assists', 'player_threepointers']

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

    sports = ['basketball_nba', 'americanfootball_nfl', 'baseball_mlb']
    
    for sport in sports:
        for prop in NBA_PROPS:
            # FIXED URL: Absolute path to prevent mashing
            url = f"https://api.the-odds-api.com{sport}/odds/"
            params = {
                'apiKey': API_KEY,
                'regions': 'us',
                'markets': prop,
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

                                    # VEGAS EDGE: Alert if price is -145 or better
                                    if price and price <= -145:
                                        m_id = f"{player}_{prop}_{line}"
                                        if m_id not in cache:
                                            # Deep Links
                                            p_query = player.replace(" ", "%20")
                                            pp_link = f"https://app.prizepicks.com{p_query}"
                                            ud_link = f"https://underdogfantasy.com{p_query}"

                                            msg = (f"🎯 **DFS PROP ALERT ({sport.upper()})**\n"
                                                   f"Player: **{player}**\n"
                                                   f"Prop: {prop.replace('player_', '').capitalize()} | Line: {line}\n"
                                                   f"Odds: {price} (Vegas Lock ✅)\n\n"
                                                   f"📲 [PrizePicks]({pp_link}) | [Underdog]({ud_link})")
                                            send_alert(msg)
                                            cache[m_id] = time.time()
            except:
                continue

    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

if __name__ == "__main__":
    send_alert("🚀 **DFS MASTER BOT ONLINE** - Scanning NBA, NFL, and MLB Props...")
    run_dfs_engine()
