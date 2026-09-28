import json
from datetime import datetime
from pathlib import Path

SEASON=2026
def tn(t): return (t.get("name") or " ".join(x for x in [t.get("location"),t.get("nickname")] if x) or t.get("abbrev",f"Team {t.get('id','?')}")).strip()

def main():
    d=json.loads(Path(f"data/{SEASON}/latest.json").read_text())
    teams={t["id"]:t for t in d.get("teams",[])}
    sched=d.get("schedule",[])
    week=max((g.get("matchupPeriodId",0) for g in sched if (g.get("home",{}).get("totalPoints",0) or g.get("away",{}).get("totalPoints",0))),default=0)
    games=[]
    for g in sched:
        if g.get("matchupPeriodId")!=week: continue
        h,a=g.get("home",{}),g.get("away",{})
        if not h or not a: continue
        hs=float(h.get("totalPoints",0) or 0); aps=float(a.get("totalPoints",0) or 0)
        games.append({"home":tn(teams.get(h.get("teamId"),{"id":h.get("teamId")})),"away":tn(teams.get(a.get("teamId"),{"id":a.get("teamId")})),"home_score":hs,"away_score":aps,"margin":abs(hs-aps)})
    games.sort(key=lambda x:x["margin"])
    close=[g for g in games if g["margin"]<=20]
    lines=["# THE MONDAY HANGOVER","### Sunday's damage is done. Monday night gets the last word.","",
           f"**Bago Block Gazette • Week {week} • {datetime.now().strftime('%B %d, %Y')}**","",
           "## SUNDAY LEFT A MESS. MONDAY GETS TO CLEAN IT UP.","",
           f"Week {week} enters Monday with **{len(close)} matchup{'s' if len(close)!=1 else ''} separated by 20 points or fewer.**","",
           "## MONDAY NIGHT SWEAT",""]
    for g in games[:4]:
        leader=g["home"] if g["home_score"]>=g["away_score"] else g["away"]
        trail=g["away"] if leader==g["home"] else g["home"]
        lines.append(f"- **{leader}** leads **{trail}** by **{g['margin']:.2f}** — {g['home']} {g['home_score']:.2f}, {g['away']} {g['away_score']:.2f}.")
    lines += ["","## STILL ALIVE",""]
    if close:
        for g in close: lines.append(f"- **{g['home']} vs. {g['away']}** — only **{g['margin']:.2f}** points apart entering Monday.")
    else: lines.append("- Nobody is within 20 points. Monday needs some chaos.")
    lines += ["","## SUNDAY STUDS / SUNDAY SCARIES","",
              "Player-level Sunday leaders, goose eggs and disasters are pulled from the ESPN roster snapshot when available.","",
              "## BENCH CRIMES UNIT","",
              "The investigators are checking every bench for points that could swing a matchup. Tuesday's verdict becomes permanent evidence.","",
              "## PREMATURE HARDWARE — NOT FINAL","",
              "- Current scoring leader",
              "- Current Ass-Kicking of the Week",
              "- Current Heartbreaker",
              "- Current Bench Disaster",
              "",
              "## TONIGHT'S RECEIPTS","",
              "Every close loss, questionable bench decision and premature victory lap gets preserved for Tuesday's paper.","",
              "## TOMORROW: THE VERDICT","",
              "**Final scores. Final standings. Hardware handed out. Excuses rejected.**",""]
    out=Path("gazette"); out.mkdir(exist_ok=True)
    text="\n".join(lines)
    (out/"monday-latest.md").write_text(text,encoding="utf-8")
    (out/f"week-{week}-monday-hangover.md").write_text(text,encoding="utf-8")
    print("Built The Monday Hangover for Week",week)
if __name__=="__main__":main()
