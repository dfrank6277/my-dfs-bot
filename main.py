def run_val_bot():
    api_key = os.getenv("ODDS_API_KEY")
    sports = ['basketball_nba', 'esports_csgo', 'baseball_mlb', 'icehockey_nhl']
    
    for sport in sports:
        # NOTICE THE SLASHES BELOW - THEY ARE REQUIRED
        url = f"https://api.the-odds-api.com{sport}/odds/"
        
        params = {
            'apiKey': api_key,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        
        print(f"Checking {sport}...")
        try:
            res = requests.get(url, params=params)
            if res.status_code != 200:
                print(f"❌ API Error {res.status_code}: {res.text}")
                continue
                
            data = res.json()
            for match in data:
                print(f"✅ Found match: {match['home_team']} vs {match['away_team']}")
                # Add your Discord logic here
        except Exception as e:
            print(f"❌ Connection Error: {e}")

