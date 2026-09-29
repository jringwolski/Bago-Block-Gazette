import json
from collections import defaultdict
from pathlib import Path

ROOT=Path("data/historical")
IDS=Path("data/manager_identities.json")
LINEAGE=Path("data/league_lineage.json")

def team_name(t):
    return (t.get("name") or " ".join(x for x in [t.get("location"),t.get("nickname")] if x) or t.get("abbrev",f"Team {t.get('id','?')}")).strip()

def norm(s):
    return " ".join((s or "").replace("’","'").split()).casefold()

def identity_lookup():
    cfg=json.loads(IDS.read_text(encoding="utf-8"))
    out={}
    for m in cfg["managers"]:
        for year,name in m.get("teams",{}).items():
            out[(int(year),norm(name))]=(m["canonical"],m["display"],name)
    return out

def main():
    lookup=identity_lookup()
    lineage=json.loads(LINEAGE.read_text(encoding="utf-8"))
    auth={int(x["season"]):str(x["leagueId"]) for x in lineage["authoritative"]}
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    got={int(x["season"]):str(x["leagueId"]) for x in manifest["seasons"]}
    if got != auth:
        raise RuntimeError(f"Historical archive lineage mismatch. expected={auth} got={got}")

    career=defaultdict(lambda:{"wins":0,"losses":0,"ties":0,"points_for":0.0,"games":0,"seasons":set()})
    games=[]; season_summaries={}; unresolved=[]
    for f in sorted(ROOT.glob("*/league.json")):
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
            hn=team_name(teams.get(hid,{"id":hid})); an=team_name(teams.get(aid,{"id":aid}))
            hi=lookup.get((y,norm(hn))); ai=lookup.get((y,norm(an)))
            if not hi or not ai:
                unresolved.append({"season":y,"week":wk,"home":hn,"away":an})
                continue
            hc,hd,_=hi; ac,ad,_=ai
            winner=hd if hs>aps else ad if aps>hs else "TIE"
            game={"season":y,"week":wk,"home_manager":hc,"home_display":hd,"home_team":hn,"home_score":hs,
                  "away_manager":ac,"away_display":ad,"away_team":an,"away_score":aps,
                  "winner":winner,"margin":round(abs(hs-aps),2),"certified":True}
            games.append(game); season_summaries[str(y)]["games"]+=1
            for c,dn,s in ((hc,hd,hs),(ac,ad,aps)):
                career[c]["display"]=dn; career[c]["points_for"]+=s; career[c]["games"]+=1; career[c]["seasons"].add(y)
            if hs>aps: career[hc]["wins"]+=1;career[ac]["losses"]+=1
            elif aps>hs: career[ac]["wins"]+=1;career[hc]["losses"]+=1
            else: career[hc]["ties"]+=1;career[ac]["ties"]+=1

    if unresolved:
        (ROOT/"unresolved_games.json").write_text(json.dumps(unresolved,indent=2),encoding="utf-8")
        raise RuntimeError(f"{len(unresolved)} games could not be mapped to canonical managers; refusing certification")

    scores=[]
    for g in games:
        scores += [{"manager":g["home_display"],"team":g["home_team"],"score":g["home_score"],"season":g["season"],"week":g["week"]},
                   {"manager":g["away_display"],"team":g["away_team"],"score":g["away_score"],"season":g["season"],"week":g["week"]}]
    records={}
    if games:
        records={"highest_score":max(scores,key=lambda x:x["score"]),"lowest_score":min(scores,key=lambda x:x["score"]),
                 "biggest_blowout":max(games,key=lambda x:x["margin"]),"closest_game":min(games,key=lambda x:x["margin"])}
    outcareer={k:{**{x:v for x,v in val.items() if x!="seasons"},"seasons":sorted(val["seasons"]),"avg_points":round(val["points_for"]/val["games"],2) if val["games"] else 0} for k,val in career.items()}
    out={"certification":{"status":"CERTIFIED","policy":"Frozen completed-game master; append new completed games only after validation.","authoritative_lineage":lineage["authoritative"],"excluded":lineage.get("excluded",[])},
         "season_summaries":season_summaries,"career":outcareer,"records":records,"games":games}
    (ROOT/"master_games.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
    (ROOT/"all_time.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
    print("CERTIFIED master:",len(games),"games,",len(outcareer),"managers")
if __name__=="__main__":main()
