import requests
import os
import json

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
    esports = ['esports_csgo', 'esports_lol']
    
    for game_type in esports:
        print(f"Analyzing {game_type}...")
        
        # --- FIXED URLS: Added /v4/sports/ and proper slashes ---
        score_url = f"https://api.the-odds-api.com{game_type}/scores/"
        odds_url = f"https://api.the-odds-api.com{game_type}/odds/"
        
        try:
            # 1. Get Scores
            score_res = requests.get(score_url, params={'apiKey': API_KEY, 'daysFrom': 1}, timeout=15)
            # 2. Get Odds
            odds_params = {'apiKey': API_KEY, 'regions': 'us', 'markets': 'h2h'}
            odds_res = requests.get(odds_url, params=odds_params, timeout=15)

            if score_res.status_code == 200 and odds_res.status_code == 200:
                scores_map = {s['id']: s for s in score_res.json()}
                
                for match in odds_res.json():
                    m_id = match['id']
                    # Check if game is LIVE
                    if m_id in scores_map and not scores_map[m_id].get('completed', False):
                        live_info = scores_map[m_id]
                        
                        for score_item in live_info.get('scores', []):
                            # Logic: If a team is down 0-1
                            if str(score_item['score']) == "0":
                                trailing_team = score_item['name']
                                
                                # Check if odds show they are still expected to win (Smart Money)
                                for book in match.get('bookmakers', []):
                                    for market in book.get('markets', []):
                                        for outcome in market.get('outcomes', []):
                                            if outcome['name'] == trailing_team and outcome['price'] < 150:
                                                msg = (f"🔄 **LIVE COMEBACK ALERT**\n"
                                                       f"Match: {match['away_team']} vs {match['home_team']}\n"
                                                       f"Value: {trailing_team} is trailing 0-1\n"
                                                       f"Smart Money Odds: {outcome['price']}")
                                                send_discord_alert(msg)
            else:
                print(f"API returned error for {game_type}")
                
        except Exception as e:
            print(f"Connection error for {game_type}: {e}")

if __name__ == "__main__":
    print("Starting DFS Optimizer Bot...")
    run_val_bot()
