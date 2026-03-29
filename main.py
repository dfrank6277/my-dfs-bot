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
    if not DISCORD_WEBHOOK: return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_dfs_engine():
    # Load Cache
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
    except:
        cache = {}

    all_found_plays = []
    # Updated slugs
    esports_titles = {'cs2': 'csgo_esl', 'lol': 'leagueoflegends_lck'}
    
    for title, odds_slug in esports_titles.items():
        print(f"Scanning {title.upper()}...")
        
        # --- BULLETPROOF URL FIX: Explicit slashes ---
        url = f"https://api.the-odds-api.com{odds_slug}/odds/"
        
        params = {
            'apiKey': ODDS_API_KEY,
            'regions': 'us',
            'markets': 'h2h'
        }
        
        try:
            # We add a 15 second timeout to prevent hanging
            res = requests.get(url, params=params, timeout=15)
            
            if res.status_code == 200:
                data = res.json()
                print(f"✅ SUCCESS: Found {len(data)} games for {odds_slug}")
                for match in data:
                    # Find all bookie prices
                    prices = [o['price'] for b in match.get('bookmakers', []) 
                             for m in b.get('markets', []) for o in m.get('outcomes', [])]
                    
                    if len(prices) >= 2:
                        avg = sum(prices) / len(prices)
                        all_found_plays.append({
                            'msg': f"🏆 **TOP {title.upper()} PLAY**\n{match['away_team']} vs {match['home_team']}\nAvg Odds: {round(avg, 1)}",
                            'odds': avg,
                            'id': match['id']
                        })
            else:
                print(f"❌ API Error {res.status_code}: {res.text}")
                
        except Exception as e:
            print(f"❌ Connection Error for {odds_slug}: {e}")

    # Sort by best odds and post top 3
    all_found_plays.sort(key=lambda x: x['odds']) 
    for play in all_found_plays[:3]:
        if play['id'] not in cache:
            send_alert(play['msg'])
            cache[play['id']] = time.time()

    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

if __name__ == "__main__":
    print("--- 24/7 BOT STARTING ---")
    send_alert("🤖 **DFS Bot is Online** - Scanning for plays...")
    run_dfs_engine()
