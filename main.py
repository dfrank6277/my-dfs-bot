import requests
import os

# TEST: Just try to send one message
WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def test_discord():
    if not WEBHOOK:
        print("❌ FAIL: GitHub Secret 'DISCORD_WEBHOOK' is empty or missing!")
        return
    
    print(f"DEBUG: Attempting to send to: {WEBHOOK[:20]}...")
    res = requests.post(WEBHOOK, json={"content": "🚨 BOT CONNECTION TEST SUCCESSFUL! 🚨"})
    
    if res.status_code == 204:
        print("✅ SUCCESS: Discord received the message!")
    else:
        print(f"❌ FAIL: Discord Error {res.status_code}: {res.text}")

if __name__ == "__main__":
    test_discord()
