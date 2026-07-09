
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default

def now_kst():
    return datetime.now(KST)

def start_in_minutes(starts_at):
    if not starts_at:
        return None
    try:
        start = datetime.fromisoformat(str(starts_at).replace("Z", "+00:00"))
        return int((start - datetime.now(timezone.utc)).total_seconds() // 60)
    except Exception:
        try:
            start = datetime.fromisoformat(str(starts_at))
            return int((start - now_kst()).total_seconds() // 60)
        except Exception:
            return None

def format_kst(starts_at):
    if not starts_at:
        return "-"
    try:
        dt = datetime.fromisoformat(str(starts_at).replace("Z", "+00:00"))
        return dt.astimezone(KST).strftime("%m/%d %H:%M")
    except Exception:
        return str(starts_at)

def valid_start_time(starts_at, min_minutes=10, max_minutes=720):
    mins = start_in_minutes(starts_at)
    return mins is not None and min_minutes <= mins <= max_minutes

def market_average(values):
    nums = [safe_float(v) for v in values if safe_float(v) > 1]
    if not nums:
        return 0
    return round(sum(nums) / len(nums), 3)

def classify_market_type(sport_name, market_key, outcome_count):
    key = str(market_key or "").lower()
    if sport_name == "baseball":
        if key == "h2h":
            return "Moneyline"
        if key == "spreads":
            return "Run Line"
        if key == "totals":
            return "Total"
    if sport_name == "football":
        if key == "h2h" and outcome_count >= 3:
            return "1X2"
        if key == "spreads":
            return "Handicap"
        if key == "totals":
            return "Total"
    if key == "h2h":
        return "Moneyline"
    return key or "-"


def implied_open_proxy(current, market_avg):
    current = safe_float(current)
    market_avg = safe_float(market_avg)
    if market_avg > 1:
        return round(market_avg * 1.025, 2)
    if current > 1:
        return round(current * 1.025, 2)
    return 0

def normalize_game(sport, source, league, league_key, country, home, away, starts_at, markets, **extra):
    return {
        "sport": sport,
        "source": source,
        "league": league,
        "league_key": league_key,
        "country": country,
        "home": home,
        "away": away,
        "starts_at": starts_at,
        "kst_time": format_kst(starts_at),
        "start_in_minutes": start_in_minutes(starts_at),
        "markets": markets,
        **extra,
    }
