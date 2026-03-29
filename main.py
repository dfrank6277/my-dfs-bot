import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# Major NBA props
NBA_PROPS = ['player_points', 'player_rebounds', 'player_assists']

def send_alert(message):
    if not DISCORD_WEBHOOK: return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_dfs_engine():
    # TEMPORARY: Clear cache to force immediate posts for testing
    cache = {} 

    print("--- 🏀 GLOBAL SCAN: SHOWING ALL PLAYS ---")
    for prop in NBA_PROPS:
        url = "https://api.the-odds-api.com"
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': prop,
            'oddsFormat': 'american',
            'bookmakers': 'fanduel,draftkings'
        }
        
        try:
            print(f"DEBUG: Pulling {prop}...")
            res = requests.get(url, params=params, timeout=15)
            data = res.json()
            
            if isinstance(data, list):
                if len(data) == 0:
                    print(f"ℹ️ No active lines for {prop} yet.")
                    continue
                
                print(f"✅ Data found! Posting to Discord...")
                for game in data:
                    for book in game.get('bookmakers', []):
                        for market in book.get('markets', []):
                            for outcome in market.get('outcomes', []):
                                player = outcome.get('description')
                                line = outcome.get('point')
                                price = outcome.get('price')
                                
                                # NO FILTER: Every play gets posted
                                msg = (f"🏀 **NBA PROP DETECTED**\n"
                                       f"Player: **{player}**\n"
                                       f"Prop: {prop.replace('player_', '').capitalize()}\n"
                                       f"Line: {line}\n"
                                       f"Odds: {price}")
                                send_alert(msg)
            else:
                print(f"⚠️ API Info: {data}")

        except Exception as e:
            print(f"❌ Error on {prop}: {e}")

if __name__ == "__main__":
    send_alert("🔍 **LIVE FEED STARTING** - Showing every active NBA line...")
    run_dfs_engine()
