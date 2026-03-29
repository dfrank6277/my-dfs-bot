import requests
import os
import json
import time

# --- 1. CONFIGURATION (GitHub Secrets) ---
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
GRID_API_KEY = os.getenv("GRID_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CACHE_FILE = "sent_matches.json"

def send_alert(message):
    if not DISCORD_WEBHOOK:
        print("❌ Webhook missing")
        return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except Exception as e:
        print(f"❌ Discord Error: {e}")

def get_grid_projections(title):
    """Pulls eSports projections from GRID."""
    url = f"https://api.grid.gg{title}/projections"
    headers = {"x-api-key": GRID_API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json() if res.status_code == 200 else {}
    except:
        return {}

def run_dfs_engine():
    # Load Cache to prevent duplicate pings
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
    except:
        cache = {}

    all_found_plays = []
    # Updated slugs for maximum compatibility
    esports_titles = {'cs2': 'csgo_esl', 'lol': 'leagueoflegends_lck'}
    
    for title, odds_slug in esports_titles.items():
        print(f"Scanning {title.upper()}...")
        
        # Pull from GRID and The Odds API
        grid_data = get_grid_projections(title)
        url = f"https://api.the-odds-api.com{odds_slug}/odds/"
        params = {'apiKey': ODDS_API_KEY, 'regions': 'us', 'markets': 'h2h'}
        
        try:
            res = requests.get(url, params=params, timeout=15)
            if res.status_code == 200:
                matches = res.json()
                for match in matches:
                    m_id = match['id']
                    
                    # --- CONSENSUS LOGIC: Calculate Average Odds ---
                    prices = []
                    for book in match.get('bookmakers', []):
                        for market in book.get('markets', []):
                            for outcome in market.get('outcomes', []):
                                if outcome.get('price'):
                                    prices.append(outcome['price'])
                    
                    if len(prices) >= 2:
                        avg_odds = sum(prices) / len(prices)
                        all_found_plays.append({
                            'msg': f"🔥 **TOP {title.upper()} PLAY**\nMatch: {match['away_team']} @ {match['home_team']}\nAvg Odds: {round(avg_odds, 1)}\n*Confidence: High*",
                            'odds': avg_odds,
                            'id': m_id
                        })
            else:
                print(f"API Error {res.status_code} for {odds_slug}")
        except Exception as e:
            print(f"Error: {e}")

    # --- TEST MODE: Sort by best odds and post top 3 ---
    all_found_plays.sort(key=lambda x: x['odds']) 
    
    for play in all_found_plays[:3]:
        if play['id'] not in cache:
            send_alert(play['msg'])
            cache[play['id']] = time.time()

    # Save updated cache
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

if __name__ == "__main__":
    print("--- 24/7 DFS ENGINE STARTING (TEST MODE) ---")
    # Immediate Heartbeat to Discord
    send_alert("🤖 **DFS Bot is Online** - Starting the 13-minute scan for the best value plays.")
    run_dfs_engine()
