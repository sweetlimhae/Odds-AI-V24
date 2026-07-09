
import os
import requests
from .config import THE_ODDS_API_KEYS
from .normalizer import safe_float, market_average, classify_market_type, valid_start_time, start_in_minutes, format_kst

def supported_keys(sport):
    if sport in ("all", "", None):
        out = []
        for items in THE_ODDS_API_KEYS.values():
            out.extend(items)
        return out
    return THE_ODDS_API_KEYS.get(sport, [])

def fetch_odds_api_games(sport="all", min_minutes=10, max_minutes=720):
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        return [], [{"source": "The Odds API", "reason": "ODDS_API_KEY 없음"}]

    games = []
    excluded = []

    for sport_name, sport_key, country, league_label in supported_keys(sport):
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
        params = {
            "apiKey": api_key,
            "regions": "us,eu,uk",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "decimal",
        }
        try:
            res = requests.get(url, params=params, timeout=12)
        except Exception as e:
            excluded.append({"source": "The Odds API", "league": league_label, "reason": f"요청 실패: {e}"})
            continue

        if res.status_code != 200:
            excluded.append({"source": "The Odds API", "league": league_label, "reason": f"API 응답 {res.status_code}"})
            continue

        data = res.json() or []
        if not data:
            excluded.append({"source": "The Odds API", "league": league_label, "reason": "경기 없음 또는 미지원 리그"})
            continue

        for item in data:
            starts_at = item.get("commence_time")
            if not valid_start_time(starts_at, min_minutes, max_minutes):
                continue

            raw_markets = []
            for bookmaker in item.get("bookmakers", []):
                book_title = bookmaker.get("title", "Unknown")
                is_pinnacle = "pinnacle" in book_title.lower()
                for market in bookmaker.get("markets", []):
                    outcomes = market.get("outcomes", []) or []
                    mtype = classify_market_type(sport_name, market.get("key"), len(outcomes))
                    for outcome in outcomes:
                        pick = outcome.get("name")
                        price = safe_float(outcome.get("price"))
                        if not pick or price <= 1:
                            continue
                        if sport_name == "baseball" and str(pick).lower() in ("draw", "x"):
                            continue
                        raw_markets.append({
                            "pick": pick,
                            "type": mtype,
                            "odds": price,
                            "bookmaker": book_title,
                            "is_pinnacle": is_pinnacle,
                            "market_key": market.get("key"),
                        })

            grouped = {}
            for row in raw_markets:
                key = (row["type"], row["pick"].lower().strip())
                if key not in grouped:
                    grouped[key] = {
                        "pick": row["pick"], "type": row["type"],
                        "all_odds": [], "pinnacle_odds": None,
                        "best_odds": row["odds"], "best_bookmaker": row["bookmaker"],
                        "bookmakers": [],
                    }
                g = grouped[key]
                g["all_odds"].append(row["odds"])
                g["bookmakers"].append({"bookmaker": row["bookmaker"], "odds": row["odds"]})
                if row["odds"] > g["best_odds"]:
                    g["best_odds"] = row["odds"]
                    g["best_bookmaker"] = row["bookmaker"]
                if row["is_pinnacle"]:
                    g["pinnacle_odds"] = row["odds"]

            markets = []
            for row in grouped.values():
                avg = market_average(row["all_odds"])
                current = safe_float(row["pinnacle_odds"]) or safe_float(row["best_odds"])
                open_proxy = round(avg * 1.025, 2) if avg else round(current * 1.025, 2)
                markets.append({
                    "pick": row["pick"],
                    "type": row["type"],
                    "odds": current,
                    "open_odds": open_proxy,
                    "pinnacle_odds": row["pinnacle_odds"],
                    "market_avg": avg,
                    "best_odds": row["best_odds"],
                    "bookmaker": "Pinnacle" if row["pinnacle_odds"] else row["best_bookmaker"],
                    "is_pinnacle": bool(row["pinnacle_odds"]),
                    "bookmakers": row["bookmakers"][:12],
                    "source": "the_odds_api",
                    "confidence_note": "초기배당은 API 한계상 시장평균 기반 추정값",
                })

            if markets:
                games.append({
                    "sport": sport_name,
                    "source": "The Odds API",
                    "league": league_label,
                    "league_key": sport_key,
                    "country": country,
                    "home": item.get("home_team"),
                    "away": item.get("away_team"),
                    "starts_at": starts_at,
                    "start_in_minutes": start_in_minutes(starts_at),
                    "kst_time": format_kst(starts_at),
                    "markets": markets,
                    "data_quality": "medium",
                })

    return games, excluded
