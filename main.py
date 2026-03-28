import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
GRID_API_KEY = os.getenv("GRID_API_KEY")
CACHE_FILE = "sent_matches.json"

def get_sent_cache():
    """Loads the list of matches we already alerted."""
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_sent_cache(cache):
    """Saves the updated list of matches."""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def send_discord_alert(message, match_id, cache):
    """Only sends to Discord if we haven't sent this match_id recently."""
    if match_id in cache:
        print(f"Skipping duplicate match: {match_id}")
        return False
    
    if not DISCORD_WEBHOOK: return False
    
    requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    cache[match_id] = time.time() # Mark as sent
    return True

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
                    match_id = game['id'] # Unique ID from the API
                    
                    # ALERT LOGIC
                    msg = f"🔥 **{sport.upper()} PLAY**\n{game['away_team']} @ {game['home_team']}"
                    
                    # Try to send (Filter handles duplicates)
                    sent = send_discord_alert(msg, match_id, cache)
                    if sent:
                        print(f"New match alerted: {match_id}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Cleanup old matches (older than 24 hours) to keep cache small
    current_time = time.time()
    cache = {k: v for k, v in cache.items() if current_time - v < 86400}
    save_sent_cache(cache)

if __name__ == "__main__":
    run_val_bot()
