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
    # OFFICIAL SLUGS FOR THE-ODDS-API
    sports = [
        'csgo_esl',              # CS:GO / CS2 (ESL)
        'leagueoflegends_lck',   # LoL (Korea)
        'leagueoflegends_lpl',   # LoL (China)
        'dota2_epic',            # Dota 2
        'cod_league'             # Call of Duty League
    ]
    
    for game_type in sports:
        print(f"Scanning {game_type}...")
        
        # We manually build the URL to avoid the slash error
        domain = "https://api.the-odds-api.com"
        path = "/v4/sports/"
        endpoint = "/odds/"
        full_url = domain + path + game_type + endpoint
        
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
                # If the list is empty, it just means no games are live right now
                print(f"✅ SUCCESS: Found {len(data)} games for {game_type}")
                
                for game in data:
                    home = game.get('home_team')
                    away = game.get('away_team')
                    msg = f"🏆 **MATCH DETECTED**\n{away} vs {home} ({game_type.upper()})"
                    send_discord_alert(msg)
            else:
                # This will tell us if your API Key is the problem or the Slug
                print(f"❌ API Error {response.status_code} for {game_type}. Msg: {response.text}")

                
        except Exception as e:
            print(f"❌ Connection Error for {game_type}: {e}")

if __name__ == "__main__":
    print("--- BOT STARTING ---")
    run_val_bot()

