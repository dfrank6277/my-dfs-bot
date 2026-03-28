import requests
import os
import json
import time

# --- CONFIGURATION (Uses GitHub Secrets for Security) ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
THRESHOLD = 0.60  # The "Brain" - Bot picks anything with >60% win probability

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
    # List of sports to analyze (CSGO, LoL, Dota, NBA, etc.)
    sports = ['basketball_nba', 'csgo', 'leagueoflegends', 'dota2']
    
    for sport in sports:
        print(f"Checking {sport}...")
        url = f"https://api.the-odds-api.com{sport}/odds/"
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h', # Will upgrade to 'player_props' later
            'oddsFormat': 'american'
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            for game in data:
                # --- THIS IS THE 'BRAIN' SECTION ---
                # Example: If a team/player is a heavy favorite (-250 or better)
                # it flags it for a DFS 'Over' play.
                home_team = game.get('home_team')
                away_team = game.get('away_team')
                
                # Logic: Find high-probability plays
                # (For now, we alert the game start. We will refine the math next.)
                alert_msg = f"Match Found: {away_team} vs {home_team} in {sport.upper()}"
                
                # SEND TO DISCORD
                send_discord_alert(alert_msg)
                
                # LOG TO 'MEMORY' (Print for GitHub Logs)
                print(f"Logged Play: {alert_msg}")
        else:
            print(f"Failed to fetch {sport}: {response.status_code}")

if __name__ == "__main__":
    print("Starting DFS Optimizer Bot...")
    run_val_bot()

