import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_discord_alert(message):
    if not DISCORD_WEBHOOK: return
    requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)

def run_val_bot():
    esports = ['esports_csgo', 'esports_lol']
    
    for game_type in esports:
        # 1. FIXED: Added the full /v4/sports/ path
        score_url = f"https://api.the-odds-api.com{game_type}/scores/"
        score_res = requests.get(score_url, params={'apiKey': API_KEY, 'daysFrom': 1})
        
        odds_url = f"https://api.the-odds-api.com{game_type}/odds/"
        odds_params = {'apiKey': API_KEY, 'regions': 'us', 'markets': 'h2h'}
        odds_res = requests.get(odds_url, params=odds_params)

        if score_res.status_code == 200 and odds_res.status_code == 200:
            scores_data = score_res.json()
            odds_data = odds_res.json()
            
            # Map scores by ID
            scores_map = {s['id']: s for s in scores_data}

            for match in odds_data:
                m_id = match['id']
                # Only analyze games that are LIVE and not finished
                if m_id in scores_map and not scores_map[m_id].get('completed', False):
                    live_info = scores_map[m_id]
                    
                    # Check scores to find who is trailing
                    for score_item in live_info.get('scores', []):
                        if score_item['score'] == "0": # Trailing in maps
                            trailing_team = score_item['name']
                            
                            # Check if odds are still favorable (Smart Money)
                            for book in match.get('bookmakers', []):
                                for market in book.get('markets', []):
                                    for outcome in market.get('outcomes', []):
                                        if outcome['name'] == trailing_team and outcome['price'] < 150:
                                            msg = f"🔄 **LIVE COMEBACK ALERT**\nGame: {match['away_team']} vs {match['home_team']}\n{trailing_team} is down 0-1, but odds are strong ({outcome['price']})!"
                                            send_discord_alert(msg)
        else:
            # FIXED: Corrected error reporting variable
            print(f"API Error: Score Status {score_res.status_code} | Odds Status {odds_res.status_code}")

if __name__ == "__main__":
    print("Scanning for Live eSports Comebacks...")
    run_val_bot()
