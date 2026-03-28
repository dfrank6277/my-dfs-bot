def run_dfs_engine():
    # Corrected Slugs
    esports_titles = {'cs2': 'csgo_esl', 'lol': 'leagueoflegends_lck'}
    
    for title, odds_slug in esports_titles.items():
        print(f"Analyzing {title.upper()}...")
        
        # --- THE BULLETPROOF URL FIX ---
        # No variables here—just the straight, correct path
        url = "https://api.the-odds-api.com" + odds_slug + "/odds/"
        
        params = {
            'apiKey': ODDS_API_KEY,
            'regions': 'us',
            'markets': 'h2h,player_props',
            'oddsFormat': 'american'
        }
        
        try:
            print(f"DEBUG: Visiting {url}")
            res = requests.get(url, params=params, timeout=15)
            
            if res.status_code == 200:
                data = res.json()
                print(f"✅ SUCCESS: Found {len(data)} games for {odds_slug}")
                for match in data:
                    msg = f"🏆 **MATCH FOUND**: {match['away_team']} vs {match['home_team']}"
                    send_alert(msg)
            else:
                print(f"❌ API Error {res.status_code}: {res.text}")
                
        except Exception as e:
            print(f"❌ Connection Error for {odds_slug}: {e}")
