import json, os, requests
from pathlib import Path

CURRENT=int(os.getenv("ESPN_SEASON","2026"))
VIEWS=["mTeam","mRoster","mMatchup","mMatchupScore","mSettings","mBoxscore","mStatus","mTransactions2"]
OUT=Path("data/historical"); OUT.mkdir(parents=True,exist_ok=True)
LINEAGE=Path("data/league_lineage.json")

def cookies():
    c={}
    if os.getenv("ESPN_S2"): c["espn_s2"]=os.getenv("ESPN_S2")
    if os.getenv("SWID"): c["SWID"]=os.getenv("SWID")
    return c

def fetch(year, league_id):
    url=f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}"
    r=requests.get(url,params=[("view",v) for v in VIEWS],cookies=cookies(),timeout=45)
    r.raise_for_status(); d=r.json()
    return d[0] if isinstance(d,list) else d

def owner_map(d,year):
    members={m.get("id"):m for m in d.get("members",[])}
    rows=[]
    for t in d.get("teams",[]):
        ids=t.get("owners") or ([t.get("primaryOwner")] if t.get("primaryOwner") else [])
        names=[]
        for oid in ids:
            m=members.get(oid,{})
            names.append(m.get("displayName") or " ".join(x for x in [m.get("firstName"),m.get("lastName")] if x) or oid)
        rows.append({"season":year,"team_id":t.get("id"),"team_name":t.get("name") or " ".join(x for x in [t.get("location"),t.get("nickname")] if x),"owner_ids":ids,"owner_names":names})
    return rows

def main():
    cfg=json.loads(LINEAGE.read_text(encoding="utf-8"))
    authoritative={int(x["season"]):str(x["leagueId"]) for x in cfg["authoritative"]}
    excluded={(int(x["season"]),str(x["leagueId"])) for x in cfg.get("excluded",[])}
    manifest={"currentSeason":CURRENT,"seasons":[],"excluded":cfg.get("excluded",[]),"notes":[]}
    identities=[]
    for year in sorted(authoritative):
        league_id=authoritative[year]
        if (year,league_id) in excluded:
            raise RuntimeError(f"Authoritative lineage points at excluded league: {year}/{league_id}")
        d=fetch(year,league_id)
        if not d.get("teams"): raise ValueError(f"{year}/{league_id}: no teams")
        p=OUT/str(year); p.mkdir(parents=True,exist_ok=True)
        (p/"league.json").write_text(json.dumps(d,indent=2),encoding="utf-8")
        manifest["seasons"].append({"season":year,"leagueId":league_id,"teams":len(d.get("teams",[])),"matchups":len(d.get("schedule",[]))})
        identities.extend(owner_map(d,year))
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    (OUT/"owner_identity_raw.json").write_text(json.dumps(identities,indent=2),encoding="utf-8")
    print(json.dumps(manifest,indent=2))
if __name__=="__main__": main()
