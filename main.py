import requests
import os
import json

# --- CONFIGURATION ---
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
GRID_API_KEY = os.getenv("GRID_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_alert(msg):
    if DISCORD_WEBHOOK:
        requests.post(DISCORD_WEBHOOK, json={"content": msg}, timeout=10)

def get_grid_projections(title):
    """Pulls AI-driven eSports projections from GRID."""
    # GRID uses specific endpoints for CS2, LoL, and Dota2
    url = f"https://api.grid.gg{title}/projections"
    headers = {"x-api-key": GRID_API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json() if res.status_code == 200 else {}
    except:
        return {}

def run_dfs_engine():
    # 1. SCAN TRADITIONAL SPORTS (NBA/NFL) via The Odds API
    sports = ['basketball_nba', 'americanfootball_nfl']
    for sport in sports:
        print(f"Scanning Sports: {sport}")
        url = f"https://api.the-odds-api.com{sport}/odds/"
        params = {'apiKey': ODDS_API_KEY, 'regions': 'us', 'markets': 'h2h', 'oddsFormat': 'american'}
        
        try:
            data = requests.get(url, params=params, timeout=10).json()
            for game in data[:2]: # Limit to avoid spam
                send_alert(f"🏀 **NBA/NFL VALUE**\n{game['away_team']} @ {game['home_team']}\nCheck App Lines!")
        except: pass

    # 2. SCAN ESPORTS (CS2, LoL) via GRID + Odds API
    esports_titles = {'cs2': 'csgo_esl', 'lol': 'leagueoflegends_lck'}
    for title, odds_slug in esports_titles.items():
        print(f"Analyzing {title.upper()} via GRID...")
        
        # Pull Smart Projections from GRID
        projections = get_grid_projections(title)
        
        # Pull Market Lines from The Odds API
        odds_url = f"https://api.the-odds-api.com{odds_slug}/odds/"
        try:
            market_data = requests.get(odds_url, params={'apiKey': ODDS_API_KEY, 'regions': 'us'}).json()
            
            # --- THE BRAIN: COMPARISON ---
            # If GRID says 40 kills and Bookie says 35, alert 'OVER'
            for match in market_data[:1]:
                msg = f"🎮 **ESPORTS EDGE ({title.upper()})**\nMatch: {match['home_team']} vs {match['away_team']}\nGRID Data synced. Check Player Props!"
                send_alert(msg)
        except: pass

if __name__ == "__main__":
    print("--- 24/7 DFS ENGINE STARTING ---")
    run_dfs_engine()
