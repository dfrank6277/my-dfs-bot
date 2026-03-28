import requests
import os
import json

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_discord_alert(message):
    if not DISCORD_WEBHOOK: return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_val_bot():
    targets = {
        'CSGO': 'https://api.the-odds-api.com',
        'LOL': 'https://api.the-odds-api.com',
        'DOTA2': 'https://api.the-odds-api.com'
    }
    
    for sport_name, full_url in targets.items():
        print(f"Scanning {sport_name}...")
        
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        
        try:
            response = requests.get(full_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                # Ensure data is a list before looping
                if isinstance(data, list):
                    print(f"✅ SUCCESS: Found {len(data)} games for {sport_name}")
                    for game in data:
                        # Extract names safely
                        home = game.get('home_team', 'Unknown Home')
                        away = game.get('away_team', 'Unknown Away')
                        msg = f"🏆 **MATCH FOUND**\n{away} vs {home} ({sport_name})"
                        send_discord_alert(msg)
                else:
                    print(f"⚠️ Unexpected data format for {sport_name}")
            else:
                print(f"❌ API Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ Processing Error for {sport_name}: {e}")

if __name__ == "__main__":
    print("--- 24/7 BOT STARTING ---")
    run_val_bot()
