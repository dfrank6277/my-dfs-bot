import requests
import os
import json
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURATION ---
SHEET_ID = "betting-tracker-service-accoun@new-future-491423.iam.gserviceaccount.com"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
TOTAL_BANKROLL = 1000 
UNIT_SIZE = TOTAL_BANKROLL * 0.01

# --- 2. THE DATA LOGGING ---
def log_to_sheets(row):
    try:
        creds_json = os.getenv("GOOGLE_SHEETS_JSON")
        if not creds_json: return
        creds_dict = json.loads(creds_json)
        scope = ['https://www.googleapis.com']
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1
        sheet.append_row(row)
    except Exception as e: 
        print(f"Sheet Error: {e}")

# --- 3. THE DECISION ENGINE ---
def analyze_play(sport, player, market_odds):
    score = 50 
    if market_odds <= -145: score += 25 # Value Gap
    if market_odds <= -160: score += 15 # Imminent Bump
    
    if score >= 90: return "🟢 GOBLIN", score, 5
    if score >= 75: return "🎯 STANDARD", score, 3
    if score >= 70: return "😈 DEMON", score, 1
    return None, 0, 0

# --- 4. EXECUTION LOOP ---
def run_bot():
    # 100k Plan allows us to scan all these major sports every 14 mins
    sports = ['basketball_nba', 'esports_csgo', 'baseball_mlb', 'basketball_wnba', 'icehockey_nhl']
    
    for sport in sports:
        # This is where the 100k Odds API pulls real data
        # For the FIRST run, we'll send one 'Gold' test signal to verify everything
        play_type, conf, units = analyze_play(sport, "System Test", -155)

        if play_type and sport == 'basketball_nba': # Just one test alert for the first run
            msg = (
                f"🚀 **ULTIMATE BOT ONLINE** 🚀\n"
                f"🏆 **Type:** {play_type} | 👤 **Player:** Live Scan Started\n"
                f"💰 **Unit Bet:** `{units}u` (${units * UNIT_SIZE:.2f})\n"
                f"📱 **Status:** 100k Plan Active | 📋 **Sheets:** Connected\n"
                f"----------------------------"
            )
            requests.post(WEBHOOK_URL, json={"content": msg})
            log_to_sheets([str(datetime.now()), sport, "System Test", play_type, units, f"{conf}%"])

if __name__ == "__main__":
    run_bot()
