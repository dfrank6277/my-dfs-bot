import requests
import os
import json

# --- CONFIGURATION (GitHub Secrets) ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_alert(message):
    if not DISCORD_WEBHOOK: return
    requests.post(DISCORD_WEBHOOK, json={"content": message})

def run_dfs_engine():
    # This matches the 'Step 2' sport keys from the official samples
    sports = ['basketball_nba', 'soccer_usa_mls', 'baseball_mlb']
    
    for sport in sports:
        # OFFICIAL URL STRUCTURE from ://github.com
        url = f'https://api.the-odds-api.com{sport}/odds'
        
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Found {len(data)} games for {sport}")
                for game in data:
                    # Logic to find your "Edge"
                    msg = f"🏆 **{sport.upper()} MATCH**\n{game['away_team']} @ {game['home_team']}"
                    send_alert(msg)
            else:
                # This catches the 'INVALID_KEY' error specifically
                print(f"❌ API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    run_dfs_engine()
