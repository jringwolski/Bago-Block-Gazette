import json
from pathlib import Path
from collections import defaultdict

SEASON=2026
def nm(t): return t.get("name") or " ".join(x for x in [t.get("location"),t.get("nickname")] if x) or t.get("abbrev",f"Team {t.get('id','?')}")

def main():
 p=Path(f"data/{SEASON}/latest.json"); d=json.loads(p.read_text()); teams={t["id"]:t for t in d.get("teams",[])}
 completed=[]
 for g in d.get("schedule",[]):
  h,a=g.get("home",{}),g.get("away",{})
  if not h or not a: continue
  hs,aps=h.get("totalPoints",0) or 0,a.get("totalPoints",0) or 0
  if hs or aps: completed.append((g.get("matchupPeriodId",0),h.get("teamId"),hs,a.get("teamId"),aps))
 week=max((g[0] for g in completed),default=0); games=[g for g in completed if g[0]==week]
 analysis={"week":week,"teams":{}}
 for t in teams.values():
  r=t.get("record",{}).get("overall",{})
  analysis["teams"][nm(t)]={"wins":r.get("wins",0),"losses":r.get("losses",0),"ties":r.get("ties",0),"points_for":r.get("pointsFor",t.get("points",0))}
 if games:
  margins=[(abs(g[2]-g[4]),g) for g in games]
  analysis["closest"]=min(margins,key=lambda x:x[0])[0]
  analysis["largest_margin"]=max(margins,key=lambda x:x[0])[0]
  analysis["league_high"]=max(max(g[2],g[4]) for g in games)
  analysis["league_low"]=min(min(g[2],g[4]) for g in games)
 Path(f"data/{SEASON}/analysis.json").write_text(json.dumps(analysis,indent=2),encoding="utf-8")
 print("Analysis built for week",week)
if __name__=="__main__": main()
