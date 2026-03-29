import requests
import os
import json

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_alert(message):
    if not DISCORD_WEBHOOK: return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_dfs_engine():
    # Official keys from your list
    sports = ['basketball_nba', 'baseball_mlb', 'americanfootball_nfl', 'soccer_usa_mls']
    
    for sport_key in sports:
        print(f"Scanning {sport_key}...")
        
        # --- THE BULLETPROOF URL FIX ---
        # We hard-code the /v4/sports/ path so it can NEVER be stripped
        full_url = f"https://api.the-odds-api.com{sport_key}/odds/"
        
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        
        try:
            print(f"DEBUG: Visiting {full_url}")
            response = requests.get(full_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Found {len(data)} games for {sport_key}")
                for game in data:
                    home = game.get('home_team')
                    away = game.get('away_team')
                    msg = f"🏆 **MATCH FOUND**\n{away} vs {home} ({sport_key.upper()})"
                    send_alert(msg)
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection Error for {sport_key}: {e}")

if __name__ == "__main__":
    print("--- 24/7 DFS ENGINE ONLINE ---")
    run_dfs_engine()
