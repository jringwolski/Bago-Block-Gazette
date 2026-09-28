import json
from pathlib import Path

def main():
    source = Path("data/historical/all_time.json")
    if not source.exists():
        raise FileNotFoundError("data/historical/all_time.json is required; run build_all_time.py first")

    all_time = json.loads(source.read_text(encoding="utf-8"))
    games = all_time.get("games", [])
    records = all_time.get("records", {})

    out = {
        "games": games,
        "records": records,
        "season_summaries": all_time.get("season_summaries", {}),
        "career": all_time.get("career", {}),
        "source": "data/historical/all_time.json",
    }

    Path("data/history.json").write_text(
        json.dumps(out, indent=2),
        encoding="utf-8",
    )
    print("Historical games:", len(games))

if __name__ == "__main__":
    main()
