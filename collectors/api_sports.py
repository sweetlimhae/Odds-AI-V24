
import os
from datetime import datetime, timedelta, timezone
from .http_client import get
from .config import API_SPORTS_FOOTBALL_LEAGUES
from .normalizer import normalize_game

def _headers():
    key = os.getenv("API_SPORTS_KEY") or os.getenv("APIFOOTBALL_KEY")
    if not key:
        return None
    return {"x-apisports-key": key}

def fetch_api_sports_football(sport="all"):
    if sport not in ("all", "football"):
        return [], []
    headers = _headers()
    if not headers:
        return [], [{"source": "API-SPORTS Football", "reason": "API_SPORTS_KEY 없음"}]

    base = os.getenv("API_SPORTS_FOOTBALL_HOST", "https://v3.football.api-sports.io")
    days = int(os.getenv("API_SPORTS_LOOKAHEAD_DAYS", "3"))
    season = int(os.getenv("FOOTBALL_SEASON", str(datetime.now().year)))
    games, excluded = [], []

    for league_label, league_id in API_SPORTS_FOOTBALL_LEAGUES.items():
        for delta in range(days + 1):
            date = (datetime.now(timezone.utc) + timedelta(days=delta)).strftime("%Y-%m-%d")
            try:
                res = get(f"{base}/fixtures", params={"league": league_id, "season": season, "date": date}, headers=headers, timeout=15)
                if res.status_code != 200:
                    excluded.append({"source": "API-SPORTS Football", "league": league_label, "reason": f"응답 {res.status_code}"})
                    continue
                payload = res.json()
            except Exception as e:
                excluded.append({"source": "API-SPORTS Football", "league": league_label, "reason": f"요청 실패: {e}"})
                continue

            for item in payload.get("response") or []:
                fixture = item.get("fixture", {})
                teams = item.get("teams", {})
                league = item.get("league", {})
                home = (teams.get("home") or {}).get("name")
                away = (teams.get("away") or {}).get("name")
                start = fixture.get("date")
                if not home or not away or not start:
                    continue
                games.append(normalize_game(
                    sport="football",
                    source="API-SPORTS Football",
                    league=league.get("name") or league_label,
                    league_key=str(league.get("id") or league_id),
                    country=league.get("country") or "-",
                    home=home,
                    away=away,
                    starts_at=start,
                    markets=[],
                    api_sports_fixture_id=fixture.get("id"),
                    data_quality="fixture_only",
                    team_stats={"note": "경기정보 수집 완료. 배당은 Odds source와 병합 필요"}
                ))
    return games, excluded
