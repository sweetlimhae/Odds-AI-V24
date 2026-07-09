
import os
from .odds_api import fetch_odds_api_games
from .api_sports import fetch_api_sports_football
from .bmbets import fetch_bmbets_games
from .flashscore import enrich_team_stats
from .demo import demo_games
from .config import FOOTBALL_BLOCK_WORDS, ALLOWED_BASEBALL
from .normalizer import start_in_minutes, format_kst, valid_start_time

def exclusion_reason(game, market=None, requested_sport="all"):
    sport = str(game.get("sport", "")).lower()
    league = str(game.get("league", ""))
    league_key = str(game.get("league_key", ""))
    home = str(game.get("home", ""))
    away = str(game.get("away", ""))
    text = f"{sport} {league} {league_key} {home} {away}".lower()

    if requested_sport and requested_sport not in ("all", sport):
        return f"선택 종목({requested_sport})과 실제 종목({sport}) 불일치"

    if sport == "baseball":
        if league not in ALLOWED_BASEBALL and league_key not in ALLOWED_BASEBALL:
            return "야구는 MLB/KBO/NPB만 허용"
        if market:
            mtype = str(market.get("type", "")).lower()
            pick = str(market.get("pick", "")).lower()
            if mtype in ("1x2", "draw") or pick in ("x", "draw", "무승부"):
                return "야구에는 1X2/X/Draw 마켓 없음"
        football_words = ["sidama", "welwalo", "adigrat", "soccer", "football", "premier", "liga"]
        if any(w in text for w in football_words):
            return "야구가 아닌 팀명/리그명 감지"

    if sport == "football":
        if any(w in text for w in FOOTBALL_BLOCK_WORDS):
            return "축구 제외 기준: 3부 이하/유소년/리저브"

    return None

def clean_games(games, sport="all"):
    clean = []
    excluded = []
    min_minutes = int(os.getenv("MIN_START_MINUTES", "10"))
    max_minutes = int(os.getenv("MAX_START_MINUTES", "720"))

    for game in games:
        if not valid_start_time(game.get("starts_at"), min_minutes, max_minutes):
            continue

        r = exclusion_reason(game, requested_sport=sport)
        if r:
            excluded.append({
                "source": game.get("source"),
                "sport": game.get("sport"),
                "league": game.get("league"),
                "game": f"{game.get('home')} vs {game.get('away')}",
                "reason": r,
            })
            continue

        markets = []
        for market in game.get("markets", []):
            mr = exclusion_reason(game, market, sport)
            if mr:
                excluded.append({
                    "source": game.get("source"),
                    "sport": game.get("sport"),
                    "league": game.get("league"),
                    "game": f"{game.get('home')} vs {game.get('away')}",
                    "type": market.get("type"),
                    "pick": market.get("pick"),
                    "reason": mr,
                })
                continue
            markets.append(market)

        if not markets:
            excluded.append({
                "source": game.get("source"),
                "sport": game.get("sport"),
                "league": game.get("league"),
                "game": f"{game.get('home')} vs {game.get('away')}",
                "reason": "분석 가능한 정상 마켓 없음",
            })
            continue

        game = dict(game)
        game["markets"] = markets
        game["start_in_minutes"] = start_in_minutes(game.get("starts_at"))
        game["kst_time"] = format_kst(game.get("starts_at"))
        clean.append(game)

    return clean, excluded


def merge_fixture_only(games):
    priced = [g for g in games if g.get("markets")]
    fixtures = [g for g in games if not g.get("markets")]
    for p in priced:
        for f in fixtures:
            if p.get("sport") != f.get("sport"):
                continue
            ph, pa = str(p.get("home","")).lower(), str(p.get("away","")).lower()
            fh, fa = str(f.get("home","")).lower(), str(f.get("away","")).lower()
            if ph and pa and (ph in fh or fh in ph) and (pa in fa or fa in pa):
                p.setdefault("team_stats", f.get("team_stats"))
                p.setdefault("api_sports_fixture_id", f.get("api_sports_fixture_id"))
                break
    return priced


def collect_games(sport="all"):
    all_games = []
    all_excluded = []
    sources = []

    # API 키 없이 사용: BMBets만 실시간 수집 시도
    bmbets_games, bmbets_ex = fetch_bmbets_games(sport)
    all_games.extend(bmbets_games)
    all_excluded.extend(bmbets_ex)
    sources.append({
        "name": "BMBets",
        "count": len(bmbets_games),
        "status": "enabled_no_api" if bmbets_games else "empty_or_parse_failed"
    })

    mode = "live_no_api"
    notice = "API 없이 BMBets 수집기만 사용 중"

    if not all_games or os.getenv("FORCE_DEMO", "0") == "1":
        all_games = demo_games(sport)
        mode = "demo"
        notice = "BMBets 수집 실패 또는 경기 없음. 데모 데이터 사용 중"
        sources.append({"name": "Demo", "count": len(all_games), "status": "fallback"})

    clean, clean_excluded = clean_games(all_games, sport)
    all_excluded.extend(clean_excluded)

    if not clean and os.getenv("ALLOW_DEMO_FALLBACK", "1") == "1":
        demo = demo_games(sport)
        clean, clean_excluded = clean_games(demo, sport)
        all_excluded.extend(clean_excluded)
        mode = "demo"
        notice = "BMBets는 수집됐지만 분석 가능한 배당이 없어 데모 데이터 사용 중"
        sources.append({"name": "Demo", "count": len(clean), "status": "fallback_after_no_priced_games"})

    meta = {"mode": mode, "notice": notice, "sources": sources}
    return clean, all_excluded, meta
