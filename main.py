import requests
import os

# 1. Your Discord Webhook
webhook_url = "https://discordapp.com/api/webhooks/1486844673111752744/rO10B7b4Ec4UYWr6U6wx41z-_0kl4WDS4XqpyBSZ2jirlMZcIHAQrcGyQXSoOHDIvR1y"
pandascore_token = os.getenv("PANDASCORE_TOKEN")

# 2. Let's try "running" matches (live) or "upcoming"
url = "https://api.pandascore.co"
headers = {"Authorization": f"Bearer {pandascore_token}"}

try:
    response = requests.get(url, headers=headers)
    data = response.json()

    if isinstance(data, list) and len(data) > 0:
        for match in data:
            name = match.get('name', 'Unknown Match')
            # Pull scores if they exist
            results = match.get('results', [])
            score_text = " - ".join([str(r.get('score', 0)) for r in results])
            
            msg = f"🔴 **LIVE CS2 MATCH ALERT**\n⚔️ **{name}**\n📊 **Current Score:** `{score_text}`\n----------------------------"
            requests.post(webhook_url, json={"content": msg})
    else:
        # Just a log in GitHub, no Discord spam if it's empty
        print("No live CS2 matches currently in progress.")

except Exception as e:
    print(f"Error: {e}")
