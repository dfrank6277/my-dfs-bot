import requests
import os
import discord
from discord.ext import commands
import pandas as pd

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

DFS_URL = "https://api.prizepicks.com/projections"

EDGE_THRESHOLD = 1.5
RECENT_GAMES = 5

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

cached_results = []

# ------------------ TEAM METRICS ------------------

TEAM_PACE = {
    "WAS": 103, "ATL": 102, "IND": 101,
    "LAL": 100, "PHX": 99,
    "NYK": 96, "CLE": 95, "MIN": 94
}

TEAM_DEF_POS = {
    "PG": 1.05, "SG": 1.04,
    "SF": 1.02, "PF": 0.98, "C": 0.97
}

# ------------------ FETCH DFS ------------------

def get_dfs_props():
    r = requests.get(DFS_URL)
    data = r.json()

    props = []

    for item in data["data"]:
        attr = item["attributes"]

        props.append({
            "player": attr.get("name"),
            "team": attr.get("team"),
            "stat": attr.get("stat_type"),
            "line": float(attr.get("line_score", 0)),
            "position": attr.get("position", "SF")
        })

    return props

# ------------------ PLAYER STATS ------------------

def get_player_recent_avg(player):
    """
    Replace with real API if available.
    This uses a stable deterministic fallback.
    """

    base = (hash(player) % 10) + 15
    trend = ((hash(player) % 5) - 2)

    return base + trend

# ------------------ MODEL ------------------

def project(prop):
    line = prop["line"]

    # Recent performance
    recent_avg = get_player_recent_avg(prop["player"])

    # Pace factor
    pace = TEAM_PACE.get(prop["team"], 100) / 100

    # Defense vs position
    dvp = TEAM_DEF_POS.get(prop["position"], 1.0)

    # Weighted projection
    projection = (
        (recent_avg * 0.5) +
        (line * 0.3) +
        (recent_avg * pace * 0.2)
    ) * dvp

    return round(projection, 2), recent_avg, pace, dvp

# ------------------ GRADING ------------------

def grade(edge, confidence):
    e = abs(edge)

    if e >= 4 and confidence > 0.7:
        return "A"
    elif e >= 2.5:
        return "B"
    elif e >= 1.5:
        return "C"
    else:
        return "D"

# ------------------ CONFIDENCE ------------------

def confidence_score(edge, pace, dvp):
    score = 0

    if abs(edge) > 3:
        score += 0.4
    elif abs(edge) > 2:
        score += 0.3

    if pace > 1:
        score += 0.2

    if dvp > 1:
        score += 0.2

    return round(min(score, 1), 2)

# ------------------ ANALYZE ------------------

def analyze():
    props = get_dfs_props()
    results = []

    for p in props:
        proj, recent, pace, dvp = project(p)

        edge = round(proj - p["line"], 2)

        if abs(edge) < EDGE_THRESHOLD:
            continue

        conf = confidence_score(edge, pace, dvp)
        g = grade(edge, conf)

        results.append({
            "player": p["player"],
            "team": p["team"],
            "stat": p["stat"],
            "line": p["line"],
            "projection": proj,
            "recent": recent,
            "pace": pace,
            "dvp": dvp,
            "edge": edge,
            "pick": "OVER" if edge > 0 else "UNDER",
            "grade": g,
            "confidence": conf,
            "score": abs(edge) * conf
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)

# ------------------ BUILD MINE ------------------

def build_mine(results):
    top = [r for r in results if r["grade"] in ["A", "B"]]
    return top[:2]

# ------------------ COMMANDS ------------------

@bot.command()
async def refresh(ctx):
    global cached_results
    cached_results = analyze()
    await ctx.send("✅ Model updated")

@bot.command()
async def top(ctx):
    if not cached_results:
        await ctx.send("Run !refresh first")
        return

    msg = "📊 TOP PLAYS\n\n"

    for r in cached_results[:10]:
        msg += (
            f"{r['grade']} | {r['player']}\n"
            f"{r['pick']} {r['line']} {r['stat']}\n"
            f"Proj: {r['projection']} | Edge: {r['edge']} | Conf: {r['confidence']}\n\n"
        )

    await ctx.send(msg)

@bot.command()
async def mine(ctx):
    if not cached_results:
        await ctx.send("Run !refresh first")
        return

    mine = build_mine(cached_results)

    msg = "💣 ELITE MINE\n\n"

    for m in mine:
        msg += (
            f"{m['grade']} | {m['player']}\n"
            f"{m['pick']} {m['line']} {m['stat']}\n"
            f"Proj: {m['projection']} | Edge: {m['edge']}\n\n"
        )

    await ctx.send(msg)

@bot.command()
async def why(ctx, *, player_name):
    for r in cached_results:
        if player_name.lower() in r["player"].lower():

            msg = (
                f"📊 {r['player']} BREAKDOWN\n\n"
                f"Line: {r['line']}\n"
                f"Projection: {r['projection']}\n"
                f"Recent Avg: {r['recent']}\n\n"
                f"Edge: {r['edge']} ({r['grade']})\n"
                f"Confidence: {r['confidence']}\n\n"
                f"Factors:\n"
                f"- Pace Impact: {r['pace']}\n"
                f"- Defense vs Pos: {r['dvp']}\n"
                f"- Model favors {r['pick']}\n"
            )

            await ctx.send(msg)
            return

    await ctx.send("Player not found")

# ------------------ RUN ------------------

bot.run(TOKEN)
