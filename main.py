import requests
import os
import json
from urllib.parse import urljoin

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
    # Official slugs for The-Odds-API
    sports = ['csgo_esl', 'leagueoflegends_lck', 'dota2_epic']
    
    # THE BULLETPROOF BASE
    base_url = "https://api.the-odds-api.com"
    
    for game_type in sports:
        print(f"Scanning {game_type}...")
        
        # This library function FORCES the slashes to be correct
        # Result: https://api.the-odds-api.comcsgo_esl/odds/
        temp_url = urljoin(base_url, f"{game_type}/")
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
                print(f"✅ SUCCESS: Found {len(data)} games for {game_type}")
                
                for game in data:
                    home = game.get('home_team')
                    away = game.get('away_team')
                    msg = f"🏆 **MATCH FOUND**\n{away} vs {home} ({game_type.upper()})"
                    send_discord_alert(msg)
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection Error for {game_type}: {e}")

if __name__ == "__main__":
    print("--- BOT STARTING ---")
    run_val_bot()
