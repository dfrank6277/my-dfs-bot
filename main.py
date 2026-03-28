import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_discord_alert(message):
    if not DISCORD_WEBHOOK: return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_val_bot():
    # Memory for tracking line movement
    try:
        with open('price_memory.json', 'r') as f:
            memory = json.load(f)
    except:
        memory = {}

    esports = ['esports_csgo', 'esports_lol']
    for game_type in esports:
        print(f"Scanning Live Lines for {game_type}...")
        
        # --- FIXED URL FORMAT (V4 Path Included) ---
        url = f"https://api.the-odds-api.com{game_type}/odds/"
        
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        
        try:
            res = requests.get(url, params=params, timeout=15)
            if res.status_code == 200:
                data = res.json()
                print(f"✅ Successfully pulled {len(data)} games for {game_type}")
                
                for match in data:
                    m_id = match['id']
                    # Look for the best price in the bookmakers list
                    for book in match.get('bookmakers', []):
                        for market in book.get('markets', []):
                            for outcome in market.get('outcomes', []):
                                price = outcome['price']
                                team = outcome['name']
                                
                                # Track movement if we have seen this match before
                                if m_id in memory and memory[m_id]['team'] == team:
                                    diff = memory[m_id]['price'] - price
                                    if diff >= 25: # Sensitivity
                                        msg = f"📈 **SMART MONEY ALERT**\nMatch: {match['away_team']} vs {match['home_team']}\nMovement: {memory[m_id]['price']} ➡️ {price}"
                                        send_discord_alert(msg)

                                # Update memory for next 13-minute run
                                memory[m_id] = {'price': price, 'team': team}
            else:
                print(f"❌ API Error {res.status_code}: {res.text}")
                
        except Exception as e:
            print(f"❌ Scraper Error: {e}")

    # Save Memory back to file
    with open('price_memory.json', 'w') as f:
        json.dump(memory, f)

if __name__ == "__main__":
    print("--- BOT STARTING ---")
    run_val_bot()
