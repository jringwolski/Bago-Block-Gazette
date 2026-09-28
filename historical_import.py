import json, os, requests
from pathlib import Path

LEAGUE_ID=os.getenv("ESPN_LEAGUE_ID","1724229206")
CURRENT=int(os.getenv("ESPN_SEASON","2026"))
VIEWS=["mTeam","mRoster","mMatchup","mMatchupScore","mSettings","mBoxscore","mStatus","mTransactions2"]
OUT=Path("data/historical"); OUT.mkdir(parents=True,exist_ok=True)

def cookies():
    c={}
    if os.getenv("ESPN_S2"): c["espn_s2"]=os.getenv("ESPN_S2")
    if os.getenv("SWID"): c["SWID"]=os.getenv("SWID")
    return c

def fetch(year):
    if year>=2018:
        url=f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{LEAGUE_ID}"
        r=requests.get(url,params=[("view",v) for v in VIEWS],cookies=cookies(),timeout=45)
    else:
        url=f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{LEAGUE_ID}"
        r=requests.get(url,params=[("seasonId",year)]+[("view",v) for v in VIEWS],cookies=cookies(),timeout=45)
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
    manifest={"leagueId":LEAGUE_ID,"currentSeason":CURRENT,"seasons":[],"notes":[]}
    identities=[]
    # Probe all modern seasons, plus legacy endpoint for pre-2018.
    misses=0
    for year in range(CURRENT,2009,-1):
        try:
            d=fetch(year)
            if not d.get("teams"): raise ValueError("no teams")
            p=OUT/str(year); p.mkdir(parents=True,exist_ok=True)
            (p/"league.json").write_text(json.dumps(d,indent=2),encoding="utf-8")
            manifest["seasons"].append({"season":year,"teams":len(d.get("teams",[])),"matchups":len(d.get("schedule",[]))})
            identities.extend(owner_map(d,year)); misses=0
        except Exception as e:
            manifest["notes"].append(f"{year}: {type(e).__name__}: {e}")
            misses+=1
            # don't stop early: older league IDs/endpoints can have gaps
    manifest["seasons"].sort(key=lambda x:x["season"])
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    (OUT/"owner_identity_raw.json").write_text(json.dumps(identities,indent=2),encoding="utf-8")
    print(json.dumps(manifest,indent=2))
if __name__=="__main__": main()
