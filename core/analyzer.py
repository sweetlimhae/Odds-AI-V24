
import math
from collectors.normalizer import safe_float

def drop_rate(open_odds, current_odds):
    open_odds = safe_float(open_odds)
    current_odds = safe_float(current_odds)
    if open_odds <= 0 or current_odds <= 0:
        return 0
    return round(((open_odds - current_odds) / open_odds) * 100, 2)

def implied_probability(odds):
    odds = safe_float(odds)
    if odds <= 0:
        return 0
    return round((1 / odds) * 100, 2)

def realistic_probability(score):
    score = safe_float(score)
    if score <= 0:
        return 0
    return min(0.72, max(0.45, score / 135))

def ev_percent(score, odds):
    odds = safe_float(odds)
    if odds <= 1 or score <= 0:
        return 0
    return round((realistic_probability(score) * odds - 1) * 100, 2)

def kelly_percent(score, odds):
    odds = safe_float(odds)
    if odds <= 1 or score <= 0:
        return 0
    p = realistic_probability(score)
    b = odds - 1
    k = ((b * p) - (1 - p)) / b
    return round(max(0, min(k * 100, 15)), 2)

def pinnacle_bonus(market):
    return 10 if market.get("is_pinnacle") or "pinnacle" in str(market.get("bookmaker", "")).lower() else 0

def value_gap_component(odds, market_avg):
    odds = safe_float(odds)
    market_avg = safe_float(market_avg)
    if odds <= 1 or market_avg <= 1:
        return 0
    gap = ((odds - market_avg) / market_avg) * 100
    if gap >= 5:
        return 18
    if gap >= 3:
        return 13
    if gap >= 1.5:
        return 8
    if gap >= 0.5:
        return 4
    if gap <= -3:
        return -10
    return 0

def sharp_component(open_odds, current_odds, pinnacle_odds, market_avg, market):
    d = drop_rate(open_odds, current_odds)
    score = 0
    if d >= 6:
        score += 25
    elif d >= 4:
        score += 18
    elif d >= 2:
        score += 10
    elif d >= 0.8:
        score += 5

    current = safe_float(current_odds)
    pin = safe_float(pinnacle_odds)
    avg = safe_float(market_avg)

    if pin and avg and pin < avg:
        score += 16
    elif pin and avg and pin <= avg * 1.01:
        score += 8

    if pin and current and abs(pin - current) / current < 0.015:
        score += 6

    score += pinnacle_bonus(market)
    return max(0, min(45, round(score, 1)))

def steam_component(open_odds, current_odds):
    d = drop_rate(open_odds, current_odds)
    if d >= 8:
        return 22
    if d >= 5:
        return 16
    if d >= 3:
        return 10
    if d >= 1:
        return 4
    return 0

def clv_component(current_odds, pinnacle_odds, market_avg):
    current = safe_float(current_odds)
    pin = safe_float(pinnacle_odds)
    avg = safe_float(market_avg)
    score = 0
    if pin and avg and pin < avg:
        score += 12
    if current and avg and current >= avg:
        score += 8
    if pin and current and current >= pin:
        score += 6
    return min(24, score)

def reverse_line_component(open_odds, current_odds, market_avg):
    d = drop_rate(open_odds, current_odds)
    avg = safe_float(market_avg)
    current = safe_float(current_odds)
    if d >= 2 and avg and current <= avg:
        return 8
    if d >= 1 and avg and current <= avg * 1.01:
        return 4
    return 0

def risk_level(score, ev, kelly, d, ai_edge):
    if score >= 86 and ev >= 2 and kelly > 0 and d >= 1 and ai_edge >= 2:
        return "low"
    if score >= 76 and ev >= -1 and ai_edge >= -1:
        return "medium"
    return "high"

def confidence_score(score, ev, kelly, risk, ai_edge):
    confidence = safe_float(score)
    if ai_edge >= 8:
        confidence += 6
    elif ai_edge >= 4:
        confidence += 3
    elif ai_edge < 0:
        confidence -= 8
    if ev >= 8:
        confidence += 5
    elif ev >= 3:
        confidence += 2
    elif ev < -3:
        confidence -= 8
    if kelly >= 5:
        confidence += 3
    elif kelly <= 0:
        confidence -= 4
    if risk == "low":
        confidence += 4
    elif risk == "high":
        confidence -= 10
    return int(max(0, min(99, round(confidence))))

def recommendation_decision(confidence, ev, kelly, ai_edge, risk):
    if risk == "high" or ev < -3 or ai_edge < -2:
        return "NO_BET"
    if confidence >= 88 and ev >= 3 and kelly > 0 and ai_edge >= 3:
        return "BET"
    if confidence >= 76 and ev >= 0 and ai_edge >= 0:
        return "WATCH"
    return "NO_BET"

def recommendation_grade(confidence, decision):
    if decision == "NO_BET":
        return "No Bet"
    if confidence >= 92:
        return "★★★★★ 강추천"
    if confidence >= 85:
        return "★★★★ 추천"
    if confidence >= 76:
        return "★★★ 관찰"
    return "No Bet"

def sharp_pattern_tag(game, market, d, sharp, steam, clv, ev, ai_edge):
    pick = str(market.get("pick", "")).lower()
    away = str(game.get("away", "")).lower()
    home = str(game.get("home", "")).lower()
    strong = d >= 2 and sharp >= 20 and (steam >= 8 or clv >= 10) and ev > 0 and ai_edge > 0
    if not strong:
        return None
    if away and away in pick:
        return "🔥 Away Sharp Pick"
    if home and home in pick:
        return "🔥 Home Sharp Pick"
    return "🔥 Sharp Pick"

def confidence_icon(confidence, decision):
    if decision == "BET" and confidence >= 90:
        return "🟢 강력추천"
    if decision in ("BET", "WATCH"):
        return "🟡 관찰"
    return "🔴 배팅금지"

def reasons_for_pick(market, d, ev, sharp, steam, clv, value_gap, risk, confidence, ai_edge, decision):
    reasons = []
    if decision == "NO_BET":
        if ev < 0:
            reasons.append("EV 부족")
        if ai_edge < 0:
            reasons.append("AI Edge 부족")
        if risk == "high":
            reasons.append("위험도 높음")
        if sharp < 12:
            reasons.append("Sharp 신호 약함")
        return reasons or ["추천 근거 부족"]

    if market.get("is_pinnacle"):
        reasons.append("Pinnacle 기준 배당")
    if d >= 3:
        reasons.append("초기 대비 배당 하락")
    elif d >= 1:
        reasons.append("배당 하락 감지")
    if sharp >= 25:
        reasons.append("Sharp Money")
    if steam >= 10:
        reasons.append("Steam Move")
    if clv >= 14:
        reasons.append("CLV 기대")
    if value_gap >= 8:
        reasons.append("시장 평균 대비 가치")
    if ev >= 5:
        reasons.append("EV 우수")
    elif ev > 0:
        reasons.append("EV 양호")
    if ai_edge >= 5:
        reasons.append("AI Edge 우수")
    if risk == "low":
        reasons.append("위험도 낮음")
    return reasons or ["관찰 필요"]

def analyze_market(game, market):
    odds = safe_float(market.get("odds"))
    open_odds = safe_float(market.get("open_odds"))
    pinnacle_odds = safe_float(market.get("pinnacle_odds"))
    market_avg = safe_float(market.get("market_avg"))

    d = drop_rate(open_odds, odds)
    base = 38
    sharp = sharp_component(open_odds, odds, pinnacle_odds, market_avg, market)
    steam = steam_component(open_odds, odds)
    clv = clv_component(odds, pinnacle_odds, market_avg)
    value_gap = value_gap_component(odds, market_avg)
    reverse = reverse_line_component(open_odds, odds, market_avg)

    score = int(max(0, min(99, round(base + sharp + steam + clv + value_gap + reverse))))
    ai_prob = round(realistic_probability(score) * 100, 2)
    market_prob = implied_probability(odds)
    ai_edge = round(ai_prob - market_prob, 2)
    ev = ev_percent(score, odds)
    kelly = kelly_percent(score, odds)
    risk = risk_level(score, ev, kelly, d, ai_edge)
    confidence = confidence_score(score, ev, kelly, risk, ai_edge)
    decision = recommendation_decision(confidence, ev, kelly, ai_edge, risk)
    pattern_tag = sharp_pattern_tag(game, market, d, sharp, steam, clv, ev, ai_edge)

    item = {
        "sport": game.get("sport"),
        "source": game.get("source"),
        "data_quality": game.get("data_quality"),
        "league": game.get("league"),
        "country": game.get("country", "-"),
        "game": f"{game.get('league')} {game.get('home')} vs {game.get('away')}",
        "home": game.get("home"),
        "away": game.get("away"),
        "starts_at": game.get("starts_at"),
        "start_in_minutes": game.get("start_in_minutes"),
        "kst_time": game.get("kst_time"),
        "type": market.get("type"),
        "pick": market.get("pick"),
        "bookmaker": market.get("bookmaker"),
        "is_pinnacle": market.get("is_pinnacle", False),
        "odds": odds,
        "open_odds": open_odds,
        "pinnacle_odds": pinnacle_odds,
        "market_avg": market_avg,
        "best_odds": market.get("best_odds"),
        "drop_rate": d,
        "market_probability": market_prob,
        "ai_probability": ai_prob,
        "ai_edge": ai_edge,
        "score": score,
        "confidence": confidence,
        "ev": ev,
        "kelly": kelly,
        "sharp_score": sharp,
        "steam_score": steam,
        "clv_score": clv,
        "rlm_score": reverse,
        "value_score": value_gap,
        "risk": risk,
        "decision": decision,
        "grade": recommendation_grade(confidence, decision),
        "pattern_tag": pattern_tag,
        "confidence_icon": confidence_icon(confidence, decision),
        "is_value_bet": ev >= 3 and ai_edge >= 2,
        "is_underdog_value": odds >= 2.05 and ev > 0 and ai_edge > 0,
        "bookmakers": market.get("bookmakers", []),
        "team_stats": game.get("team_stats"),
    }
    item["reasons"] = reasons_for_pick(market, d, ev, sharp, steam, clv, value_gap, risk, confidence, ai_edge, decision)
    if pattern_tag:
        item["reasons"].insert(0, pattern_tag)
    return item

def analyze_games(games):
    picks = []
    for game in games or []:
        for market in game.get("markets", []):
            if safe_float(market.get("odds")) > 1:
                picks.append(analyze_market(game, market))
    return sorted(picks, key=lambda p: (p["decision"] == "BET", p["confidence"], p["ev"], p["sharp_score"], p["value_score"]), reverse=True)
