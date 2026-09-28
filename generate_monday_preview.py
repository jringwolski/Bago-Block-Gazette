import json
from datetime import datetime
from pathlib import Path

SEASON=2026
BENCH_SLOTS={20,21}
MNF_PRO_TEAMS={3:"CHI",21:"PHI"}

def tn(t):
    return (t.get("name") or " ".join(x for x in [t.get("location"),t.get("nickname")] if x) or t.get("abbrev",f"Team {t.get('id','?')}")).strip()

def matchup_roster(side, team):
    r=side.get("rosterForCurrentScoringPeriod") or side.get("roster") or {}
    entries=r.get("entries") or []
    if not entries:
        entries=((team or {}).get("roster") or {}).get("entries") or []
    return entries

def monday_players(side, team):
    out=[]
    for e in matchup_roster(side,team):
        if e.get("lineupSlotId") in BENCH_SLOTS:
            continue
        p=((e.get("playerPoolEntry") or {}).get("player") or {})
        pro=p.get("proTeamId")
        if pro in MNF_PRO_TEAMS:
            out.append(f"{p.get('fullName') or p.get('name') or 'Unknown'} ({MNF_PRO_TEAMS[pro]})")
    return out

def main():
    d=json.loads(Path(f"data/{SEASON}/latest.json").read_text())
    teams={t["id"]:t for t in d.get("teams",[])}
    week=int((d.get("_gazette") or {}).get("scoringPeriodId") or (d.get("status") or {}).get("currentScoringPeriod") or 0)
    if not week:
        week=max((g.get("matchupPeriodId",0) for g in d.get("schedule",[])),default=0)

    games=[]
    for g in d.get("schedule",[]):
        if g.get("matchupPeriodId")!=week:
            continue
        h,a=g.get("home",{}),g.get("away",{})
        if not h or not a:
            continue
        ht,at=teams.get(h.get("teamId"),{}),teams.get(a.get("teamId"),{})
        hs=float(h.get("totalPoints",0) or 0)
        aps=float(a.get("totalPoints",0) or 0)
        games.append({
            "home":tn(ht),"away":tn(at),
            "home_score":hs,"away_score":aps,
            "margin":abs(hs-aps),
            "home_mnf":monday_players(h,ht),
            "away_mnf":monday_players(a,at),
        })

    games.sort(key=lambda x:x["margin"])
    leaders=sorted(games,key=lambda x:max(x["home_score"],x["away_score"]),reverse=True)

    lines=[
        "# THE MONDAY HANGOVER",
        "### Sunday's damage is done. Monday night gets the last word.",
        "",
        f"**Bago Block Gazette • Week {week} • {datetime.now().strftime('%B %d, %Y')}**",
        "",
        "## WHAT HAPPENED SUNDAY",
        ""
    ]
    for g in leaders:
        leader=g["home"] if g["home_score"]>=g["away_score"] else g["away"]
        loser=g["away"] if leader==g["home"] else g["home"]
        ls=max(g["home_score"],g["away_score"]); rs=min(g["home_score"],g["away_score"])
        lines.append(f"- **{leader} {ls:.2f} — {loser} {rs:.2f}**")

    lines += ["","## SCOREBOARD",""]
    for g in games:
        lines.append(f"- **{g['away']} {g['away_score']:.2f}** at **{g['home']} {g['home_score']:.2f}** — margin **{g['margin']:.2f}**")

    lines += ["","## WHAT'S ON THE LINE TONIGHT","",
              "**Eagles at Bears — 8:15 PM ET.** These are the fantasy starters still capable of moving the Bago Block scoreboard tonight.",""]

    any_live=False
    for g in games:
        if not (g["home_mnf"] or g["away_mnf"]):
            continue
        any_live=True
        lines.append(f"### {g['away']} {g['away_score']:.2f} at {g['home']} {g['home_score']:.2f}")
        if g["away_mnf"]:
            lines.append(f"- **{g['away']} still has:** " + ", ".join(g["away_mnf"]))
        if g["home_mnf"]:
            lines.append(f"- **{g['home']} still has:** " + ", ".join(g["home_mnf"]))
        trail=g["away"] if g["away_score"]<g["home_score"] else g["home"]
        lines.append(f"- **Current gap:** {g['margin']:.2f}. **{trail}** needs at least that much swing tonight.")
        lines.append("")
    if not any_live:
        lines.append("- No active Eagles/Bears starters were identified in the current ESPN snapshot.")

    close=sorted(games,key=lambda x:x["margin"])[:3]
    lines += ["## MONDAY NIGHT SWEAT",""]
    for g in close:
        lines.append(f"- **{g['away']} vs. {g['home']}** — only **{g['margin']:.2f}** points apart.")

    lines += ["","## TOMORROW: THE VERDICT","",
              "**Final scores. Final standings. Hardware handed out. Excuses rejected.**",""]

    out=Path("gazette"); out.mkdir(exist_ok=True)
    text="\n".join(lines)
    (out/"monday-latest.md").write_text(text,encoding="utf-8")
    (out/f"week-{week}-monday-hangover.md").write_text(text,encoding="utf-8")
    print("Built The Monday Hangover for Week",week)

if __name__=="__main__":
    main()
