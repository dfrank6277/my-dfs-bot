import requests
import os
from datetime import datetime

# --- CONFIG ---
API_KEY = os.getenv("ODDS_API_KEY")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
# Use the exact keys from The Odds API docs
SPORTS = ['basketball_nba', 'esports_csgo', 'baseball_mlb', 'icehockey_nhl']
 
REGIONS = 'us' # Change to 'eu' if scanning European CS2 books
MARKETS = 'h2h' # Moneyline

def run_val_bot():
    for sport in SPORTS:
        # 1. Pull the data
        url = f"https://api.the-odds-api.com/{sport}/odds/"
        params = {
            'apiKey': API_KEY,
            'regions': REGIONS,
            'markets': MARKETS,
            'oddsFormat': 'american'
        }
        
        res = requests.get(url, params=params)
        data = res.json()

        # Debug: This will show in your console if the API is actually sending data
        if not data:
            print(f"Empty data for {sport}. No upcoming matches found.")
            continue

        for match in data:
            home_team = match['home_team']
            away_team = match['away_team']
            
            for bookie in match['bookmakers']:
                for market in bookie['markets']:
                    for outcome in market['outcomes']:
                        price = outcome['price']
                        name = outcome['name']
                        
                        # LOGIC: Signal if we find a 'Value' price
                        # Example: If a team is heavily favored (-150 or better)
                        if price <= -145:
                            msg = {
                                "content": f"🎯 **VALUE ALERT** | {sport.upper()}\n"
                                           f"⚔️ **Match:** {away_team} @ {home_team}\n"
                                           f"👤 **Bet:** {name} ({price})\n"
                                           f"🏦 **Bookie:** {bookie['title']}\n"
                                           f"----------------------------"
                            }
                            requests.post(WEBHOOK_URL, json=msg)

if __name__ == "__main__":
    run_val_bot()
