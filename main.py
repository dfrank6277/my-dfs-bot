def run_val_bot():
    api_key = os.getenv("ODDS_API_KEY")
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL") # Get your webhook from secrets
    sports = ['basketball_nba', 'esports_csgo', 'baseball_mlb', 'icehockey_nhl']
    
    for sport in sports:
        url = f"https://api.the-odds-api.com{sport}/odds/"
        params = {'apiKey': api_key, 'regions': 'us', 'markets': 'h2h', 'oddsFormat': 'american'}
        
        print(f"Checking {sport}...")
        res = requests.get(url, params=params)

        if res.status_code == 200:
            data = res.json()
            for match in data:
                home = match.get('home_team')
                away = match.get('away_team')
                
                # --- STEP 2: THE DISCORD ALERT ---
                print(f"✅ Found match: {away} @ {home}") # Logs to GitHub

                msg = {
                    "content": f"🚀 **BOT ONLINE**\n📡 **Match Found:** {away} @ {home}\n📊 **Sport:** {sport.upper()}"
                }
                
                # This actually sends it to your Discord channel
                requests.post(webhook_url, json=msg)
                # ---------------------------------
        else:
            print(f"❌ API Error {res.status_code}: {res.text}")

