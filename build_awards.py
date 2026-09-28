import json
from pathlib import Path

def main():
    p=Path("data/2026/latest.json")
    if not p.exists(): return
    d=json.loads(p.read_text()); teams={t["id"]:t for t in d.get("teams",[])}
    games=[]
    for g in d.get("schedule",[]):
        h=g.get("home",{});a=g.get("away",{})
        if not a or not h:continue
        hs=h.get("totalPoints",0) or 0; aps=a.get("totalPoints",0) or 0
        if hs or aps:games.append((g.get("matchupPeriodId",0),h.get("teamId"),hs,a.get("teamId"),aps))
    if not games:return
    w=max(x[0] for x in games); games=[x for x in games if x[0]==w]
    def n(i): 
        t=teams.get(i,{"id":i}); return t.get("name") or " ".join(x for x in [t.get("location"),t.get("nickname")] if x) or t.get("abbrev",str(i))
    closest=min(games,key=lambda x:abs(x[2]-x[4])); blow=max(games,key=lambda x:abs(x[2]-x[4]))
    high=max(games,key=lambda x:max(x[2],x[4])); low=min(games,key=lambda x:min(x[2],x[4]))
    def win(g):return n(g[1] if g[2]>=g[4] else g[3])
    def lose(g):return n(g[3] if g[2]>=g[4] else g[1])
    a={"week":w,"game_of_week":{"teams":[n(closest[1]),n(closest[3])],"margin":abs(closest[2]-closest[4])},
       "ass_kicking":{"winner":win(blow),"victim":lose(blow),"margin":abs(blow[2]-blow[4])},
       "high_score":{"team":win(high),"score":max(high[2],high[4])},
       "low_score":{"team":lose(low),"score":min(low[2],low[4])},
       "heartbreaker":{"team":lose(closest),"margin":abs(closest[2]-closest[4])}}
    Path("data/2026/awards.json").write_text(json.dumps(a,indent=2),encoding="utf-8")
if __name__=="__main__":main()
