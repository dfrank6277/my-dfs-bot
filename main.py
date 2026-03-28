import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_discord_alert(message):
    """Sends the found play to your Discord channel."""
    if not DISCORD_WEBHOOK:
        print("Discord Webhook not found in Secrets.")
        return
        
    data = {
        "content": f"🚀 **DFS BOT ALERT** 🚀\n{message}",
        "username": "DFS Optimizer Pro"
    }
    try:
        requests.post(DISCORD_WEBHOOK, json=data, timeout=10)
    except Exception as e:
        print(f"Discord Error: {e}")

def run_val_bot():
    """Main logic to find matches in Sports and eSports."""
    sports = ['basketball_nba', 'csgo', 'leagueoflegends', 'dota2']
    
    for sport in sports:
        print(f"Checking {sport}...")
        url = f"https://api.the-odds-api.com{sport}/odds/"
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h', 
            'oddsFormat': 'american'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for game in data:
                    home_team = game.get('home_team')
                    away_team = game.get('away_team')
                    
                    alert_msg = f"Match Found: {away_team} vs {home_team} in {sport.upper()}"
                    send_discord_alert(alert_msg)
                    print(f"Logged Play: {alert_msg}")
            else:
                print(f"API Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Connection Error for {sport}: {e}")

if __name__ == "__main__":
    print("Starting DFS Optimizer Bot...")
    
    # --- ADD THIS LINE HERE ---
    send_discord_alert("Bot is ONLINE and scanning for plays! 🔍")
    
    run_val_bot()

