def run_val_bot():
    # --- UPDATED SPORT SLUGS ---
    sports = [
        'csgo',             # Counter-Strike (was esports_csgo)
        'leagueoflegends',  # League of Legends (was esports_lol)
        'dota2',            # Dota 2
        'pointspread_cod'   # Call of Duty
    ]
    
    for game_type in sports:
        print(f"Scanning {game_type}...")
        
        # URL Logic (Already fixed!)
        domain = "https://api.the-odds-api.com"
        path = "/v4/sports/"
        endpoint = "/odds/"
        full_url = domain + path + game_type + endpoint
        
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        
        try:
            response = requests.get(full_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Found {len(data)} games for {game_type}")
                
                for game in data:
                    home = game.get('home_team')
                    away = game.get('away_team')
                    msg = f"🏆 **MATCH DETECTED**\n{away} vs {home} ({game_type.upper()})"
                    send_discord_alert(msg)
            else:
                print(f"❌ API Error {response.status_code} for {game_type}")
