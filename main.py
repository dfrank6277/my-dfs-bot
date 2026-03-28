import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CACHE_FILE = "sent_matches.json"
SENSITIVITY = 30 # How many 'points' a line must move to trigger (e.g. -110 to -140)

def get_sent_cache():
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_sent_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def send_discord_alert(message):
    if not DISCORD_WEBHOOK: return
    requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)

def run_val_bot():
    cache = get_sent_cache()
    sports = ['basketball_nba', 'esports_csgo', 'leagueoflegends']
    
    for sport in sports:
        url = f"https://api.the-odds-api.com{sport}/odds/"
        params = {'apiKey': API_KEY, 'regions': 'us', 'markets': 'h2h'}
        
        try:
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                data = res.json()
                for game in data:
                    match_id = game['id']
                    # Get the current odds for the Favorite
                    current_odds = game['bookmakers'][0]['markets'][0]['outcomes'][0]['price']
                    
                    # SMART MONEY LOGIC
                    if match_id in cache:
                        prev_odds = cache[match_id]['price']
                        
                        # Calculate movement (If odds drop from -110 to -150, that's 40 points)
                        movement = prev_odds - current_odds
                        
                        if movement >= SENSITIVITY:
                            msg = f"🚨 **SMART MONEY ALERT** 🚨\n{game['away_team']} @ {game['home_team']}\nLine Moved: {prev_odds} ➡️ {current_odds}\n*Heavy action detected!*"
                            send_discord_alert(msg)
                    
                    # Update cache with latest price
                    cache[match_id] = {'price': current_odds, 'time': time.time()}
                    
        except Exception as e:
            print(f"Error: {e}")
    
    save_sent_cache(cache)

if __name__ == "__main__":
    run_val_bot()
