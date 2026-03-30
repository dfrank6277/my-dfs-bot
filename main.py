import requests
import os
import json
import discord
import asyncio
from discord.ext import commands, tasks

# ------------------ CONFIG ------------------

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

REFRESH_MINUTES = 5
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

# ------------------ DATA ------------------

TEAM_PACE = {
    "WAS": 103, "ATL": 102, "IND": 101,
    "LAL": 100, "PHX": 99,
    "NYK": 96, "CLE": 95, "MIN": 94
}

TEAM_DEF_POS = {
    "PG": 1.05, "SG": 1.04,
    "SF": 1.02, "PF": 0.98, "C": 0.97
}

# ------------------ FETCH PROPS ------------------

def get_props():
    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "player_points,player_rebounds,player_assists",
        "oddsFormat": "decimal"
    }

    r = requests.get(url, params=params)

    if r.status_code != 200:
        print("API error:", r.status_code)
        return []

    props = []
    data = r.json()

    for game in data:
        for book in game.get("bookmakers", []):
            for market in book.get("markets", []):
                stat = market.get("key")

                for outcome in market.get("outcomes", []):
                    player = outcome.get("description")
                    line = outcome.get("point")

                    if not player or line is None:
                        continue

                    key = f"{player}_{stat}"

                    # track line movement
                    old_line = line_history.get(key)
                    movement = None

                    if old_line:
                        movement = round(line - old_line, 2)

                    line_history[key] = line

                    props.append({
                        "player": player,
                        "stat": stat,
                        "line": float(line),
                        "movement": movement,
                        "team": "UNK",
                        "position": "SF"
                    })

    save_json(LINES_FILE, line_history)
    return props

# ------------------ HELPERS ------------------

def normalize(stat):
    if "points" in stat: return "points"
    if "rebounds" in stat: return "rebounds"
    if "assists" in stat: return "assists"
    return "other"

def get_recent(player, stat):
    try:
        s = requests.get("https://www.balldontlie.io/api/v1/players",
                         params={"search": player}).json()

        if not s["data"]:
            return 20

        pid = s["data"][0]["id"]

        stats = requests.get(
            "https://www.balldontlie.io/api/v1/stats",
            params={"player_ids[]": pid, "per_page": 5}
        ).json()

        games = stats.get("data", [])
        if not games:
            return 20

        if stat == "points":
            vals = [g["pts"] for g in games]
        elif stat == "rebounds":
            vals = [g["reb"] for g in games]
        elif stat == "assists":
            vals = [g["ast"] for g in games]
        else:
            return 20

        return sum(vals) / len(vals)

    except:
        return 20

# ------------------ MODEL ------------------

def project(p):
    stat = normalize(p["stat"])
    line = p["line"]

    recent = get_recent(p["player"], stat)
    pace = TEAM_PACE.get(p["team"], 100) / 100
    dvp = TEAM_DEF_POS.get(p["position"], 1.0)

    if stat == "points":
        base = recent * 0.6 + line * 0.4
    elif stat == "rebounds":
        base = recent * 0.7 + line * 0.3
    elif stat == "assists":
        base = recent * 0.65 + line * 0.35
    else:
        base = line

    return round(base * pace * dvp, 2), recent, pace, dvp

def confidence(edge, pace, dvp):
    score = 0
    if abs(edge) > 3: score += 0.4
    elif abs(edge) > 2: score += 0.3
    elif abs(edge) > 1: score += 0.2
    if pace > 1: score += 0.2
    if dvp > 1: score += 0.2
    return round(min(score, 1), 2)

def grade(edge, conf):
    e = abs(edge)
    if e >= 4 and conf >= 0.7: return "A"
    if e >= 2.5: return "B"
    if e >= 1.5: return "C"
    return "D"

# ------------------ ANALYZE ------------------

def analyze():
    props = get_props()
    results = []

    for p in props:
        proj, recent, pace, dvp = project(p)
        edge = round(proj - p["line"], 2)
        pick = "OVER" if edge > 0 else "UNDER"
        conf = confidence(edge, pace, dvp)
        g = grade(edge, conf)

        results.append({
            **p,
            "projection": proj,
            "recent": recent,
            "pace": pace,
            "dvp": dvp,
            "edge": edge,
            "pick": pick,
            "grade": g,
            "confidence": conf,
            "score": (abs(edge) ** 1.2) * conf
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)

# ------------------ AUTO LOOP ------------------

@tasks.loop(minutes=REFRESH_MINUTES)
async def auto_refresh():
    global cached_results
    cached_results = analyze()
    print("Auto-refreshed model")

# ------------------ COMMANDS ------------------

@bot.event
async def on_ready():
    print(f"Jarvis online as {bot.user}")
    auto_refresh.start()

@bot.command()
async def top(ctx):
    if not cached_results:
        await ctx.send("Still building the board...")
        return

    msg = "Top edges right now:\n\n"

    for r in cached_results[:10]:
        move = f" | Move: {r['movement']}" if r["movement"] else ""
        msg += f"{r['grade']} {r['player']} — {r['pick']} {r['line']} (Edge {r['edge']}){move}\n"

    await ctx.send(jarvis(msg))

@bot.command()
async def mine(ctx):
    best = [r for r in cached_results if r["grade"] in ["A", "B"]][:2]

    msg = "2-leg build with strongest value:\n\n"
    for r in best:
        msg += f"{r['player']} — {r['pick']} {r['line']} (Edge {r['edge']})\n"

    await ctx.send(jarvis(msg))

@bot.command()
async def why(ctx, *, name):
    for r in cached_results:
        if name.lower() in r["player"].lower():
            msg = (
                f"{r['player']} breakdown:\n\n"
                f"Line: {r['line']} → Projection: {r['projection']}\n"
                f"Recent: {round(r['recent'],1)}\n"
                f"Edge: {r['edge']} ({r['grade']})\n"
                f"Confidence: {r['confidence']}\n"
                f"Pace: {r['pace']} | Matchup: {r['dvp']}\n"
                f"Line movement: {r['movement']}"
            )
            await ctx.send(jarvis(msg))
            return

    await ctx.send("Not on the board.")

# ------------------ RUN ------------------

bot.run(TOKEN)
