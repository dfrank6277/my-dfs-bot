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
            data = response.json()
            
            # CASE 1: Successful List of Games
            if isinstance(data, list):
                print(f"✅ SUCCESS: Found {len(data)} games for {sport_name}")
                for game in data:
                    home = game.get('home_team', 'Unknown')
                    away = game.get('away_team', 'Unknown')
                    msg = f"🏆 **MATCH FOUND**\n{away} vs {home} ({sport_name})"
                    send_discord_alert(msg)
            
            # CASE 2: Error Message (Returned as a Dictionary)
            elif isinstance(data, dict):
                error_msg = data.get('message', 'Unknown Error')
                error_code = data.get('error_code', 'No Code')
                print(f"❌ API ERROR for {sport_name}: {error_code} - {error_msg}")
                # This will tell you if your API Key is actually the problem
                if "apiKey" in error_msg or "key" in error_msg:
                    print("⚠️ CHECK: Your ODDS_API_KEY in GitHub Secrets may be incorrect.")

        except Exception as e:
            print(f"❌ Processing Error for {sport_name}: {e}")

if __name__ == "__main__":
    print("--- 24/7 BOT STARTING ---")
    run_val_bot()
