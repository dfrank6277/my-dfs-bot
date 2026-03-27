import requests
import os
import json
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURATION ---
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
PANDASCORE_TOKEN = os.getenv("PANDASCORE_TOKEN")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
# Ensure SHEET_ID is the long ID string from the URL, not the email address
SHEET_ID = "YOUR_ACTUAL_SHEET_ID_HERE" 

TOTAL_BANKROLL = 1000 
UNIT_SIZE = TOTAL_BANKROLL * 0.01

# --- 2. DATA LOGGING ---
def log_to_sheets(row):
    try:
        creds_json = os.getenv("GOOGLE_SHEETS_JSON")
        if not creds_json: 
            print("Missing Google Sheets JSON secret.")
            return
        
        creds_dict = json.loads(creds_json)
        scope = ['https://www.googleapis.com', 'https://www.googleapis.com']
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1
        sheet.append_row(row)
    except Exception as e: 
        print(f"Sheet Error: {e}")

# --- 3. THE DECISION ENGINE ---
def analyze_play(market_odds):
    score = 50 
    if market_odds <= -145: score += 25 
    if market_odds <= -160: score += 15 
    
    if score >= 90: return "🟢 GOBLIN", score, 5
    if score >= 75: return "🎯 STANDARD", score, 3
    if score >= 70: return "😈 DEMON", score, 1
    return None, 0, 0

# --- 4. EXECUTION ---
def run_bot():
    # Example: Scanning CS2 Live Matches via PandaScore
    if PANDASCORE_TOKEN:
        try:
            url = "https://api.pandascore.co"
            headers = {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}
            response = requests.get(url, headers=headers)
            matches = response.json()

            if isinstance(matches, list) and len(matches) > 0:
                for match in matches:
                    name = match.get('name', 'Unknown Match')
                    results = match.get('results', [])
                    score_text = " - ".join([str(r.get('score', 0)) for r in results])
                    
                    msg = f"🔴 **LIVE CS2 MATCH**\n⚔️ **{name}**\n📊 **Score:** `{score_text}`"
                    requests.post(WEBHOOK_URL, json={"content": msg})
            else:
                print("No live CS2 matches found.")
        except Exception as e:
            print(f"PandaScore Error: {e}")

    # Example: System Test / Odds API Simulation
    # In a real run, you'd loop through Odds API results here
    play_type, conf, units = analyze_play(-155)

    if play_type:
        msg = (
            f"🚀 **ULTIMATE BOT ONLINE** 🚀\n"
            f"🏆 **Type:** {play_type} | 🎯 **Conf:** {conf}%\n"
            f"💰 **Unit Bet:** `{units}u` (${units * UNIT_SIZE:.2f})\n"
            f"----------------------------"
        )
        requests.post(WEBHOOK_URL, json={"content": msg})
        log_to_sheets([str(datetime.now()), "System Test", "Live Scan", play_type, units, f"{conf}%"])

if __name__ == "__main__":
    run_bot()
