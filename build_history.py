import json
from pathlib import Path

def main():
    games=[]
    for f in sorted(Path("data").glob("*/snapshot-*.json")):
        d=json.loads(f.read_text(encoding="utf-8"))
        teams={t["id"]:t for t in d.get("teams",[])}
        for g in d.get("schedule",[]):
            h=g.get("home",{}); a=g.get("away",{})
            if not h or not a: continue
            hs=h.get("totalPoints",0) or 0; aps=a.get("totalPoints",0) or 0
            if hs==0 and aps==0: continue
            def name(i):
                t=teams.get(i,{"id":i})
                return t.get("name") or t.get("abbrev",str(i))
            games.append({"season":f.parent.name,"week":g.get("matchupPeriodId"),"home":name(h.get("teamId")),"home_score":hs,"away":name(a.get("teamId")),"away_score":aps})
    unique={(x["season"],x["week"],x["home"],x["away"]):x for x in games}
    games=list(unique.values())
    records={}
    if games:
        scores=[{"team":g["home"],"score":g["home_score"],"season":g["season"],"week":g["week"]} for g in games]+[{"team":g["away"],"score":g["away_score"],"season":g["season"],"week":g["week"]} for g in games]
        records["highest_score"]=max(scores,key=lambda x:x["score"])
        records["lowest_score"]=min(scores,key=lambda x:x["score"])
        records["biggest_blowout"]=max(games,key=lambda x:abs(x["home_score"]-x["away_score"]))
        records["closest_game"]=min(games,key=lambda x:abs(x["home_score"]-x["away_score"]))
    Path("data/history.json").write_text(json.dumps({"games":games,"records":records},indent=2),encoding="utf-8")
    print("Historical games:",len(games))
if __name__=="__main__":main()
