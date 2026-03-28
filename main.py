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
    # List of sports to scan
    sports = ['esports_csgo', 'esports_lol']
    
    for game_type in sports:
        print(f"Scanning {game_type}...")
        
        # --- THE BULLETPROOF URL FIX ---
        # Note the explicit /v4/sports/ and the trailing /odds/
        base_url = "https://api.the-odds-api.com"
        full_url = base_url + game_type + "/odds/"
        
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        
        try:
            # We use the full_url we just built manually
            response = requests.get(full_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Found {len(data)} games for {game_type}")
                
                for game in data:
                    home = game.get('home_team')
                    away = game.get('away_team')
                    msg = f"🏆 **MATCH DETECTED**\n{away} vs {home} ({game_type.upper()})"
                    send_discord_alert(msg)
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            # This will now show the EXACT URL it tried to visit
            print(f"❌ Connection Error for {game_type}. Tried to visit: {full_url}")
            print(f"Error Details: {e}")

if __name__ == "__main__":
    print("--- BOT STARTING ---")
    run_val_bot()
