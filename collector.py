import json, os
from datetime import datetime, timezone
from pathlib import Path
import requests

LEAGUE_ID=os.getenv("ESPN_LEAGUE_ID","1724229206")
SEASON=int(os.getenv("ESPN_SEASON","2026"))
URL=f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{SEASON}/segments/0/leagues/{LEAGUE_ID}"
VIEWS=["mTeam","mRoster","mMatchupScore","mSettings","mBoxscore"]

def main():
    r=requests.get(URL,params=[("view",v) for v in VIEWS],timeout=30,headers={"User-Agent":"Bago-Block-Gazette/1.0"})
    r.raise_for_status()
    data=r.json()
    out=Path("data")/str(SEASON); out.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    payload=json.dumps(data,indent=2)
    (out/"latest.json").write_text(payload,encoding="utf-8")
    (out/f"snapshot-{stamp}.json").write_text(payload,encoding="utf-8")
    print(f"Saved league {LEAGUE_ID}; teams={len(data.get('teams',[]))}")

if __name__=="__main__": main()
