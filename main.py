import requests
import os

API_KEY = os.getenv("ODDS_API_KEY")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

SPORT = "basketball_nba"
MARKETS = ["player_points"]

BOOKMAKERS = "draftkings,fanduel,betmgm,caesars"
DFS_URL = "https://api.prizepicks.com/projections"

EDGE_THRESHOLD = 1.5

# ------------------ UTIL ------------------

def send_alert(message):
    if not WEBHOOK_URL:
        print(message)
        return

    requests.post(WEBHOOK_URL, json={"content": message})

def normalize(name):
    return name.lower().strip()

# ------------------ GRADING ------------------

def grade_prop(edge):
    abs_edge = abs(edge)

    score = 0

    if abs_edge >= 3:
        score += 5
    elif abs_edge >= 2:
        score += 4
    elif abs_edge >= 1.5:
        score += 3
    elif abs_edge >= 1:
        score += 2
    else:
        score += 1

    if score >= 5:
        return "A"
    elif score == 4:
        return "B"
    elif score == 3:
        return "C"
    else:
        return "D"

# ------------------ DFS DATA ------------------

def get_dfs_props():
    r = requests.get(DFS_URL)
    data = r.json()

    props = []

    for item in data["data"]:
        attr = item["attributes"]

        props.append({
            "player": attr.get("name"),
            "stat": attr.get("stat_type"),
            "line": attr.get("line_score")
        })

    return props

# ------------------ SPORTSBOOK DATA ------------------

def get_sportsbook_props():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"

    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": ",".join(MARKETS),
        "oddsFormat": "american",
        "bookmakers": BOOKMAKERS
    }

    r = requests.get(url, params=params)
    data = r.json()

    props = []

    for game in data:
        home = game["home_team"]
        away = game["away_team"]

        for book in game.get("bookmakers", []):
            for market in book.get("markets", []):
                for outcome in market.get("outcomes", []):

                    player = outcome.get("description")
                    line = outcome.get("point")

                    if not player or line is None:
                        continue

                    props.append({
                        "player": player,
                        "market": market["key"],
                        "line": line,
                        "game": f"{away} @ {home}"
                    })

    return props

# ------------------ EDGE DETECTION ------------------

def find_edges(sportsbook_props, dfs_props):
    edges = []

    dfs_map = {
        (normalize(p["player"]), p["stat"]): p
        for p in dfs_props
    }

    for prop in sportsbook_props:
        key = (normalize(prop["player"]), prop["market"])

        if key not in dfs_map:
            continue

        dfs_line = dfs_map[key]["line"]
        book_line = prop["line"]

        diff = book_line - dfs_line

        if abs(diff) < EDGE_THRESHOLD:
            continue

        pick = "OVER" if diff > 0 else "UNDER"
        grade = grade_prop(diff)

        edges.append({
            "player": prop["player"],
            "stat": prop["market"],
            "dfs_line": dfs_line,
            "book_line": book_line,
            "edge": round(diff, 2),
            "score": abs(diff),
            "pick": pick,
            "grade": grade,
            "game": prop["game"]
        })

    return sorted(edges, key=lambda x: x["score"], reverse=True)

# ------------------ RANKINGS ------------------

def send_rankings(edges):
    msg = "📊 DFS EDGE RANKINGS\n\n"

    for e in edges[:10]:
        msg += (
            f"{e['grade']} | {e['player']}\n"
            f"{e['pick']} {e['dfs_line']} {e['stat']}\n"
            f"Edge: {e['edge']}\n\n"
        )

    send_alert(msg)

# ------------------ SLIP BUILDER ------------------

def build_slips(edges):
    slips = []
    used_games = set()

    filtered = [e for e in edges if e["grade"] in ["A", "B"]]

    for edge in filtered:
        if edge["game"] in used_games:
            continue

        slip = [edge]
        used_games.add(edge["game"])

        for other in filtered:
            if other["game"] in used_games:
                continue

            slip.append(other)
            used_games.add(other["game"])

            if len(slip) == 2:
                break

        if len(slip) >= 2:
            slips.append(slip)

    return slips[:3]

# ------------------ DISCORD OUTPUT ------------------

def send_slip(slip):
    msg = "🎯 DFS SNIPER SLIP\n\n"

    for leg in slip:
        msg += (
            f"{leg['grade']} | {leg['player']}\n"
            f"{leg['pick']} {leg['dfs_line']} {leg['stat']}\n"
            f"Book: {leg['book_line']} | Edge: {leg['edge']}\n\n"
        )

    send_alert(msg)

# ------------------ MAIN ------------------

def main():
    print("Fetching DFS props...")
    dfs_props = get_dfs_props()

    print("Fetching sportsbook props...")
    sportsbook_props = get_sportsbook_props()

    print("Finding edges...")
    edges = find_edges(sportsbook_props, dfs_props)

    if not edges:
        send_alert("⚠️ No strong DFS edges found")
        return

    print(f"Found {len(edges)} edges")

    send_rankings(edges)

    slips = build_slips(edges)

    for slip in slips:
        send_slip(slip)

if __name__ == "__main__":
    main()
