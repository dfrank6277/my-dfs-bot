import requests
import os
import json

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
GRID_API_KEY = os.getenv("GRID_API_KEY")

def send_discord_alert(message):
    if not DISCORD_WEBHOOK: return
    requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)

def get_player_props(game_type, match_id):
    """Queries specific player props for a detected comeback match."""
    url = f"https://api.the-odds-api.com{game_type}/events/{match_id}/odds/"
    params = {'apiKey': API_KEY, 'regions': 'us', 'markets': 'player_kills,player_points', 'oddsFormat': 'american'}
    res = requests.get(url, params=params)
    return res.json() if res.status_code == 200 else {}

def run_val_bot():
    esports = ['esports_csgo', 'esports_lol']
    
    for game_type in esports:
        # FIXED: Added the full /v4/sports/ path
        score_url = f"https://api.the-odds-api.com{game_type}/scores/"
        score_res = requests.get(score_url, params={'apiKey': API_KEY, 'daysFrom': 1})
        
        odds_url = f"https://api.the-odds-api.com{game_type}/odds/"
        odds_params = {'apiKey': API_KEY, 'regions': 'us', 'markets': 'h2h'}
        odds_res = requests.get(odds_url, params=odds_params)

        if score_res.status_code == 200 and odds_res.status_code == 200:
            scores_map = {s['id']: s for s in score_res.json()}
            
            for match in odds_res.json():
                m_id = match['id']
                if m_id in scores_map and not scores_map[m_id].get('completed', False):
                    live_info = scores_map[m_id]
                    
                    for score_item in live_info.get('scores', []):
                        if score_item['score'] == "0": # Team is trailing
                            trailing_team = score_item['name']
                            
                            for book in match.get('bookmakers', []):
                                for market in book.get('markets', []):
                                    for outcome in market.get('outcomes', []):
                                        # 1. DETECT COMEBACK VALUE
                                        if outcome['name'] == trailing_team and outcome['price'] < 150:
                                            
                                            # 2. TRIGGER PLAYER PROP LOOKUP
                                            props = get_player_props(game_type, m_id)
                                            best_prop = "Check Grid for Over" # Placeholder for Grid API comparison
                                            
                                            msg = (f"🔄 **COMEBACK & PROP ALERT**\n"
                                                   f"Game: {match['away_team']} vs {match['home_team']}\n"
                                                   f"Value: {trailing_team} down 0-1 (Odds: {outcome['price']})\n"
                                                   f"🎯 **Best DFS Play:** Take Top Fragger 'Over' (3 Maps Expected!)")
                                            send_discord_alert(msg)
        else:
            print(f"API Error for {game_type}")

if __name__ == "__main__":
    run_val_bot()
