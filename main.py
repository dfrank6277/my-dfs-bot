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
    # Make sure your secret name matches exactly what is in GitHub
    api_key = os.getenv("ODDS_API_KEY")
    
    if not api_key:
        print("❌ CRITICAL ERROR: ODDS_API_KEY is missing from environment secrets.")
        return

    sports = ['basketball_nba', 'esports_csgo', 'baseball_mlb', 'icehockey_nhl']
    
    for sport in sports:
        url = f"https://api.the-odds-api.com{sport}/odds/"
        params = {
            'apiKey': api_key,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        
        print(f"Checking {sport}...")
        res = requests.get(url, params=params)

        # 1. CHECK STATUS FIRST (Prevents the JSONDecodeError)
        if res.status_code != 200:
            print(f"❌ API REJECTED REQUEST ({res.status_code}): {res.text}")
            continue
            
        # 2. SAFE JSON LOADING
        try:
            data = res.json()
        except Exception:
            print(f"❌ ERROR: Received non-JSON response for {sport}")
            continue

        if not data:
            print(f"No active matches for {sport}.")
            continue

        # 3. YOUR PROCESSING LOGIC
        for match in data:
            # (Your logic for analyzing plays goes here)
            print(f"Found match: {match.get('home_team')} vs {match.get('away_team')}")

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
