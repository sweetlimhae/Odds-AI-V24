
import math
from collectors.normalizer import safe_float

def game_key(pick):
    return f"{pick.get('sport')}|{pick.get('league')}|{pick.get('home')}|{pick.get('away')}|{pick.get('starts_at')}"

def pick_sort_score(p):
    return (
        safe_float(p.get("confidence")),
        safe_float(p.get("ai_edge")),
        safe_float(p.get("ev")),
        safe_float(p.get("sharp_score")),
        safe_float(p.get("kelly")),
    )

def one_pick_per_game(picks):
    best = {}
    for p in picks:
        key = game_key(p)
        if key not in best or pick_sort_score(p) > pick_sort_score(best[key]):
            best[key] = p
    return sorted(best.values(), key=pick_sort_score, reverse=True)

def combo_stats(combo_type, picks):
    total_odds = math.prod([safe_float(p.get("odds"), 1) for p in picks])
    avg_confidence = sum(safe_float(p.get("confidence")) for p in picks) / len(picks)
    avg_score = sum(safe_float(p.get("score")) for p in picks) / len(picks)
    avg_ev = sum(safe_float(p.get("ev")) for p in picks) / len(picks)
    avg_kelly = sum(safe_float(p.get("kelly")) for p in picks) / len(picks)
    avg_edge = sum(safe_float(p.get("ai_edge")) for p in picks) / len(picks)

    if combo_type == "안정형":
        stake = "추천 비중 3~5%"
        risk = "낮음"
        reasons = ["AI 신뢰도 높음", "Sharp/EV/Kelly 조건 충족", "중복 경기 없음"]
    elif combo_type == "평균형":
        stake = "추천 비중 1~3%"
        risk = "보통"
        reasons = ["균형형 2폴더", "EV 양수 위주", "Sharp 또는 Steam 조건 충족"]
    else:
        stake = "소액 도전 0.5~1.5%"
        risk = "높음"
        reasons = ["Value Bet/역배 가치 중심", "AI Edge 우수 픽 포함", "고배당 도전형"]

    return {
        "type": combo_type,
        "folder_size": 2,
        "total_odds": round(total_odds, 2),
        "avg_score": round(avg_score, 1),
        "avg_confidence": round(avg_confidence, 1),
        "avg_ev": round(avg_ev, 2),
        "avg_kelly": round(avg_kelly, 2),
        "avg_edge": round(avg_edge, 2),
        "risk": risk,
        "stake_guide": stake,
        "reasons": reasons,
        "picks": picks,
    }

def select_two(candidates, used_games):
    selected = []
    for p in candidates:
        key = game_key(p)
        if key in used_games:
            continue
        selected.append(p)
        used_games.add(key)
        if len(selected) == 2:
            return selected
    for p in selected:
        used_games.discard(game_key(p))
    return None

def build_recommendations(raw_picks):
    usable = [p for p in raw_picks if p["decision"] != "NO_BET" and safe_float(p.get("ev")) >= 0]
    unique = one_pick_per_game(usable)

    top5 = unique[:5]
    used_games = set()
    combos = []

    stable_candidates = [
        p for p in unique
        if p["confidence"] >= 90
        and p["ev"] >= 3
        and p["kelly"] >= 2
        and p["sharp_score"] >= 20
        and p["risk"] == "low"
    ]

    average_candidates = [
        p for p in unique
        if 80 <= p["confidence"] < 90
        and p["ev"] >= 0
        and (p["sharp_score"] >= 15 or p["steam_score"] >= 8)
        and p["risk"] in ("low", "medium")
    ]

    challenge_candidates = [
        p for p in unique
        if p["ev"] >= 1
        and p["ai_edge"] >= 1
        and (
            "Away Sharp Pick" in str(p.get("pattern_tag", ""))
            or safe_float(p.get("odds")) >= 2.05
            or safe_float(p.get("value_score")) >= 8
        )
    ]

    selected = select_two(stable_candidates, used_games)
    if selected:
        combos.append(combo_stats("안정형", selected))

    selected = select_two(average_candidates, used_games)
    if selected:
        combos.append(combo_stats("평균형", selected))

    selected = select_two(challenge_candidates, used_games)
    if selected:
        combos.append(combo_stats("도전형", selected))

    return combos, top5, len(combos) == 0
