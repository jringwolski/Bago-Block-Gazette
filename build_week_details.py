import json
from pathlib import Path

SEASON=2026
BENCH_SLOTS={20,21}

def team_name(t):
    return (t.get("name") or " ".join(x for x in [t.get("location"),t.get("nickname")] if x) or t.get("abbrev",f"Team {t.get('id','?')}")).strip()

def player_points(player, week):
    stats=player.get("stats") or []
    candidates=[]
    for s in stats:
        if s.get("scoringPeriodId")==week:
            val=s.get("appliedTotal")
            if val is not None:
                candidates.append((s.get("statSourceId",99),s.get("statSplitTypeId",99),float(val)))
    if not candidates:
        return 0.0
    candidates.sort(key=lambda x:(x[0]!=0,x[1]!=1,x[0],x[1]))
    return candidates[0][2]

def entries_from_side(side):
    r=side.get("rosterForCurrentScoringPeriod") or side.get("roster") or {}
    return r.get("entries") or []

def main():
    d=json.loads(Path(f"data/{SEASON}/latest.json").read_text(encoding="utf-8"))
    teams={t["id"]:t for t in d.get("teams",[])}
    out={}
    completed_weeks = sorted({int(g.get("matchupPeriodId")) for g in d.get("schedule",[]) if g.get("matchupPeriodId") and (g.get("home") or {}).get("totalPoints") is not None and (g.get("away") or {}).get("totalPoints") is not None})\n    for week in completed_weeks:
        rows=[]
        team_summaries={}
        for g in d.get("schedule",[]):
            if g.get("matchupPeriodId")!=week: continue
            for side_key in ("home","away"):
                side=g.get(side_key) or {}
                tid=side.get("teamId")
                if tid is None: continue
                tname=team_name(teams.get(tid,{"id":tid}))
                entries=entries_from_side(side)
                # Fallback to current roster only when matchup-specific roster is absent.
                if not entries:
                    entries=((teams.get(tid,{}) or {}).get("roster") or {}).get("entries") or []
                plist=[]
                for e in entries:
                    ppe=e.get("playerPoolEntry") or {}
                    p=ppe.get("player") or {}
                    pname=p.get("fullName") or p.get("name")
                    if not pname: continue
                    pts=player_points(p,week)
                    slot=e.get("lineupSlotId")
                    starter=slot not in BENCH_SLOTS
                    rec={"team":tname,"player":pname,"points":round(pts,2),"lineupSlotId":slot,"starter":starter}
                    rows.append(rec); plist.append(rec)
                team_summaries[tname]={
                    "starter_points":round(sum(x["points"] for x in plist if x["starter"]),2),
                    "bench_points":round(sum(x["points"] for x in plist if not x["starter"]),2),
                    "top_bench":max((x for x in plist if not x["starter"]),key=lambda x:x["points"],default=None),
                    "top_starter":max((x for x in plist if x["starter"]),key=lambda x:x["points"],default=None)
                }
        starters=[x for x in rows if x["starter"]]
        bench=[x for x in rows if not x["starter"]]
        out[str(week)]={
            "week":week,
            "player_of_week":max(starters,key=lambda x:x["points"],default=None),
            "bench_player_of_week":max(bench,key=lambda x:x["points"],default=None),
            "bench_disaster":max(team_summaries.items(),key=lambda kv:kv[1]["bench_points"],default=(None,None)),
            "teams":team_summaries,
            "players":sorted(rows,key=lambda x:x["points"],reverse=True)
        }
    Path(f"data/{SEASON}/week_details.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
    for week,val in out.items():
        Path(f"data/{SEASON}/week-{week}-details.json").write_text(json.dumps(val,indent=2),encoding="utf-8")
    print(f"Built detailed player reports for completed weeks: {completed_weeks}")
if __name__=="__main__": main()
