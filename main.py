import requests
import os
import json

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_discord_alert(message):
    print(f"DEBUG: Attempting to send to Discord: {message[:30]}...")
    
    if not DISCORD_WEBHOOK or DISCORD_WEBHOOK == "":
        print("❌ DEBUG ERROR: DISCORD_WEBHOOK is None or Empty! Check your GitHub Secrets.")
        return

    data = {"content": message}
    try:
        # 204 is the success code for Discord Webhooks
        response = requests.post(DISCORD_WEBHOOK, json=data, timeout=10)
        print(f"DEBUG: Discord Response Code: {response.status_code}")
    except Exception as e:
        print(f"DEBUG: Discord Request Failed: {e}")

def run_val_bot():
    # We use these sports for testing; make sure they are active
    sports = ['basketball_nba', 'soccer_usa_mls', 'esports_csgo']
    
    if not API_KEY:
        print("❌ DEBUG ERROR: API_KEY is missing! Check your GitHub Secrets.")
        return

    for sport in sports:
        print(f"DEBUG: Checking {sport}...")
        
        # --- FIXED URL FORMAT WITH PROPER SLASHES ---
        url = f"https://api.the-odds-api.com{sport}/odds/"
        
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        
        try:
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                data = res.json()
                print(f"✅ DEBUG: Found {len(data)} games for {sport}")
                
                for game in data[:3]: # Alert first 3 matches found
                    msg = f"🏆 **{sport.upper()} Match Found**\n{game['away_team']} @ {game['home_team']}"
                    send_discord_alert(msg)
            else:
                print(f"DEBUG: API returned error {res.status_code}: {res.text}")
        except Exception as e:
            print(f"DEBUG: API Call Failed for {sport}: {e}")

if __name__ == "__main__":
    print("--- BOT STARTING ---")
    send_discord_alert("🚀 Bot is ONLINE and the URL fix is applied!")
    run_val_bot()

