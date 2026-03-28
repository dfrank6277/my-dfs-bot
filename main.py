def run_val_bot():
    api_key = "YOUR_API_KEY_HERE" # Make sure your key is inside the quotes
    sport = "basketball_nba"
    
    # Notice the slashes between the sections
    url = f"https://api.the-odds-api.com{sport}/odds/"
    
    params = {
        'apiKey': api_key,
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'american'
    }
    
    print(f"Connecting to: {url}") # This helps you see if it's correct in the logs
    res = requests.get(url, params=params)
    # ... rest of your code
