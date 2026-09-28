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
 lines=[f"# Bago Block Monday Morning Edition — Week {week}","",f"*Sunday wrap-up • generated {datetime.now().strftime('%B %d, %Y')}*","",
 "## Sunday Night State of the League",""]
 if games:
  close=[g for g in games if g["margin"]<=20]
  lines.append(f"Week {week} heads into Monday with **{len(close)} matchup{'s' if len(close)!=1 else ''} within 20 points**.")
  lines += ["","## Down to the Wire Tonight",""]
  for g in games[:4]:
   leader=g["home"] if g["home_score"]>=g["away_score"] else g["away"]
   trail=g["away"] if leader==g["home"] else g["home"]
   lines.append(f"- **{leader}** leads {trail} by **{g['margin']:.2f}** ({g['home']} {g['home_score']:.2f}, {g['away']} {g['away_score']:.2f}).")
 lines += ["","## What to Watch Monday Night","",
 "- Which close matchup flips before the final whistle.",
 "- Whether any manager gets burned by points left on the bench.",
 "- The week's scoring crown and low-score punishment are still provisional until Monday night is complete.",
 "- Tuesday's full Gazette locks the final scores, awards, standings, records and receipts.","",
 "## Tuesday Morning","",
 "The full **Bago Block Gazette** publishes after Monday Night Football with the official weekly autopsy.",""]
 out=Path("gazette");out.mkdir(exist_ok=True)
 (out/"monday-latest.md").write_text("\n".join(lines),encoding="utf-8")
 (out/f"week-{week}-monday-preview.md").write_text("\n".join(lines),encoding="utf-8")
 print("Built Monday morning edition for Week",week)
if __name__=="__main__":main()
