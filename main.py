import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CACHE_FILE = "sent_matches.json"

def send_discord_alert(message):
    if not DISCORD_WEBHOOK: return
    requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)

def run_val_bot():
    # Targeted eSports Slugs for Map-Specific Data
    esports = ['esports_csgo', 'esports_lol', 'esports_dota2']
    
    for game_type in esports:
        print(f"Analyzing Maps for {game_type}...")
        
        # We query specifically for Map Winner markets
        url = f"https://api.the-odds-api.com{game_type}/odds/"
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h_lay,h2h_1,h2h_2', # Pulls Match, Map 1, and Map 2 odds
            'oddsFormat': 'american'
        }
        
        try:
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                data = res.json()
                for match in data:
                    match_name = f"{match['away_team']} vs {match['home_team']}"
                    
                    # LOGIC: Check for Map Discrepancies
                    # If a team is -150 to win the match, but -300 to win Map 1, 
                    # they are a "Map 1 Specialist." We alert this for DFS 'Over' plays.
                    for bookmaker in match.get('bookmakers', []):
                        for market in bookmaker.get('markets', []):
                            market_key = market['key'] # e.g., 'h2h_1' (Map 1 Winner)
                            
                            if 'h2h_' in market_key:
                                map_num = market_key.split('_')[-1]
                                favorite = min(market['outcomes'], key=lambda x: x['price'])
                                
                                # High-Confidence Map Alert
                                if favorite['price'] <= -250:
                                    alert_msg = f"🗺️ **{game_type.upper()} MAP {map_num} ALERT**\nMatch: {match_name}\nMap {map_num} Lock: **{favorite['name']}** ({favorite['price']})\n*Perfect for Map 1 Kills/Stats Overs!*"
                                    send_discord_alert(alert_msg)
            else:
                print(f"API Error {res.status_code}: {res.text}")
        except Exception as e:
            print(f"Error analyzing {game_type}: {e}")

if __name__ == "__main__":
    run_val_bot()
