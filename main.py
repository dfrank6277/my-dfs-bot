import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
GRID_API_KEY = os.getenv("GRID_API_KEY")
SENSITIVITY = 25  # Alerts if a line moves 25+ points (e.g. -110 to -135)

def send_discord_alert(message):
    if not DISCORD_WEBHOOK: return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_val_bot():
    # Load 'Last Price' memory
    try:
        with open('price_memory.json', 'r') as f:
            memory = json.load(f)
    except:
        memory = {}

    esports = ['esports_csgo', 'esports_lol']
    for game_type in esports:
        print(f"Scanning Live Lines for {game_type}...")
        url = f"https://api.the-odds-api.com{game_type}/odds/"
        
        try:
            res = requests.get(url, params={'apiKey': API_KEY, 'regions': 'us', 'markets': 'h2h'}, timeout=15)
            if res.status_code != 200: continue
            
            for match in res.json():
                m_id = match['id']
                # Track the Favorite's Price
                for book in match.get('bookmakers', []):
                    for market in book.get('markets', []):
                        for outcome in market.get('outcomes', []):
                            price = outcome['price']
                            team = outcome['name']
                            
                            # LOGIC: Compare to 13 minutes ago
                            if m_id in memory and memory[m_id]['team'] == team:
                                diff = memory[m_id]['price'] - price
                                if diff >= SENSITIVITY:
                                    msg = (f"📈 **SMART MONEY DETECTED**\n"
                                           f"Match: {match['away_team']} vs {match['home_team']}\n"
                                           f"Team: {team}\n"
                                           f"Movement: {memory[m_id]['price']} ➡️ {price}\n"
                                           f"🔥 **Action:** Line is crashing! Bet now.")
                                    send_discord_alert(msg)

                            # Update Memory
                            memory[m_id] = {'price': price, 'team': team, 'time': time.time()}
                            
        except Exception as e:
            print(f"Scraper Error: {e}")

    # Save Memory
    with open('price_memory.json', 'w') as f:
        json.dump(memory, f)

if __name__ == "__main__":
    run_val_bot()
