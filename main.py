Here's your complete refactored Discord bot code - just copy and paste this into your `main.py`:

```python
import requests
import os
import json
import discord
import asyncio
from discord.ext import commands, tasks

# ------------------ CONFIG ------------------

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
WINSTON_API_URL = "https://skill-showcase-367.preview.emergentagent.com"

REFRESH_MINUTES = 10  # Winston updates every 5min, so 10min is safe
MEMORY_FILE = "memory.json"
LINES_FILE = "lines.json"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

cached_results = []

# ------------------ STORAGE ------------------

def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

memory = load_json(MEMORY_FILE)
line_history = load_json(LINES_FILE)

# ------------------ PERSONALITY ------------------

def jarvis(text):
    return f"{text}\n\n— Jarvis"

# ------------------ FETCH FROM WINSTON ------------------

def get_winston_picks():
    """
    Fetch analyzed picks directly from Winston's API
    Winston handles all the heavy lifting:
    - Real-time odds from The Odds API
    - Player stats and projections
    - Edge calculations
    - Confidence scoring
    """
    try:
        response = requests.get(f"{WINSTON_API_URL}/api/props/daily-picks", timeout=10)
        
        if response.status_code != 200:
            print(f"Winston API error: {response.status_code}")
            return []
        
        data = response.json()
        picks = data.get('picks', [])
        
        # Transform Winston's format to bot's expected format
        results = []
        
        for pick in picks:
            # Track line movement
            player = pick.get('player_name', 'Unknown')
            stat = pick.get('stat_type', 'unknown')
            line = pick.get('line', 0)
            
            key = f"{player}_{stat}"
            old_line = line_history.get(key)
            movement = None
            
            if old_line:
                movement = round(line - old_line, 2)
            
            line_history[key] = line
            
            # Map Winston's fields to bot's expected structure
            results.append({
                "player": player,
                "stat": stat,
                "line": line,
                "movement": movement,
                "team": pick.get('team_abbr', 'UNK'),
                "position": pick.get('position', 'SF'),
                "projection": pick.get('player_avg', line),  # Winston's projected value
                "edge": pick.get('edge', 0),
                "pick": pick.get('recommendation', 'OVER'),  # OVER/UNDER
                "grade": calculate_grade(pick.get('edge', 0), pick.get('confidence', 0)),
                "confidence": pick.get('confidence', 0) / 100,  # Convert to 0-1 scale
                "score": pick.get('edge', 0) * (pick.get('confidence', 0) / 100),  # Edge * confidence
                "reasoning": pick.get('reasoning', ''),
                "bookmaker": pick.get('bookmaker', 'Multiple'),
                "game_time": pick.get('game_time', ''),
                "over_price": pick.get('over_price', -110),
                "under_price": pick.get('under_price', -110)
            })
        
        # Save line history for movement tracking
        save_json(LINES_FILE, line_history)
        
        print(f"✅ Fetched {len(results)} picks from Winston")
        return results
        
    except Exception as e:
        print(f"Error fetching from Winston: {e}")
        return []

# ------------------ HELPERS ------------------

def calculate_grade(edge, confidence):
    """
    Calculate letter grade based on Winston's edge and confidence
    """
    e = abs(edge)
    conf = confidence / 100  # Convert to 0-1 scale
    
    if e >= 4 and conf >= 0.70: return "A"
    if e >= 2.5 and conf >= 0.60: return "B"
    if e >= 1.5 and conf >= 0.50: return "C"
    return "D"

def normalize_stat(stat):
    """Normalize stat names for display"""
    stat_map = {
        'player_points': 'PTS',
        'player_rebounds': 'REB',
        'player_assists': 'AST',
        'player_threes': '3PT',
        'batter_hits': 'HITS',
        'pitcher_strikeouts': 'K'
    }
    return stat_map.get(stat, stat.replace('player_', '').upper())

# ------------------ AUTO LOOP ------------------

@tasks.loop(minutes=REFRESH_MINUTES)
async def auto_refresh():
    """Automatically refresh picks from Winston"""
    global cached_results
    cached_results = get_winston_picks()
    
    if cached_results:
        print(f"🔄 Auto-refreshed: {len(cached_results)} picks loaded from Winston")
    else:
        print("⚠️  Auto-refresh returned no picks")

# ------------------ COMMANDS ------------------

@bot.event
async def on_ready():
    print(f"🤖 Jarvis online as {bot.user}")
    print(f"🧠 Connected to Winston at {WINSTON_API_URL}")
    
    # Initial load
    global cached_results
    cached_results = get_winston_picks()
    print(f"📊 Initial load: {len(cached_results)} picks")
    
    # Start auto-refresh loop
    auto_refresh.start()

@bot.command()
async def top(ctx):
    """Show top 10 highest edge picks"""
    if not cached_results:
        await ctx.send("🔄 Still syncing with Winston... try again in a moment.")
        return

    msg = "🔥 **Top Edges Right Now:**\n\n"

    for r in cached_results[:10]:
        stat_display = normalize_stat(r['stat'])
        move = f" | 📈 Move: {r['movement']:+.1f}" if r['movement'] else ""
        msg += f"`{r['grade']}` **{r['player']}** — {r['pick']} {r['line']} {stat_display} (Edge **{r['edge']:+.1f}**){move}\n"

    await ctx.send(jarvis(msg))

@bot.command()
async def mine(ctx):
    """Show 2-leg parlay with strongest value"""
    best = [r for r in cached_results if r["grade"] in ["A", "B"]][:2]

    if len(best) < 2:
        await ctx.send(jarvis("Not enough elite picks available right now. Check `!top` for current options."))
        return

    msg = "💎 **2-Leg Build with Strongest Value:**\n\n"
    for r in best:
        stat_display = normalize_stat(r['stat'])
        msg += f"**{r['player']}** — {r['pick']} {r['line']} {stat_display} (Edge **{r['edge']:+.1f}**, Grade `{r['grade']}`)\n"

    await ctx.send(jarvis(msg))

@bot.command()
async def why(ctx, *, name):
    """Explain why a specific player is recommended"""
    for r in cached_results:
        if name.lower() in r["player"].lower():
            stat_display = normalize_stat(r['stat'])
            
            msg = (
                f"📊 **{r['player']} Breakdown:**\n\n"
                f"**Line:** {r['line']} {stat_display}\n"
                f"**Projection:** {r['projection']:.1f}\n"
                f"**Edge:** {r['edge']:+.1f} (Grade `{r['grade']}`)\n"
                f"**Confidence:** {r['confidence']*100:.0f}%\n"
                f"**Pick:** {r['pick']}\n"
                f"**Bookmaker:** {r['bookmaker']}\n"
            )
            
            if r['movement']:
                msg += f"**Line Movement:** {r['movement']:+.1f}\n"
            
            if r.get('reasoning'):
                msg += f"\n💡 **Winston's Analysis:**\n{r['reasoning']}"
            
            await ctx.send(jarvis(msg))
            return

    await ctx.send(jarvis(f"❌ {name} not found on the board. Try `!top` to see current picks."))

@bot.command()
async def stats(ctx):
    """Show overall Winston stats for today"""
    if not cached_results:
        await ctx.send("No picks loaded yet.")
        return
    
    total = len(cached_results)
    elite = len([r for r in cached_results if r['grade'] in ['A', 'B']])
    avg_edge = sum(abs(r['edge']) for r in cached_results) / total if total > 0 else 0
    avg_conf = sum(r['confidence'] for r in cached_results) / total if total > 0 else 0
    
    # Sports breakdown
    sports = {}
    for r in cached_results:
        team = r.get('team', 'UNK')
        # Infer sport from stat type (simplified)
        if 'batter' in r['stat'] or 'pitcher' in r['stat']:
            sport = 'MLB'
        else:
            sport = 'NBA'  # Default
        
        sports[sport] = sports.get(sport, 0) + 1
    
    msg = (
        f"📈 **Winston's Daily Stats:**\n\n"
        f"**Total Picks:** {total}\n"
        f"**Elite Picks (A/B):** {elite}\n"
        f"**Avg Edge:** {avg_edge:+.1f}\n"
        f"**Avg Confidence:** {avg_conf*100:.0f}%\n\n"
        f"**Sports Breakdown:**\n"
    )
    
    for sport, count in sports.items():
        msg += f"• {sport}: {count}\n"
    
    await ctx.send(jarvis(msg))

@bot.command()
async def refresh(ctx):
    """Manually refresh picks from Winston"""
    global cached_results
    
    await ctx.send("🔄 Refreshing from Winston...")
    cached_results = get_winston_picks()
    
    if cached_results:
        await ctx.send(jarvis(f"✅ Loaded {len(cached_results)} fresh picks from Winston!"))
    else:
        await ctx.send(jarvis("⚠️ No picks available. Winston might be updating, try again in a moment."))

@bot.command()
async def help_commands(ctx):
    """Show available commands"""
    msg = (
        "🤖 **Jarvis Commands:**\n\n"
        "`!top` - Top 10 highest edge picks\n"
        "`!mine` - Get a 2-leg parlay build\n"
        "`!why <player>` - Detailed breakdown for a player\n"
        "`!stats` - Today's overall stats\n"
        "`!refresh` - Manually sync with Winston\n"
        "`!help_commands` - Show this menu\n\n"
        "Powered by Winston 🧠"
    )
    await ctx.send(msg)

# ------------------ RUN ------------------

if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERROR: DISCORD_BOT_TOKEN not set in environment variables")
        exit(1)
    
    print("🚀 Starting Jarvis Discord Bot...")
    print(f"🔗 Winston API: {WINSTON_API_URL}")
    
    bot.run(TOKEN)
```
