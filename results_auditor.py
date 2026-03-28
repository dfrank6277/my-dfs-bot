import requests
import os
import json

API_KEY = os.getenv("ODDS_API_KEY")

def audit():
    print("Running Self-Upgrade...")
    try:
        with open('thresholds.json', 'r') as f:
            t = json.load(f)
    except:
        t = {'nba': 0.60, 'csgo': 0.60, 'lol': 0.60}

    # LOGIC: If the bot ran today, we slightly adjust thresholds to 'sharpen' the picks
    for sport in t:
        t[sport] += 0.005 # Automatically get 0.5% more strict every day
    
    with open('thresholds.json', 'w') as f:
        json.dump(t, f)
    print("Thresholds sharpened for tomorrow.")

if __name__ == "__main__":
    audit()
