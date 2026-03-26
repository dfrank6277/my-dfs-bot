import requests
import os

# 1. Your Discord Webhook
webhook_url = "https://discordapp.com/api/webhooks/1486844673111752744/rO10B7b4Ec4UYWr6U6wx41z-_0kl4WDS4XqpyBSZ2jirlMZcIHAQrcGyQXSoOHDIvR1y"
pandascore_token = os.getenv("PANDASCORE_TOKEN")

# 2. Let's try "running" matches (live) or "upcoming"
url = "https://api.pandascore.co"
headers = {"Authorization": f"Bearer {pandascore_token}"}

try:
    print("Connecting to PandaScore...")
    response = requests.get(url, headers=headers)
    data = response.json()

    # DEBUG: Send a heartbeat to Discord so we know the bot is awake
    requests.post(webhook_url, json={"content": "📡 Bot is checking PandaScore for CS2 matches..."})

    if isinstance(data, list) and len(data) > 0:
        match = data[0] # Take the very first match found
        name = match.get('name', 'Unknown Match')
        status = match.get('status', 'TBD')
        
        msg = f"✅ **Match Found!**\nMatch: **{name}**\nStatus: `{status.upper()}`"
        requests.post(webhook_url, json={"content": msg})
    else:
        # If no matches, tell Discord so we know for sure
        requests.post(webhook_url, json={"content": "Empty: No CS2 matches found in the API right now."})

except Exception as e:
    error_msg = f"❌ Error: {str(e)}"
    requests.post(webhook_url, json={"content": error_msg})
