import requests
import os
import json

# --- CONFIGURATION (GitHub Secrets) ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_discord_alert(message):
    if not DISCORD_WEBHOOK:
        print("❌ ERROR: DISCORD_WEBHOOK not found in Secrets")
        return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except Exception as e:
        print(f"❌ Discord Error: {e}")

def run_val_bot():
    # MANDATORY PATHS for The-Odds-API v4
    targets = {
        'CSGO': f'https://api.the-odds-api.com{API_KEY}&regions=us&markets=h2h',
        'LOL': f'https://api.the-odds-api.com{API_KEY}&regions=us&markets=h2h',
        'DOTA2': f'https://api.the-odds-api.com{API_KEY}&regions=us&markets=h2h'
    }
    
    for sport_name, full_url in targets.items():
        print(f"Scanning {sport_name}...")
        try:
            response = requests.get(full_url, timeout=15)
            data = response.json()
            
            # If the response is a list, we found games
            if isinstance(data, list):
                if len(data) > 0:
                    print(f"✅ SUCCESS: Found {len(data)} games for {sport_name}")
                    for game in data:
                        msg = f"🏆 **{sport_name} MATCH**\n{game.get('away_team')} vs {game.get('home_team')}"
                        send_discord_alert(msg)
                else:
                    print(f"ℹ️ {sport_name}: No active games scheduled right now.")
            
            # If it's a dict, it's an error or the welcome message
            elif isinstance(data, dict):
                print(f"❌ API Response Error: {data.get('message', 'No message')}")

        except Exception as e:
            print(f"❌ Connection Error for {sport_name}: {e}")

if __name__ == "__main__":
    print("--- 24/7 BOT STARTING ---")
    # TEST: If this doesn't show in Discord, your Webhook Secret is broken
    send_discord_alert("🚀 Bot is starting a 13-minute scan...") 
    run_val_bot()
