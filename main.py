import requests
import os
import json

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_alert(message):
    if not DISCORD_WEBHOOK: return
    requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)

def run_dfs_engine():
    # TEST: If the key is empty, the bot will tell us here
    if not API_KEY:
        print("❌ CRITICAL ERROR: API_KEY is empty in GitHub Secrets!")
        return

    NBA_PROPS = ['player_points', 'player_rebounds', 'player_assists']
    
    for prop in NBA_PROPS:
        # THE FIX: Hard-coding the query string into the URL
        url = f"https://api.the-odds-api.com{API_KEY}&regions=us&markets={prop}&oddsFormat=american&bookmakers=fanduel,draftkings"
        
        try:
            print(f"DEBUG: Visiting URL (Key Hidden)...")
            res = requests.get(url, timeout=15)
            data = res.json()
            
            if isinstance(data, list):
                print(f"✅ SUCCESS: Found {len(data)} games for {prop}")
                for game in data:
                    # ... (rest of your logic to post to Discord)
                    pass
            else:
                # If it still shows 'Welcome', we'll see the exact message here
                print(f"❌ API Rejected Key. Message: {data.get('message')}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    run_dfs_engine()
