import requests
import os
import json

# --- CONFIGURATION (GitHub Secrets) ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_alert(message):
    if not DISCORD_WEBHOOK: return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_dfs_engine():
    # Official sport keys
    sports = ['basketball_nba', 'soccer_usa_mls', 'baseball_mlb']
    
    for sport in sports:
        print(f"Scanning {sport}...")
        
        # --- THE ULTIMATE URL FIX ---
        # We use a hard-coded base and add the sport and /odds/ manually
        base_url = "https://api.the-odds-api.com"
        full_url = base_url + sport + "/odds/"
        
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        
        try:
            # We call the full_url we just built manually
            response = requests.get(full_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Found {len(data)} games for {sport}")
                for game in data:
                    msg = f"🏆 **{sport.upper()} MATCH**\n{game['away_team']} @ {game['home_team']}"
                    send_alert(msg)
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            # This will now show the EXACT URL it tried to visit in the logs
            print(f"❌ Connection Error for {sport}. Tried to visit: {full_url}")
            print(f"Error Details: {e}")

if __name__ == "__main__":
    print("--- OFFICIAL DFS ENGINE ONLINE ---")
    run_dfs_engine()
