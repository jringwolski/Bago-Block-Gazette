import json
from datetime import datetime
from pathlib import Path

SEASON=2026
def name(t): return (t.get("name") or " ".join(x for x in [t.get("location"),t.get("nickname")] if x) or t.get("abbrev",f"Team {t.get('id','?')}")).strip()

def main():
 d=json.loads((Path("data")/str(SEASON)/"latest.json").read_text(encoding="utf-8"))
 teams={t["id"]:t for t in d.get("teams",[])}
 games=[]
 for s in d.get("schedule",[]):
  h,a=s.get("home",{}),s.get("away",{})
  if not h or not a: continue
  hs,aps=h.get("totalPoints",0) or 0,a.get("totalPoints",0) or 0
  if hs or aps: games.append((s.get("matchupPeriodId",0),h.get("teamId"),hs,a.get("teamId"),aps))
 week=max((x[0] for x in games),default=0); games=[x for x in games if x[0]==week]
 closest=min(games,key=lambda x:abs(x[2]-x[4])); blow=max(games,key=lambda x:abs(x[2]-x[4])); high=max(games,key=lambda x:max(x[2],x[4]))
 def tn(i): return name(teams.get(i,{"id":i}))
 def winner(g): return tn(g[1] if g[2]>=g[4] else g[3])
 def loser(g): return tn(g[3] if g[2]>=g[4] else g[1])
 standings=sorted(teams.values(),key=lambda t:(t.get("record",{}).get("overall",{}).get("wins",0),t.get("record",{}).get("overall",{}).get("pointsFor",t.get("points",0))),reverse=True)
 lead=f"{winner(high).upper()} DROPS {max(high[2],high[4]):.2f}"
 lines=[f"# {lead}",f"*Bago Block Gazette — Week {week} • {datetime.now().strftime('%B %d, %Y')}*","",
 f"## Lead Story","",f"**{winner(high)}** owns the Week {week} front page after posting a league-best **{max(high[2],high[4]):.2f} points**.","",
 "## Week "+str(week)+" Scoreboard",""]
 for _,h,hs,a,aps in sorted(games,key=lambda x:max(x[2],x[4]),reverse=True):
  lines.append(f"- **{winner((week,h,hs,a,aps))}** {max(hs,aps):.2f} — {loser((week,h,hs,a,aps))} {min(hs,aps):.2f}")
 lines += ["","## Weekly Hardware","",
 f"- **Game of the Week:** {tn(closest[1])} {closest[2]:.2f} vs. {tn(closest[3])} {closest[4]:.2f} — decided by **{abs(closest[2]-closest[4]):.2f}**",
 f"- **Ass-Kicking of the Week:** {winner(blow)} over {loser(blow)} by **{abs(blow[2]-blow[4]):.2f}**",
 f"- **Heartbreaker:** {loser(closest)} — lost by **{abs(closest[2]-closest[4]):.2f}**",
 f"- **High Score:** {winner(high)} — **{max(high[2],high[4]):.2f}**","",
 "## Standings",""]
 for i,t in enumerate(standings,1):
  r=t.get("record",{}).get("overall",{}); pf=r.get("pointsFor",t.get("points",0))
  lines.append(f"{i}. **{name(t)}** — {r.get('wins',0)}-{r.get('losses',0)} | {pf:.2f} PF")
 hist=Path("data/history.json")
 if hist.exists():
  rec=json.loads(hist.read_text()).get("records",{})
  lines += ["","## Record Book",""]
  if rec.get("highest_score"): x=rec["highest_score"]; lines.append(f"- **Season high:** {x['team']} — {x['score']:.2f} (Week {x['week']})")
  if rec.get("lowest_score"): x=rec["lowest_score"]; lines.append(f"- **Season low:** {x['team']} — {x['score']:.2f} (Week {x['week']})")
  if rec.get("biggest_blowout"):
   x=rec["biggest_blowout"]
   margin=x.get("margin",abs(x.get("home_score",0)-x.get("away_score",0)))
   home=x.get("home") or x.get("home_team") or x.get("home_display","Home")
   away=x.get("away") or x.get("away_team") or x.get("away_display","Away")
   lines.append(f"- **Biggest blowout:** {margin:.2f} points — {home} vs. {away} (Week {x['week']})")
 text="\n".join(lines)+"\n"; out=Path("gazette");out.mkdir(exist_ok=True)
 (out/"latest.md").write_text(text,encoding="utf-8");(out/f"week-{week}.md").write_text(text,encoding="utf-8")
if __name__=="__main__":main()
