import json, os, time
from pathlib import Path
import requests

LEAGUE_ID=os.getenv("ESPN_LEAGUE_ID","1724229206")
CURRENT=int(os.getenv("ESPN_SEASON","2026"))
BASE="https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl"
VIEWS=["mTeam","mRoster","mMatchup","mMatchupScore","mSettings","mBoxscore","mStatus","mTransactions2"]

def get(url, params):
    r=requests.get(url,params=params,timeout=45,headers={"User-Agent":"Bago-Block-Gazette/1.0"})
    r.raise_for_status()
    return r.json()

def league(season):
    url=f"{BASE}/seasons/{season}/segments/0/leagues/{LEAGUE_ID}"
    return get(url,[("view",v) for v in VIEWS])

def discover():
    # Start with current league metadata; ESPN commonly exposes previousSeasons here.
    cur=league(CURRENT)
    seasons={CURRENT}
    prev=(cur.get("status") or {}).get("previousSeasons") or []
    for x in prev:
        try: seasons.add(int(x))
        except: pass
    # Probe backwards too, stopping after several consecutive misses.
    misses=0
    for y in range(CURRENT-1,2009,-1):
        if y in seasons: continue
        try:
            d=league(y)
            if d.get("teams"):
                seasons.add(y); misses=0
            else: misses+=1
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code in (400,401,403,404):
                misses+=1
            else: raise
        if misses>=4 and prev: break
        time.sleep(.15)
    return cur,sorted(seasons)

def main():
    root=Path("data/historical"); root.mkdir(parents=True,exist_ok=True)
    cur,seasons=discover()
    manifest={"leagueId":LEAGUE_ID,"currentSeason":CURRENT,"seasons":[],"notes":[]}
    for y in seasons:
        try:
            d=cur if y==CURRENT else league(y)
            if not d.get("teams"): continue
            p=root/str(y); p.mkdir(parents=True,exist_ok=True)
            (p/"league.json").write_text(json.dumps(d,indent=2),encoding="utf-8")
            manifest["seasons"].append({"season":y,"teams":len(d.get("teams",[])),"matchups":len(d.get("schedule",[]))})
            print("Archived",y,len(d.get("teams",[])),"teams")
        except Exception as e:
            manifest["notes"].append(f"{y}: {type(e).__name__}: {e}")
    (root/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print("Historical seasons archived:",[x["season"] for x in manifest["seasons"]])

if __name__=="__main__": main()
