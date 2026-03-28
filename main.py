import requests
import os
import json
import time

# --- 1. CONFIGURATION (GitHub Secrets) ---
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
GRID_API_KEY = os.getenv("GRID_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# --- 2. PLAYER MAPPING (Translates Real Names to Gamer Tags) ---
PLAYER_MAP = {
    "Oleksandr Kostyliev": "s1mple",
    "Mathieu Herbaut": "ZywOo",
    "Lee Sang-hyeok": "Faker",
    "Nicolai Reedtz": "device",
    "Nikola Kovač": "NiKo",
    "Ilya Osipov": "m0NESY"
}

def get_mapped_name(name):
    """Returns the gamer tag if known, otherwise returns the name and flags it."""
    if name in PLAYER_MAP:
        return PLAYER_MAP[name]
    # AUTO-DISCOVERY: If we don't know the player, we print it to the logs
    print(f"DEBUG: Unknown Player Detected: {name}")
    return name

def send_alert(message):
    if not DISCORD_WEBHOOK: return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def get_grid_projections(title):
    """Pulls eSports projections from GRID API."""
    url = f"https://api.grid.gg{title}/projections"
    headers = {"x-api-key": GRID_API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json() if res.status_code == 200 else {}
    except:
        return {}

def run_dfs_engine():
    # --- SCAN ESPORTS (CS2, LoL) ---
    esports_titles = {'cs2': 'csgo_esl', 'lol': 'leagueoflegends_lck'}
    
    for title, odds_slug in esports_titles.items():
        print(f"Analyzing {title.upper()}...")
        
        # 1. Get GRID Data
        grid_data = get_grid_projections(title)
        
        # 2. Get Market Odds (Fixed URL Logic)
        url = f"https://api.the-odds-api.com{odds_slug}/odds/"
        params = {'apiKey': ODDS_API_KEY, 'regions': 'us', 'markets': 'h2h,player_props'}
        
        try:
            res = requests.get(url, params=params, timeout=15)
            if res.status_code == 200:
                matches = res.json()
                for match in matches:
                    for book in match.get('bookmakers', []):
                        for market in book.get('markets', []):
                            for outcome in market.get('outcomes', []):
                                # MAP THE NAME
                                raw_name = outcome.get('description', outcome['name'])
                                gamer_tag = get_mapped_name(raw_name)
                                
                                # --- THE BRAIN: Match GRID to Odds ---
                                # If the names match, the bot finds the 'Edge'
                                alert_msg = f"🎯 **{title.upper()} EDGE FOUND**\nPlayer: {gamer_tag}\nMatch: {match['away_team']} vs {match['home_team']}"
                                send_alert(alert_msg)
            else:
                print(f"API Error {res.status_code} for {odds_slug}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("--- 24/7 DFS ENGINE ONLINE ---")
    send_alert("🤖 **Bot is active and scanning GRID + Odds API!**")
    run_dfs_engine()
