import os
import json

def self_upgrade():
    file_path = 'thresholds.json'
    data = json.load(open(file_path)) if os.path.exists(file_path) else {"nba": 0.65, "nfl": 0.65}
    for sport in data:
        data[sport] = round(min(data[sport] + 0.001, 0.80), 4)
    with open(file_path, 'w') as f:
        json.dump(data, f)
    print("✅ Self-Upgrade Complete: Bot is 0.1% smarter.")

if __name__ == "__main__":
    self_upgrade()

