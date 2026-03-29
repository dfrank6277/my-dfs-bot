import json
import os

def upgrade_logic():
    print("--- STARTING DAILY SELF-UPGRADE ---")
    # This file tracks which sports are performing best
    stats_file = 'performance_stats.json'
    
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            stats = json.load(f)
    else:
        # Initial 'Confidence' levels (65% is the pro standard)
        stats = {"NBA": 0.65, "CS2": 0.65, "LoL": 0.65}

    # SELF-LEARNING: Automatically tighten thresholds by 0.5% each day 
    # to force the bot to find higher value "Sniper" plays.
    for sport in stats:
        stats[sport] = round(min(stats[sport] + 0.005, 0.80), 3)
        print(f"✅ {sport} sharpened. Now requiring {stats[sport]*100}% confidence.")

    with open('performance_stats.json', 'w') as f:
        json.dump(stats, f)

if __name__ == "__main__":
    upgrade_logic()
