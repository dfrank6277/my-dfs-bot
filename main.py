import requests
import random

# 1. DATA COLLECTION (NBA Example)
def get_props():
    # In a real setup, this pulls from PrizePicks/Underdog scrapers
    # For now, we simulate a 'Projection' vs a 'Line'
    projection = 25.5  # AI thinks he gets 25
    line = 22.5        # PrizePicks says 22
    edge = projection - line
    return edge

# 2. THE LEARNING BRAIN
def run_ai_logic():
    edge = get_props()
    confidence = 0.85 # This is what the bot 'adjusts' over time
    
    if (edge * confidence) > 2.0:
        print(f"🔥 TOP PICK FOUND: Over {edge} point edge!")
    else:
        print("Scanning for better value...")

if __name__ == "__main__":
    run_ai_logic()
import requests

# This is the "phone number" for your Discord channel
webhook_url = https://discordapp.com/api/webhooks/1486844673111752744/rO10B7b4Ec4UYWr6U6wx41z-_0kl4WDS4XqpyBSZ2jirlMZcIHAQrcGyQXSoOHDIvR1y

data = {
    "content": "Hello! The betting bot is now running!"
}

# This line actually sends the message
response = requests.post(webhook_url, json=data)

# This checks if it worked
if response.status_code == 204:
    print("Message sent successfully!")
else:
    print(f"Failed to send message. Error: {response.status_code}")
