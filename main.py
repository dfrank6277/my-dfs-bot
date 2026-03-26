import requests
import os

# Get your secrets
webhook_url = "https://discordapp.com/api/webhooks/1486844673111752744/rO10B7b4Ec4UYWr6U6wx41z-_0kl4WDS4XqpyBSZ2jirlMZcIHAQrcGyQXSoOHDIvR1y"
pandascore_token = os.getenv("PANDASCORE_TOKEN")

# PandaScore CS2 Matches Endpoint
url = "https://api.pandascore.co"
headers = {"Authorization": f"Bearer {pandascore_token}"}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    match_data = response.json()[0]
    team_a = match_data['opponents'][0]['opponent']['name']
    team_b = match_data['opponents'][1]['opponent']['name']
    winner = match_data['winner']['name']
    
    msg = f"🎮 **CS2 Result Update**\n{team_a} vs {team_b}\n🏆 Winner: **{winner}**"
    requests.post(webhook_url, json={"content": msg})
else:
    print(f"Error fetching data: {response.status_code}")
