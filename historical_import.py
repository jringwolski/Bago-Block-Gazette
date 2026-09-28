import json, os, requests
from pathlib import Path

LEAGUE_ID=os.getenv("ESPN_LEAGUE_ID","1724229206")
MID_LEAGUE_ID=os.getenv("MID_ESPN_LEAGUE_ID","704863106")
OLD_LEAGUE_ID=os.getenv("OLD_ESPN_LEAGUE_ID","746360760")
CURRENT=int(os.getenv("ESPN_SEASON","2026"))
# Authenticated historical archive refresh trigger
VIEWS=["mTeam","mRoster","mMatchup","mMatchupScore","mSettings","mBoxscore","mStatus","mTransactions2"]
OUT=Path("data/historical"); OUT.mkdir(parents=True,exist_ok=True)

def cookies():
    c={}
    if os.getenv("ESPN_S2"): c["espn_s2"]=os.getenv("ESPN_S2")
    if os.getenv("SWID"): c["SWID"]=os.getenv("SWID")
    return c

def fetch(year, league_id):
    if year>=2018:
        url=f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}"
        r=requests.get(url,params=[("view",v) for v in VIEWS],cookies=cookies(),timeout=45)
    else:
        url=f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{league_id}"
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
    manifest={"leagueIds":{"v3":LEAGUE_ID,"bago_block":MID_LEAGUE_ID,"lake_country_village":OLD_LEAGUE_ID},"currentSeason":CURRENT,"seasons":[],"notes":[]}
    identities=[]
    # Recovered ESPN lineage:
    # 2025-26 Bago Block v3 = 1724229206
    # 2023 Bago Block = 704863106
    # 2021 Lake Country Village = 746360760
    # Probe the likely ID first for each season, then fall back to the other recovered IDs.
    candidates = {
        2026: [LEAGUE_ID],
        2025: [LEAGUE_ID],
        2024: [MID_LEAGUE_ID, OLD_LEAGUE_ID],
        2023: [MID_LEAGUE_ID, OLD_LEAGUE_ID],
        2022: [OLD_LEAGUE_ID],
        2021: [OLD_LEAGUE_ID],
    }
    for year in range(CURRENT, 2020, -1):
        found=False
        for league_id in candidates.get(year, [LEAGUE_ID, MID_LEAGUE_ID, OLD_LEAGUE_ID]):
            try:
                d=fetch(year, league_id)
                if not d.get("teams"): raise ValueError("no teams")
                p=OUT/str(year); p.mkdir(parents=True,exist_ok=True)
                (p/"league.json").write_text(json.dumps(d,indent=2),encoding="utf-8")
                manifest["seasons"].append({"season":year,"leagueId":league_id,"teams":len(d.get("teams",[])),"matchups":len(d.get("schedule",[]))})
                identities.extend(owner_map(d,year))
                found=True
                break
            except Exception as e:
                manifest["notes"].append(f"{year} league {league_id}: {type(e).__name__}: {e}")
        if not found:
            manifest["notes"].append(f"{year}: no recovered league ID returned a usable season")
    manifest["seasons"].sort(key=lambda x:x["season"])
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    (OUT/"owner_identity_raw.json").write_text(json.dumps(identities,indent=2),encoding="utf-8")
    print(json.dumps(manifest,indent=2))
if __name__=="__main__": main()
