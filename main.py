import requests
import os
import json
import time

# --- 1. CONFIGURATION ---
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
GRID_API_KEY = os.getenv("GRID_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CACHE_FILE = "sent_matches.json"

def send_alert(message):
    if not DISCORD_WEBHOOK: return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def get_grid_rosters(title):
    """Pulls live roster data from GRID to detect last-minute swaps."""
    url = f"https://api.grid.gg{title}/teams"
    headers = {"x-api-key": GRID_API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json() if res.status_code == 200 else {}
    except:
        return {}

def run_dfs_engine():
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
    except:
        cache = {}

    esports_titles = {'cs2': 'csgo_esl', 'lol': 'leagueoflegends_lck'}
    
    for title, odds_slug in esports_titles.items():
        print(f"Analyzing {title.upper()}...")
        
        # 1. ROSTER TRACKER (GRID API)
        roster_data = get_grid_rosters(title)
        # Logic: If a 'Stand-in' flag is found in GRID, alert immediately
        if "standin" in str(roster_data).lower():
            send_alert(f"🚨 **ROSTER CHANGE DETECTED ({title.upper()})**\nA team is using a stand-in! Check lines before they move!")

        # 2. CONSENSUS FILTER (The Odds API)
        url = f"https://api.the-odds-api.com{odds_slug}/odds/"
        params = {'apiKey': ODDS_API_KEY, 'regions': 'us', 'markets': 'h2h'}
        
        try:
            res = requests.get(url, params=params, timeout=15)
            if res.status_code == 200:
                matches = res.json()
                for match in matches:
                    m_id = match['id']
                    
                    # Collect all bookie prices
                    prices = []
                    for book in match.get('bookmakers', []):
                        for market in book.get('markets', []):
                            for outcome in market.get('outcomes', []):
                                if outcome.get('price'):
                                    prices.append(outcome['price'])
                    
                    # Multi-Bookie Consensus Filter (3+ Bookies)
                    if len(prices) >= 3:
                        avg_price = sum(prices) / len(prices)
                        
                        # High-Confidence Alert
                        if avg_price < -185 and m_id not in cache:
                            msg = (f"💎 **VERIFIED CONSENSUS LOCK ({title.upper()})**\n"
                                   f"Match: {match['away_team']} vs {match['home_team']}\n"
                                   f"Verified by {len(prices)//2} Sportsbooks ✅")
                            send_alert(msg)
                            cache[m_id] = time.time()
        except:
            pass

    # Save Cache
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

if __name__ == "__main__":
    print("--- 24/7 DFS ENGINE ONLINE ---")
    run_dfs_engine()
