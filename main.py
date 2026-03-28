import requests
import os
import json
import time

# --- THIS PART WAS MISSING OR BROKEN ---
# This pulls the keys from your GitHub Secrets into the bot
API_KEY = os.getenv("ODDS_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_discord_alert(message):
    """Sends the found play to your Discord channel."""
    if not DISCORD_WEBHOOK:
        print("Discord Webhook not found in Secrets.")
        return
        
    data = {
        "content": f"🚀 **DFS BOT ALERT** 🚀\n{message}",
        "username": "DFS Optimizer Pro"
    }
    try:
        # Using json=data automatically sets the headers for you
        requests.post(DISCORD_WEBHOOK, json=data, timeout=10)
    except Exception as e:
        print(f"Discord Error: {e}")

def run_val_bot():
    # ... the rest of your run_val_bot function code here ...

