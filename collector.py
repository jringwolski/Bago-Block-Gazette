import json, os
from datetime import datetime, timezone
from pathlib import Path
import requests

LEAGUE_ID=os.getenv("ESPN_LEAGUE_ID","1724229206")
SEASON=int(os.getenv("ESPN_SEASON","2026"))
URL=f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{SEASON}/segments/0/leagues/{LEAGUE_ID}"
VIEWS=["mTeam","mRoster","mMatchup","mMatchupScore","mSettings","mBoxscore","mStatus"]

def current_scoring_period():
    r=requests.get(URL,params=[("view","mStatus")],timeout=30,headers={"User-Agent":"Bago-Block-Gazette/1.0"})
    r.raise_for_status()
    d=r.json()
    status=d.get("status") or {}
    return int(status.get("currentScoringPeriod") or status.get("currentMatchupPeriod") or 0)

def main():
    scoring_period=current_scoring_period()
    params=[("view",v) for v in VIEWS]
    if scoring_period:
        params.append(("scoringPeriodId",str(scoring_period)))
    r=requests.get(URL,params=params,timeout=30,headers={"User-Agent":"Bago-Block-Gazette/1.0"})
    r.raise_for_status()
    data=r.json()
    data["_gazette"]={"scoringPeriodId":scoring_period}
    out=Path("data")/str(SEASON); out.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    payload=json.dumps(data,indent=2)
    (out/"latest.json").write_text(payload,encoding="utf-8")
    (out/f"snapshot-{stamp}.json").write_text(payload,encoding="utf-8")
    print(f"Saved league {LEAGUE_ID}; teams={len(data.get('teams',[]))}; scoringPeriod={scoring_period}")

if __name__=="__main__":
    main()
