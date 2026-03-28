import requests
import os
import json

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_discord_alert(message):
    print(f"DEBUG: Attempting to send to Discord: {message[:20]}...")
    
    if not DISCORD_WEBHOOK:
        print("DEBUG: DISCORD_WEBHOOK is None or Empty!")
        return

    data = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK, json=data, timeout=10)
        print(f"DEBUG: Discord Response Code: {response.status_code}")
    except Exception as e:
        print(f"DEBUG: Discord Request Failed: {e}")

def run_val_bot():
    # We use 'upcoming' to ensure we find games even if none are live
    sports = ['basketball_nba', 'soccer_usa_mls', 'americanfootball_nfl']
    
    if not API_KEY:
        print("DEBUG: API_KEY is missing!")
        return

    for sport in sports:
        print(f"DEBUG: Checking {sport}...")
        url = f"https://api.the-odds-api.com{sport}/odds/"
        params = {'apiKey': API_KEY, 'regions': 'us', 'markets': 'h2h'}
        
        try:
            res = requests.get(url, params=params)
            data = res.json()
            print(f"DEBUG: Found {len(data)} games for {sport}")
            
            for game in data[:2]: # Only alert first 2 to avoid spam
                msg = f"MATCH: {game['away_team']} @ {game['home_team']}"
                send_discord_alert(msg)
        except Exception as e:
            print(f"DEBUG: API Call Failed for {sport}: {e}")

if __name__ == "__main__":
    print("--- BOT STARTING ---")
    send_discord_alert("🔔 TEST: Bot is communicating with Discord!")
    run_val_bot()

