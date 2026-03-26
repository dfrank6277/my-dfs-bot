import requests
import os

# 1. Your Discord Webhook
webhook_url = "https://discordapp.com/api/webhooks/1486844673111752744/rO10B7b4Ec4UYWr6U6wx41z-_0kl4WDS4XqpyBSZ2jirlMZcIHAQrcGyQXSoOHDIvR1y"
pandascore_token = os.getenv("PANDASCORE_TOKEN")

# 2. Simplified URL to get ANY upcoming CS2 match
url = "https://api.pandascore.co"
headers = {"Authorization": f"Bearer {pandascore_token}"}

try:
    response = requests.get(url, headers=headers)
    data = response.json()

    # If it's a list, take the first item. If it's a dict, use it as is.
    match = data[0] if isinstance(data, list) and len(data) > 0 else data

    if match and 'name' in match:
        name = match.get('name', 'Unknown Match')
        scheduled_at = match.get('begin_at', 'TBD')
        
        msg = f"🔫 **Upcoming CS2 Match Found!**\nMatch: **{name}**\nStarts: `{scheduled_at}`"
        requests.post(webhook_url, json={"content": msg})
        print("Success! Sent to Discord.")
    else:
        print(f"No match found. API Response: {data}")

except Exception as e:
    print(f"Something went wrong: {e}")

webhook_url = "https://discordapp.com/api/webhooks/1486844673111752744/rO10B7b4Ec4UYWr6U6wx41z-_0kl4WDS4XqpyBSZ2jirlMZcIHAQrcGyQXSoOHDIvR1y"
