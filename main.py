import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_alert(message):
    if not WEBHOOK: return
    requests.post(WEBHOOK, json={"content": message}, timeout=10)

def run_val_bot():
    # These are the exact keys from your list!
    sports_to_scan = [
        'basketball_nba', 
        'baseball_mlb', 
        'icehockey_nhl',
        'soccer_epl',
        'soccer_usa_mls',
        'americanfootball_nfl'
    ]
    
    for sport in sports_to_scan:
        print(f"Scanning {sport}...")
        
        # DEFINITIVE URL FIX: Manually built to prevent mashing
        url = f"https://api.the-odds-api.com{sport}/odds/"
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        
        try:
            res = requests.get(url, params=params, timeout=15)
            if res.status_code == 200:
                data = res.json()
                print(f"✅ SUCCESS: Found {len(data)} games for {sport}")
                for game in data:
                    msg = f"🏆 **{sport.upper()} MATCH**\n{game['away_team']} @ {game['home_team']}"
                    send_alert(msg)
            else:
                print(f"❌ API Error {res.status_code} for {sport}")
        except Exception as e:
            print(f"❌ Connection Error for {sport}: {e}")

if __name__ == "__main__":
    send_alert("🚀 **Universal Bot Online** - Scanning NBA, MLB, NHL, and Soccer...")
    run_val_bot()
                print(f"❌ API Rejected Key. Message: {data.get('message')}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    run_dfs_engine()
