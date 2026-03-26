import requests
import os

# 1. Use your real Discord URL here
webhook_url = "https://discordapp.com/api/webhooks/1486844673111752744/rO10B7b4Ec4UYWr6U6wx41z-_0kl4WDS4XqpyBSZ2jirlMZcIHAQrcGyQXSoOHDIvR1y"

pandascore_token = os.getenv("PANDASCORE_TOKEN")

# 2. Updated URL to find ANY recent CS2 matches
url = "https://api.pandascore.co"
headers = {"Authorization": f"Bearer {pandascore_token}"}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    
    if len(data) > 0:
        match = data[0]
        match_name = match.get('name', 'Unknown Match')
        status = match.get('status', 'scheduled')
        
        msg = f"🎮 **CS2 Match Found!**\nMatch: {match_name}\nStatus: **{status.upper()}**"
        requests.post(webhook_url, json={"content": msg})
        print("Success: Message sent to Discord!")
    else:
        print("Connected to API, but no matches were found.")
        requests.post(webhook_url, json={"content": "Checking CS2 matches... none active right now."})
else:
    print(f"Error: {response.status_code}")
    print(response.text)
