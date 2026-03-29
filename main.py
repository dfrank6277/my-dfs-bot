import requests
import os
from urllib.parse import urljoin

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
    # UPDATED KEYS FROM YOUR LIST
    sports = [
        'basketball_nba', 
        'baseball_mlb', 
        'americanfootball_nfl', 
        'soccer_usa_mls'
    ]
    
    # THE BULLETPROOF BASE
    base_url = "https://api.the-odds-api.com"
    
    for sport_key in sports:
        print(f"Scanning {sport_key}...")
        
        # urljoin forces the slash between .com and the sport key
        # Result: https://api.the-odds-api.combasketball_nba/odds/
        temp_url = urljoin(base_url, f"{sport_key}/")
        full_url = urljoin(temp_url, "odds/")
        
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
                    msg = f"🏆 **MATCH FOUND**\n{game.get('away_team')} vs {game.get('home_team')} ({sport_key.upper()})"
                    send_alert(msg)
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection Error for {sport_key}. Tried: {full_url}")
            print(f"Error Details: {e}")

if __name__ == "__main__":
    print("--- OFFICIAL DFS ENGINE ONLINE ---")
    run_dfs_engine()
