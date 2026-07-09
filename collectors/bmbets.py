
import os, re, json
from bs4 import BeautifulSoup
from .config import BMBETS_URLS
from .http_client import get
from .normalizer import safe_float, implied_open_proxy, normalize_game, now_kst

def _walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)

def _json_roots(html):
    roots = []
    soup = BeautifulSoup(html, "html.parser")

    for s in soup.find_all("script"):
        text = (s.string or s.get_text() or "").strip()
        if not text:
            continue

        if s.get("id") == "__NEXT_DATA__" or s.get("type") == "application/json":
            try:
                roots.append(json.loads(text))
            except Exception:
                pass

        # __NUXT__, window.__DATA__, hydration state 계열
        if any(k in text.lower() for k in ["match", "matches", "odds", "home", "away", "league"]):
            candidates = []
            for marker in ["window.__NUXT__=", "window.__INITIAL_STATE__=", "__NUXT__=", "__INITIAL_STATE__="]:
                if marker in text:
                    part = text.split(marker, 1)[1].strip().rstrip(";")
                    candidates.append(part)

            for c in candidates:
                try:
                    roots.append(json.loads(c))
                except Exception:
                    pass

    return roots

def _val(d, names):
    lower = {str(k).lower(): k for k in d.keys()}
    for name in names:
        k = lower.get(name.lower())
        if k is not None:
            v = d.get(k)
            if isinstance(v, dict):
                return v.get("name") or v.get("title") or v.get("label")
            return v
    return None

def _team_pair(d):
    home = _val(d, ["home", "home_team", "homeTeam", "home_name", "participant1", "team1", "homeName"])
    away = _val(d, ["away", "away_team", "awayTeam", "away_name", "participant2", "team2", "awayName"])
    league = _val(d, ["league", "competition", "tournament", "category", "event_group", "leagueName"])
    start = _val(d, ["start_time", "startTime", "commence_time", "date", "time", "starts_at", "kickoff", "startDate"])
    return home, away, league, start

def _markets_from_node(d, sport):
    markets = []
    for node in _walk(d):
        if not isinstance(node, dict):
            continue
        price = node.get("odds") or node.get("price") or node.get("decimal") or node.get("value") or node.get("odd")
        price = safe_float(price)
        if price <= 1:
            continue

        pick = node.get("pick") or node.get("name") or node.get("team") or node.get("label") or node.get("outcome") or node.get("selection")
        if isinstance(pick, dict):
            pick = pick.get("name") or pick.get("label")
        if not pick:
            continue

        book = node.get("bookmaker") or node.get("book") or node.get("site") or node.get("provider") or "BMBets"
        market_type = node.get("market") or node.get("type") or node.get("marketName") or ("1X2" if sport == "football" else "Moneyline")

        markets.append({
            "pick": str(pick),
            "type": str(market_type),
            "odds": price,
            "open_odds": implied_open_proxy(price, 0),
            "pinnacle_odds": price if "pinnacle" in str(book).lower() else None,
            "market_avg": price,
            "bookmaker": str(book),
            "is_pinnacle": "pinnacle" in str(book).lower(),
            "source": "bmbets_no_api",
        })
    return markets[:24]

def _html_card_fallback(html, sport):
    # JSON이 안 잡힐 때 텍스트 기반 최후 보조.
    # 정확도 낮아서 팀/배당이 같이 보이는 구조에서만 사용.
    games = []
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    joined = " ".join(lines)

    # 매우 단순한 "A vs B" 패턴
    for m in re.finditer(r'([A-Za-z가-힣0-9 ._\-]{2,40})\s+vs\s+([A-Za-z가-힣0-9 ._\-]{2,40})', joined, re.I):
        home, away = m.group(1).strip(), m.group(2).strip()
        if home.lower() == away.lower():
            continue
        markets = []
        # 주변 250자에서 배당 숫자 찾기
        chunk = joined[max(0, m.start()-120):m.end()+180]
        odds = [safe_float(x) for x in re.findall(r'\b[1-9]\.\d{2}\b', chunk)]
        odds = [x for x in odds if 1.01 <= x <= 20]
        if odds:
            markets.append({
                "pick": home,
                "type": "1X2" if sport == "football" else "Moneyline",
                "odds": odds[0],
                "open_odds": implied_open_proxy(odds[0], 0),
                "pinnacle_odds": None,
                "market_avg": odds[0],
                "bookmaker": "BMBets",
                "is_pinnacle": False,
                "source": "bmbets_text_fallback",
            })
        if len(odds) >= 2:
            markets.append({
                "pick": away,
                "type": "1X2" if sport == "football" else "Moneyline",
                "odds": odds[1],
                "open_odds": implied_open_proxy(odds[1], 0),
                "pinnacle_odds": None,
                "market_avg": odds[1],
                "bookmaker": "BMBets",
                "is_pinnacle": False,
                "source": "bmbets_text_fallback",
            })
        if markets:
            games.append(normalize_game(
                sport=sport, source="BMBets", league="BMBets", league_key="BMBets",
                country="-", home=home, away=away, starts_at=now_kst().isoformat(),
                markets=markets, data_quality="low_text_fallback"
            ))
    return games[:30]

def parse_bmbets_html(html, sport):
    games, seen = [], set()

    for root in _json_roots(html):
        for d in _walk(root):
            if not isinstance(d, dict) or len(d) < 3:
                continue
            home, away, league, start = _team_pair(d)
            if not home or not away:
                continue
            home, away = str(home), str(away)
            if home == away:
                continue
            league = str(league or "BMBets")
            key = (sport, league, home, away, str(start))
            if key in seen:
                continue
            seen.add(key)

            markets = _markets_from_node(d, sport)
            if not markets:
                continue

            games.append(normalize_game(
                sport=sport, source="BMBets", league=league, league_key=league,
                country="-", home=home, away=away, starts_at=start or now_kst().isoformat(),
                markets=markets, data_quality="medium"
            ))

    if not games:
        games = _html_card_fallback(html, sport)

    return games

def fetch_bmbets_games(sport="all"):
    if os.getenv("ENABLE_BMBETS", "1") != "1":
        return [], [{"source": "BMBets", "reason": "ENABLE_BMBETS=1 아님"}]

    targets = BMBETS_URLS.items() if sport in ("all", "", None) else [(sport, BMBETS_URLS.get(sport))]
    games, excluded = [], []

    for sport_name, url in targets:
        if not url:
            continue
        try:
            res = get(url, timeout=20)
            if res.status_code != 200:
                excluded.append({"source": "BMBets", "sport": sport_name, "reason": f"응답 {res.status_code}"})
                continue
            parsed = parse_bmbets_html(res.text, sport_name)
            if not parsed:
                excluded.append({
                    "source": "BMBets",
                    "sport": sport_name,
                    "reason": "파싱 실패: 사이트가 JS 렌더링이면 Render requests만으로 수집 불가"
                })
            games.extend(parsed)
        except Exception as e:
            excluded.append({"source": "BMBets", "sport": sport_name, "reason": f"요청 실패: {e}"})
    return games, excluded
