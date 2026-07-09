
# Flashscore/Sofascore류 경기 데이터 보강 모듈 placeholder
# 목적:
# - 최근 5/10경기
# - 홈/원정 성적
# - H2H
# - 리그 순위
# - 득점/실점
#
# 공식 API가 아니므로 기본 비활성화.
# 나중에 RapidAPI, API-Football, 스포츠데이터 API 등을 붙이면 이 파일만 수정하면 됨.

def enrich_team_stats(games):
    for game in games:
        game.setdefault("team_stats", {
            "recent_5": None,
            "recent_10": None,
            "home_away": None,
            "h2h": None,
            "standings": None,
            "goals_for_against": None,
            "injuries": None,
            "note": "팀 성적 데이터 소스 미연결",
        })
    return games
