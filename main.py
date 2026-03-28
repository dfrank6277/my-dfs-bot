import requests
import os
import json

# --- CONFIGURATION ---
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
GRID_API_KEY = os.getenv("GRID_API_KEY")

def send_discord_alert(message):
    if not DISCORD_WEBHOOK: return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def get_grid_projection(team_name, game_type):
    """Fetches the exact kill count projection from your Grid API."""
    url = f"https://api.thegrid.io{game_type}" 
    headers = {"Authorization": f"Bearer {GRID_API_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        for p in res.get('players', []):
            if p['team'] in team_name:
                return p.get('kills_projection')
    except:
        return None
    return None

def run_val_bot():
    esports = ['esports_csgo', 'esports_lol']
    for game_type in esports:
        print(f"Scanning {game_type}...")
        score_url = f"https://api.the-odds-api.com{game_type}/scores/"
        odds_url = f"https://api.the-odds-api.com{game_type}/odds/"
        
        try:
            score_data = requests.get(score_url, params={'apiKey': API_KEY, 'daysFrom': 1}, timeout=10).json()
            scores_map = {s['id']: s for s in score_data}
            
            odds_res = requests.get(odds_url, params={'apiKey': API_KEY, 'regions': 'us', 'markets': 'h2h'}, timeout=10).json()

            for match in odds_res:
                m_id = match['id']
                if m_id in scores_map and not scores_map[m_id].get('completed', False):
                    live_info = scores_map[m_id]
                    for score_item in live_info.get('scores', []):
                        if str(score_item['score']) == "0":
                            trailing_team = score_item['name']
                            
                            for book in match.get('bookmakers', []):
                                for market in book.get('markets', []):
                                    for outcome in market.get('outcomes', []):
                                        if outcome['name'] == trailing_team and outcome['price'] < 150:
                                            proj = get_grid_projection(trailing_team, game_type)
                                            proj_text = f"🎯 **Grid Proj:** {proj} Kills" if proj else "🎯 **Grid Proj:** High Volume Expected"

                                            msg = (f"🔄 **LIVE COMEBACK ALERT**\n"
                                                   f"Match: {match['away_team']} vs {match['home_team']}\n"
                                                   f"Value: {trailing_team} is down 0-1 (Odds: {outcome['price']})\n"
                                                   f"{proj_text}\n"
                                                   f"🔥 **Play:** Over on {trailing_team} Star Players")
                                            send_discord_alert(msg)
        except Exception as e:
            print(f"Error scanning {game_type}: {e}")

if __name__ == "__main__":
    run_val_bot()
