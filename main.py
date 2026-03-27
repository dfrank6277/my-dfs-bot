def run_val_bot():
    api_key = os.getenv("ODDS_API_KEY")
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    # 100k Plan - Let's scan the heavy hitters
    sports = ['basketball_nba', 'esports_csgo', 'baseball_mlb', 'icehockey_nhl']
    
    for sport in sports:
        url = f"https://api.the-odds-api.com{sport}/odds/"
        params = {
            'apiKey': api_key, 
            'regions': 'us', 
            'markets': 'h2h', 
            'oddsFormat': 'american'
        }
        
        print(f"📡 Scanning {sport}...")
        res = requests.get(url, params=params)

        if res.status_code == 200:
            data = res.json()
            if not data:
                print(f"Empty market for {sport}.")
                continue

            for match in data:
                home = match.get('home_team')
                away = match.get('away_team')
                
                # --- THE VALUE FILTER (100k Strategy) ---
                # We only want plays with high probability (Odds <= -145)
                found_value = False
                for bookmaker in match.get('bookmakers', []):
                    for market in bookmaker.get('markets', []):
                        for outcome in market.get('outcomes', []):
                            price = outcome.get('price')
                            
                            if price and price <= -145:
                                found_value = True
                                print(f"🎯 VALUE FOUND: {outcome['name']} ({price})")
                                
                                # --- THE DISCORD ALERT ---
                                msg = {
                                    "content": (
                                        f"🎯 **100K VALUE PLAY FOUND** 🎯\n"
                                        f"🏆 **Sport:** {sport.upper()}\n"
                                        f"⚔️ **Match:** {away} @ {home}\n"
                                        f"👤 **Pick:** {outcome['name']} ({price})\n"
                                        f"🏦 **Bookie:** {bookmaker['title']}\n"
                                        f"----------------------------"
                                    )
                                }
                                
                                # Send and CHECK for errors
                                if webhook_url:
                                    response = requests.post(webhook_url, json=msg)
                                    if response.status_code != 204:
                                        print(f"❌ Discord Error {response.status_code}: {response.text}")
                                else:
                                    print("❌ CRITICAL: DISCORD_WEBHOOK_URL is missing from Secrets!")
                
                if not found_value:
                    print(f"No high-value plays for {away} vs {home}.")
        else:
            print(f"❌ API Error {res.status_code}: {res.text}")

