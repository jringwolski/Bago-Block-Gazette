import json
from collections import defaultdict
from pathlib import Path

def name(t):
    return (t.get("name") or " ".join(x for x in [t.get("location"),t.get("nickname")] if x) or t.get("abbrev",f"Team {t.get('id','?')}")).strip()

def main():
    root=Path("data/historical")
    career=defaultdict(lambda:{"wins":0,"losses":0,"ties":0,"points_for":0.0,"games":0,"seasons":set()})
    games=[]; season_summaries={}
    for f in sorted(root.glob("*/league.json")):
        y=int(f.parent.name); d=json.loads(f.read_text()); teams={t["id"]:t for t in d.get("teams",[])}
        season_summaries[str(y)]={"teams":len(teams),"games":0}
        seen=set()
        for g in d.get("schedule",[]):
            wk=g.get("matchupPeriodId"); h=g.get("home") or {}; a=g.get("away") or {}
            if not h or not a: continue
            hid,aid=h.get("teamId"),a.get("teamId"); hs=float(h.get("totalPoints",0) or 0); aps=float(a.get("totalPoints",0) or 0)
            if not (hs or aps): continue
            key=(wk,hid,aid)
            if key in seen: continue
            seen.add(key)
            hn=name(teams.get(hid,{"id":hid})); an=name(teams.get(aid,{"id":aid}))
            games.append({"season":y,"week":wk,"home":hn,"home_score":hs,"away":an,"away_score":aps,"margin":abs(hs-aps)})
            season_summaries[str(y)]["games"]+=1
            for n,s in ((hn,hs),(an,aps)):
                career[n]["points_for"]+=s; career[n]["games"]+=1; career[n]["seasons"].add(y)
            if hs>aps: career[hn]["wins"]+=1;career[an]["losses"]+=1
            elif aps>hs: career[an]["wins"]+=1;career[hn]["losses"]+=1
            else: career[hn]["ties"]+=1;career[an]["ties"]+=1
    scores=[]
    for g in games:
        scores += [{"team":g["home"],"score":g["home_score"],"season":g["season"],"week":g["week"]},
                   {"team":g["away"],"score":g["away_score"],"season":g["season"],"week":g["week"]}]
    records={}
    if games:
        records={"highest_score":max(scores,key=lambda x:x["score"]),"lowest_score":min(scores,key=lambda x:x["score"]),
                 "biggest_blowout":max(games,key=lambda x:x["margin"]),"closest_game":min(games,key=lambda x:x["margin"])}
    outcareer={k:{**{x:v for x,v in val.items() if x!="seasons"},"seasons":sorted(val["seasons"]),"avg_points":round(val["points_for"]/val["games"],2) if val["games"] else 0} for k,val in career.items()}
    out={"season_summaries":season_summaries,"career":outcareer,"records":records,"games":games}
    (root/"all_time.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
    print("All-time database:",len(games),"games,",len(outcareer),"team identities")
if __name__=="__main__":main()
