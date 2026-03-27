import requests
import os

def run_val_bot():
    api_key = os.getenv("ODDS_API_KEY")
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    # Using 100k Plan Slugs
    sports = ['basketball_nba', 'esports_csgo', 'baseball_mlb', 'icehockey_nhl']
    
    for sport in sports:
        url = f"https://api.the-odds-api.com{sport}/odds/"
        params = {'apiKey': api_key, 'regions': 'us', 'markets': 'h2h', 'oddsFormat': 'american'}
        
        print(f"📡 Checking {sport}...")
        res = requests.get(url, params=params)

        if res.status_code == 200:
            data = res.json()
            if not data:
                print(f"No matches found for {sport}")
                continue

            for match in data:
                home = match.get('home_team')
                away = match.get('away_team')
                
                # FORCE ALERT: No filters, just send to Discord
                msg = {"content": f"✅ **TEST ALERT**\n🏆 {sport.upper()}\n⚔️ {away} @ {home}"}
                
                print(f"Sending {away} @ {home} to Discord...")
                response = requests.post(webhook_url, json=msg)
                
                if response.status_code != 204:
                    print(f"❌ Discord Error: {response.status_code} - {response.text}")
        else:
            print(f"❌ API Error {res.status_code}: {res.text}")

if __name__ == "__main__":
    run_val_bot()
