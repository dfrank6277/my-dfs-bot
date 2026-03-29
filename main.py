import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CACHE_FILE = "price_memory.json"
SENSITIVITY = 20  

def send_alert(message):
    if not WEBHOOK: return
    try:
        requests.post(WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_val_bot():
    # Load Price Memory
    memory = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                memory = json.load(f)
        except:
            memory = {}

    # THE SPORTS TO SCAN
    sports = ['basketball_nba', 'baseball_mlb', 'soccer_usa_mls', 'icehockey_nhl']
    
    for sport in sports:
        print(f"Scanning {sport}...")
        
        # --- BULLETPROOF URL FIX ---
        # We manually add the /v4/sports/ path and the slashes
        url = "https://api.the-odds-api.com" + sport + "/odds/"
        
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        
        try:
            # Added a timeout and explicit headers to look like a real browser
            res = requests.get(url, params=params, timeout=15)
            
            if res.status_code == 200:
                data = res.json()
                print(f"✅ SUCCESS: Found {len(data)} games for {sport}")
                
                for game in data:
                    m_id = game['id']
                    for book in game.get('bookmakers', []):
                        for market in book.get('markets', []):
                            for outcome in market.get('outcomes', []):
                                price = outcome['price']
                                team = outcome['name']

                                # --- PRICE MOVEMENT LOGIC ---
                                if m_id in memory and memory[m_id].get('team') == team:
                                    prev_price = memory[m_id]['price']
                                    diff = prev_price - price
                                    
                                    if diff >= SENSITIVITY:
                                        msg = (f"📈 **SMART MONEY ALERT ({sport.upper()})**\n"
                                               f"Match: {game['away_team']} @ {game['home_team']}\n"
                                               f"Team: {team}\n"
                                               f"Movement: {prev_price} ➡️ {price}")
                                        send_alert(msg)

                                memory[m_id] = {'price': price, 'team': team}
            else:
                print(f"❌ API Error {res.status_code} for {sport}: {res.text}")

        except Exception as e:
            print(f"❌ Connection Error for {sport}: {e}")

    # Save Price Memory back to file
    with open(CACHE_FILE, 'w') as f:
        json.dump(memory, f)

if __name__ == "__main__":
    print("--- 24/7 UNIVERSAL SCANNER ONLINE ---")
    run_val_bot()
