import json
from pathlib import Path

def team_name(teams, team_id):
    t = teams.get(team_id, {"id": team_id})
    return (t.get("name") or " ".join(x for x in [t.get("location"), t.get("nickname")] if x) or t.get("abbrev", str(team_id))).strip()

def award_week(games, teams, week):
    games = [g for g in games if g[0] == week]
    if not games:
        return None

    def n(i): return team_name(teams, i)
    def winner(g): return n(g[1] if g[2] >= g[4] else g[3])
    def loser(g): return n(g[3] if g[2] >= g[4] else g[1])

    closest = min(games, key=lambda x: abs(x[2] - x[4]))
    blowout = max(games, key=lambda x: abs(x[2] - x[4]))
    all_scores = [(g[2], g[1]) for g in games] + [(g[4], g[3]) for g in games]
    high_score, high_team = max(all_scores, key=lambda x: x[0])
    low_score, low_team = min(all_scores, key=lambda x: x[0])

    return {
        "week": week,
        "nuclear_performance": {"team": n(high_team), "score": round(high_score, 2)},
        "dumpster_fire": {"team": n(low_team), "score": round(low_score, 2)},
        "akow": {
            "winner": winner(blowout),
            "victim": loser(blowout),
            "margin": round(abs(blowout[2] - blowout[4]), 2),
        },
        "heartbreak": {"team": loser(closest), "margin": round(abs(closest[2] - closest[4]), 2)},
        "escape_artist": {"team": winner(closest), "margin": round(abs(closest[2] - closest[4]), 2)},
    }

def main():
    p = Path("data/2026/latest.json")
    if not p.exists():
        return

    d = json.loads(p.read_text(encoding="utf-8"))
    teams = {t["id"]: t for t in d.get("teams", [])}
    games = []
    for g in d.get("schedule", []):
        h, a = g.get("home", {}), g.get("away", {})
        if not h or not a:
            continue
        hs, aps = h.get("totalPoints", 0) or 0, a.get("totalPoints", 0) or 0
        if hs or aps:
            games.append((g.get("matchupPeriodId", 0), h.get("teamId"), hs, a.get("teamId"), aps))

    if not games:
        return

    current_scoring_period = int((d.get("_gazette") or {}).get("scoringPeriodId") or 0)
    completed_weeks = sorted({
        g[0] for g in games
        if g[0] > 0 and (not current_scoring_period or g[0] < current_scoring_period)
    })

    weekly = [award_week(games, teams, w) for w in completed_weeks]
    weekly = [x for x in weekly if x]

    Path("data/2026/weekly_awards.json").write_text(
        json.dumps({"season": 2026, "completed_through_week": max(completed_weeks, default=0), "weeks": weekly}, indent=2),
        encoding="utf-8",
    )

    # Preserve the existing awards.json contract for the most recent completed week.
    if weekly:
        last = weekly[-1]
        legacy = {
            "week": last["week"],
            "game_of_week": {
                "teams": [last["escape_artist"]["team"], last["heartbreak"]["team"]],
                "margin": last["escape_artist"]["margin"],
            },
            "ass_kicking": {
                "winner": last["akow"]["winner"],
                "victim": last["akow"]["victim"],
                "margin": last["akow"]["margin"],
            },
            "high_score": {
                "team": last["nuclear_performance"]["team"],
                "score": last["nuclear_performance"]["score"],
            },
            "low_score": {
                "team": last["dumpster_fire"]["team"],
                "score": last["dumpster_fire"]["score"],
            },
            "heartbreaker": {
                "team": last["heartbreak"]["team"],
                "margin": last["heartbreak"]["margin"],
            },
        }
        Path("data/2026/awards.json").write_text(json.dumps(legacy, indent=2), encoding="utf-8")

    print(f"Built weekly awards through Week {max(completed_weeks, default=0)}")

if __name__ == "__main__":
    main()
