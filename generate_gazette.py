import json
from datetime import datetime
from pathlib import Path

SEASON=2026
src=Path("data")/str(SEASON)/"latest.json"
out=Path("gazette"); out.mkdir(exist_ok=True)
d=json.loads(src.read_text(encoding="utf-8"))
members={m["id"]:m for m in d.get("members",[])}
teams={t["id"]:t for t in d.get("teams",[])}

def team_name(t):
    return t.get("name") or " ".join(x for x in [t.get("location"),t.get("nickname")] if x) or t.get("abbrev",f"Team {t['id']}")

def owner(t):
    ids=t.get("owners") or []
    if not ids:return ""
    m=members.get(ids[0],{})
    return (m.get("firstName","")+" "+m.get("lastName","")).strip()

scores=[]
for s in d.get("schedule",[]):
    h=s.get("home",{}); a=s.get("away",{})
    if not h or not a: continue
    hs=h.get("totalPoints",0) or 0; aps=a.get("totalPoints",0) or 0
    if hs==0 and aps==0: continue
    scores.append((s.get("matchupPeriodId",0),h.get("teamId"),hs,a.get("teamId"),aps))
week=max([x[0] for x in scores],default=0)
games=[x for x in scores if x[0]==week]
games.sort(key=lambda x:max(x[2],x[4]),reverse=True)

lines=[f"# Bago Block Gazette — Week {week}", "", f"*Season {SEASON} • Generated {datetime.now().strftime('%B %d, %Y')}*", "", "## Scoreboard", ""]
for _,hid,hs,aid,aps in games:
    hn=team_name(teams.get(hid,{"id":hid})); an=team_name(teams.get(aid,{"id":aid}))
    lines.append(f"- **{hn} {hs:.2f}** — {an} {aps:.2f}" if hs>=aps else f"- **{an} {aps:.2f}** — {hn} {hs:.2f}")

if games:
    closest=min(games,key=lambda x:abs(x[2]-x[4]))
    blow=max(games,key=lambda x:abs(x[2]-x[4]))
    high=max(games,key=lambda x:max(x[2],x[4]))
    def winner(g):
        _,h,hs,a,aps=g
        return team_name(teams.get(h if hs>=aps else a,{"id":h if hs>=aps else a}))
    lines += ["", "## Weekly Hardware", "",
      f"- **Game of the Week:** {team_name(teams.get(closest[1],{'id':closest[1]}))} vs. {team_name(teams.get(closest[3],{'id':closest[3]}))} — margin {abs(closest[2]-closest[4]):.2f}",
      f"- **Ass-Kicking of the Week:** {winner(blow)} — won by {abs(blow[2]-blow[4]):.2f}",
      f"- **Top Score:** {winner(high)} — {max(high[2],high[4]):.2f} points"]

stand=sorted(teams.values(),key=lambda t:(t.get("record",{}).get("overall",{}).get("wins",0),t.get("points",0)),reverse=True)
lines += ["", "## Standings", ""]
for i,t in enumerate(stand,1):
    r=t.get("record",{}).get("overall",{})
    lines.append(f"{i}. **{team_name(t)}** — {r.get('wins',0)}-{r.get('losses',0)}-{r.get('ties',0)}")

lines += ["", "---", "*Automatically generated from ESPN league data. More awards, rivalry history, records and trash-talk layers will build on the stored snapshots.*", ""]
text="\n".join(lines)
(out/"latest.md").write_text(text,encoding="utf-8")
(out/f"week-{week}.md").write_text(text,encoding="utf-8")
print(f"Generated Week {week} Gazette")
