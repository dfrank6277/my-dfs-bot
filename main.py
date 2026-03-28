import requests
import os
import json
import time

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CACHE_FILE = "sent_matches.json"

def send_discord_alert(message):
    if not DISCORD_WEBHOOK: return
    requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)

def run_val_bot():
    # Adding 'scores' to the list to see live progress
    esports = ['esports_csgo', 'esports_lol']
    
    for game_type in esports:
        # 1. Fetch LIVE scores first
        score_url = f"https://api.the-odds-api.com{game_type}/scores/"
        score_res = requests.get(score_url, params={'apiKey': API_KEY, 'daysFrom': 1})
        
        # 2. Fetch LIVE odds
        odds_url = f"https://api.the-odds-api.com{game_type}/odds/"
        odds_params = {'apiKey': API_KEY, 'regions': 'us', 'markets': 'h2h'}
        odds_res = requests.get(odds_url, params=odds_params)

        if score_res.status_code == 200 and odds_res.status_code == 200:
            scores = {s['id']: s for s in score_res.json()}
            odds = odds_res.json()

            for match in odds:
                m_id = match['id']
                if m_id in scores and not scores[m_id]['completed']:
                    live_data = scores[m_id]
                    
                    # LOGIC: Check for 0-1 Comeback Opportunity
                    # Find the team that is currently losing in maps
                    for score_item in live_data.get('scores', []):
                        if int(score_item['score']) == 0:
                            trailing_team = score_item['name']
                            
                            # Check if the "Smart Money" still likes the trailing team
                            for book in match['bookmakers']:
                                for outcome in book['markets'][0]['outcomes']:
                                    if outcome['name'] == trailing_team and outcome['price'] < 150:
                                        msg = f"🔄 **LIVE COMEBACK ALERT** 🔄\nGame: {match['away_team']} vs {match['home_team']}\nStatus: **{trailing_team} is down 0-1**\nSmart Money Odds: **{outcome['price']}**\n*The model predicts a 2-1 Reverse Sweep!*"
                                        send_discord_alert(msg)

            else:
                print(f"API Error {res.status_code}: {res.text}")
        except Exception as e:
            print(f"Error analyzing {game_type}: {e}")

if __name__ == "__main__":
    run_val_bot()
