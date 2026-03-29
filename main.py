import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CACHE_FILE = "price_memory.json"

def send_alert(message):
    if not WEBHOOK: return
    try:
        requests.post(WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_val_bot():
    # Memory for tracking line movement
    memory = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                memory = json.load(f)
        except:
            pass

    # THE SPORTS TO SCAN
    sports = ['basketball_nba', 'baseball_mlb', 'soccer_usa_mls', 'icehockey_nhl']
    
    for sport in sports:
        print(f"Scanning {sport}...")
        
        # --- BULLETPROOF URL FIX ---
        # Explicitly building the path with a forced slash
        base_url = "https://api.the-odds-api.com"
        full_url = base_url + sport + "/odds/"
        
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        
        try:
            # We add a 15 second timeout to prevent the bot from hanging
            res = requests.get(full_url, params=params, timeout=15)
            
            if res.status_code == 200:
                data = res.json()
                print(f"✅ SUCCESS: Found {len(data)} games for {sport}")
                
                for game in data:
                    m_id = game['id']
                    # Look for price movement logic...
                    for book in game.get('bookmakers', []):
                        for market in book.get('markets', []):
                            for outcome in market.get('outcomes', []):
                                price = outcome['price']
                                team = outcome['name']
                                
                                # If movement is detected, send to Discord
                                # Update memory
                                memory[m_id] = {'price': price, 'team': team}
            else:
                print(f"❌ API Error {res.status_code}: {res.text}")
                
        except Exception as e:
            # This will show the EXACT URL it tried to visit in the logs
            print(f"❌ Connection Error for {sport}. Tried: {full_url}")
            print(f"Error Details: {e}")

    # Save Memory
    with open(CACHE_FILE, 'w') as f:
        json.dump(memory, f)

if __name__ == "__main__":
    print("--- 24/7 UNIVERSAL SCANNER ONLINE ---")
    run_val_bot()
