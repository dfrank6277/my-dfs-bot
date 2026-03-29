import requests
import os
import discord
from discord.ext import commands

# ------------------ CONFIG ------------------

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

cached_results = []

# ------------------ TEAM DATA ------------------

TEAM_PACE = {
    "WAS": 103, "ATL": 102, "IND": 101,
    "LAL": 100, "PHX": 99,
    "NYK": 96, "CLE": 95, "MIN": 94
}

TEAM_DEF_POS = {
    "PG": 1.05, "SG": 1.04,
    "SF": 1.02, "PF": 0.98, "C": 0.97
}

# ------------------ FETCH REAL PROPS ------------------

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
        print("Odds API error:", r.status_code)
        return []

    data = r.json()
    props = []

    for game in data:
        for book in game.get("bookmakers", []):
            for market in book.get("markets", []):
                stat = market.get("key")

                for outcome in market.get("outcomes", []):
                    player = outcome.get("description")
                    line = outcome.get("point")

                    if not player or line is None:
                        continue

                    props.append({
                        "player": player,
                        "team": "UNK",
                        "stat": stat,
                        "line": float(line),
                        "position": "SF"
                    })

    return props

# ------------------ NORMALIZE STAT ------------------

def normalize_stat(stat):
    if "points" in stat:
        return "points"
    elif "rebounds" in stat:
        return "rebounds"
    elif "assists" in stat:
        return "assists"
    else:
        return "other"

# ------------------ REAL PLAYER DATA ------------------

def get_player_recent_avg(player):
    try:
        search = requests.get(
            "https://www.balldontlie.io/api/v1/players",
            params={"search": player}
        ).json()

        if not search["data"]:
            return 20

        player_id = search["data"][0]["id"]

        stats = requests.get(
            "https://www.balldontlie.io/api/v1/stats",
            params={
                "player_ids[]": player_id,
                "per_page": 5
            }
        ).json()

        games = stats.get("data", [])

        if not games:
            return 20

        pts = [g["pts"] for g in games]
        return sum(pts) / len(pts)

    except:
        return 20

# ------------------ PROJECTION MODEL ------------------

def project(prop):
    stat_type = normalize_stat(prop["stat"])
    line = prop["line"]

    recent = get_player_recent_avg(prop["player"])
    pace = TEAM_PACE.get(prop["team"], 100) / 100
    dvp = TEAM_DEF_POS.get(prop["position"], 1.0)

    if stat_type == "points":
        proj = recent * 0.6 + line * 0.4
    elif stat_type == "rebounds":
        proj = recent * 0.7 + line * 0.3
    elif stat_type == "assists":
        proj = recent * 0.65 + line * 0.35
    else:
        proj = line

    projection = proj * pace * dvp

    return round(projection, 2), recent, pace, dvp

# ------------------ CONFIDENCE ------------------

def confidence_score(edge, pace, dvp):
    score = 0

    if abs(edge) > 3:
        score += 0.4
    elif abs(edge) > 2:
        score += 0.3
    elif abs(edge) > 1:
        score += 0.2

    if pace > 1:
        score += 0.2

    if dvp > 1:
        score += 0.2

    return round(min(score, 1), 2)

# ------------------ GRADING ------------------

def grade(edge, confidence):
    e = abs(edge)

    if e >= 4 and confidence >= 0.7:
        return "A"
    elif e >= 2.5:
        return "B"
    elif e >= 1.5:
        return "C"
    else:
        return "D"

# ------------------ ANALYSIS ------------------

def analyze():
    props = get_props()
    results = []

    for p in props:
        proj, recent, pace, dvp = project(p)
        edge = round(proj - p["line"], 2)

        pick = "OVER" if edge > 0 else "UNDER"
        conf = confidence_score(edge, pace, dvp)
        g = grade(edge, conf)

        results.append({
            "player": p["player"],
            "stat": p["stat"],
            "line": p["line"],
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

# ------------------ BUILD MINE ------------------

def build_mine(results):
    top = [r for r in results if r["grade"] in ["A", "B"]]
    return top[:2]

# ------------------ DISCORD COMMANDS ------------------

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def refresh(ctx):
    global cached_results
    cached_results = analyze()
    await ctx.send("✅ Model refreshed")

@bot.command()
async def top(ctx):
    if not cached_results:
        await ctx.send("Run !refresh first")
        return

    msg = "📊 TOP PLAYS\n\n"

    for r in cached_results[:15]:
        msg += (
            f"{r['grade']} | {r['player']} ({r['stat']})\n"
            f"{r['pick']} {r['line']}\n"
            f"Proj: {r['projection']} | Edge: {r['edge']} | Conf: {r['confidence']}\n\n"
        )

    await ctx.send(msg)

@bot.command()
async def mine(ctx):
    if not cached_results:
        await ctx.send("Run !refresh first")
        return

    mine = build_mine(cached_results)

    msg = "💣 BEST 2-PICK\n\n"

    for m in mine:
        msg += (
            f"{m['grade']} | {m['player']} ({m['stat']})\n"
            f"{m['pick']} {m['line']}\n"
            f"Proj: {m['projection']} | Edge: {m['edge']}\n\n"
        )

    await ctx.send(msg)

@bot.command()
async def why(ctx, *, player_name):
    for r in cached_results:
        if player_name.lower() in r["player"].lower():

            msg = (
                f"📊 {r['player']} ANALYSIS\n\n"
                f"Stat: {r['stat']}\n"
                f"Line: {r['line']}\n"
                f"Projection: {r['projection']}\n"
                f"Recent Avg: {r['recent']}\n\n"
                f"Pick: {r['pick']} ({r['grade']})\n"
                f"Edge: {r['edge']} | Confidence: {r['confidence']}\n\n"
                f"Pace: {r['pace']} | DvP: {r['dvp']}"
            )

            await ctx.send(msg)
            return

    await ctx.send("Player not found")

# ------------------ RUN ------------------

bot.run(TOKEN)
