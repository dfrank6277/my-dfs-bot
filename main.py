import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_alert(message):
    if not DISCORD_WEBHOOK:
        return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_val_bot():
    if not API_KEY:
        print("❌ CRITICAL ERROR: API_KEY is empty in GitHub Secrets!")
        return

    # Using the official sport keys from your list
    sports = ['basketball_nba', 'baseball_mlb', 'soccer_epl', 'icehockey_nhl']
    
    for sport in sports:
        print(f"Scanning {sport}...")
        
        # DEFINITIVE URL FIX: Prevents mashing errors
        url = f"https://api.the-odds-api.com{sport}/odds/"
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        
        try:
            res = requests.get(url, params=params, timeout=15)
            data = res.json()
            
            if isinstance(data, list):
                if len(data) > 0:
                    print(f"✅ SUCCESS: Found {len(data)} games for {sport}")
                    for game in data:
                        msg = f"🏆 **{sport.upper()} MATCH**\n{game.get('away_team')} @ {game.get('home_team')}"
                        send_alert(msg)
                else:
                    print(f"ℹ️ No active games for {sport} right now.")
            else:
                # FIXED INDENTATION HERE
                print(f"❌ API Rejected Key. Message: {data.get('message', 'Unknown Error')}")
        except Exception as e:
            print(f"❌ Connection Error for {sport}: {e}")

if __name__ == "__main__":
    print("--- 24/7 UNIVERSAL BOT ONLINE ---")
    send_alert("🚀 **Universal Bot Online** - Scanning NBA, MLB, NHL, and Soccer...")
    run_val_bot()
