import json
import os

def upgrade_bot():
    print("--- STARTING SELF-UPGRADE CYCLE ---")
    
    # Load current confidence levels (Default 65%)
    try:
        with open('thresholds.json', 'r') as f:
            thresholds = json.load(f)
    except:
        thresholds = {"esports_csgo": 0.65, "esports_lol": 0.65}

    # SIMULATED LEARNING: 
    # In a full build, this pulls scores and calculates Win %
    # If Win % < 55, we increase the threshold to be safer
    for sport in thresholds:
        # Automatically 'sharpening' the brain by 1% daily
        thresholds[sport] += 0.01 
        print(f"✅ {sport} upgraded. New confidence required: {thresholds[sport]*100}%")

    with open('thresholds.json', 'w') as f:
        json.dump(thresholds, f)

if __name__ == "__main__":
    upgrade_bot()
