import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CACHE_FILE = "sent_matches.json"

def send_alert(message):
    if not WEBHOOK: return
    requests.post(WEBHOOK, json={"content": message}, timeout=10)

def run_val_bot():
    # Targets for NBA and top eSports leagues
    targets = {
        'NBA': f'https://api.the-odds-api.com{API_KEY}&regions=us&markets=h2h',
        'CS2': f'https://api.the-odds-api.com{API_KEY}&regions=us&markets=h2h',
        'LoL': f'https://api.the-odds-api.com{API_KEY}&regions=us&markets=h2h'
    }
    
    for sport, url in targets.items():
        print(f"Scanning {sport}...")
        try:
            res = requests.get(url, timeout=15)
            data = res.json()
            
            if isinstance(data, list) and len(data) > 0:
                for game in data:
                    home = game.get('home_team')
                    away = game.get('away_team')
                    
                    # LOGIC: If a match is found, send a high-visibility alert
                    msg = f"🏆 **NEW {sport} MATCH DETECTED**\n🔥 {away} @ {home}\n*Check your DFS apps for value lines!*"
                    send_alert(msg)
            else:
                print(f"ℹ️ {sport}: No active games found right now.")
        except Exception as e:
            print(f"❌ Error scanning {sport}: {e}")

if __name__ == "__main__":
    send_alert("🤖 **DFS BOT ONLINE** - Starting 13-minute scan...")
    run_val_bot()
