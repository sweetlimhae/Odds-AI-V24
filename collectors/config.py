
# V22 데이터 수집 기준
# 축구: 3부 이하/유소년/리저브만 제외. 국가대표/친선/컵대회 포함.

SPORT_LABELS = {
    "baseball": "야구",
    "football": "축구",
    "basketball": "농구",
    "volleyball": "배구",
    "ice-hockey": "하키",
    "american-football": "미식축구",
}

ALLOWED_BASEBALL = {
    "MLB", "KBO", "NPB",
    "baseball_mlb", "baseball_kbo", "baseball_npb"
}

FOOTBALL_BLOCK_WORDS = [
    "u17", "u18", "u19", "u20", "u21", "u23",
    "youth", "reserve", "reserves", "academy",
    "liga3", "league_three", "third", "3rd",
    "serie_c", "national_league", "regional", "amateur"
]

# The Odds API 키. 지원 안 되는 리그는 자동 스킵됨.
THE_ODDS_API_KEYS = {
    "baseball": [
        ("baseball", "baseball_mlb", "USA", "MLB"),
        ("baseball", "baseball_kbo", "KR", "KBO"),
        ("baseball", "baseball_npb", "JP", "NPB"),
    ],
    "football": [
        # 1부/2부 주요 리그
        ("football", "soccer_epl", "UK", "EPL"),
        ("football", "soccer_efl_champ", "UK", "챔피언십"),
        ("football", "soccer_spain_la_liga", "ES", "라리가"),
        ("football", "soccer_spain_segunda_division", "ES", "세군다"),
        ("football", "soccer_italy_serie_a", "IT", "세리에A"),
        ("football", "soccer_italy_serie_b", "IT", "세리에B"),
        ("football", "soccer_germany_bundesliga", "DE", "분데스리가"),
        ("football", "soccer_germany_bundesliga2", "DE", "분데스리가2"),
        ("football", "soccer_france_ligue_one", "FR", "리그1"),
        ("football", "soccer_france_ligue_two", "FR", "리그2"),
        ("football", "soccer_japan_j_league", "JP", "J1"),
        ("football", "soccer_japan_j2_league", "JP", "J2"),
        ("football", "soccer_korea_kleague1", "KR", "K리그1"),
        ("football", "soccer_korea_kleague2", "KR", "K리그2"),
        ("football", "soccer_usa_mls", "USA", "MLS"),

        # 컵/국가대표/친선/국제대회
        ("football", "soccer_uefa_champs_league", "UEFA", "챔피언스리그"),
        ("football", "soccer_uefa_europa_league", "UEFA", "유로파리그"),
        ("football", "soccer_uefa_europa_conference_league", "UEFA", "컨퍼런스리그"),
        ("football", "soccer_afc_champions_league", "AFC", "AFC 챔피언스리그"),
        ("football", "soccer_fifa_world_cup", "FIFA", "월드컵"),
        ("football", "soccer_fifa_world_cup_qualifiers", "FIFA", "월드컵 예선"),
        ("football", "soccer_uefa_nations_league", "UEFA", "네이션스리그"),
        ("football", "soccer_international_friendlies", "INT", "친선경기"),
        ("football", "soccer_england_fa_cup", "UK", "FA컵"),
        ("football", "soccer_england_efl_cup", "UK", "리그컵"),
        ("football", "soccer_spain_copa_del_rey", "ES", "코파 델 레이"),
        ("football", "soccer_germany_dfb_pokal", "DE", "DFB 포칼"),
        ("football", "soccer_italy_coppa_italia", "IT", "코파 이탈리아"),
        ("football", "soccer_france_coupe_de_france", "FR", "프랑스컵"),
    ],
    "basketball": [
        ("basketball", "basketball_nba", "USA", "NBA"),
        ("basketball", "basketball_wnba", "USA", "WNBA"),
        ("basketball", "basketball_kbl", "KR", "KBL"),
    ],
    "ice-hockey": [
        ("ice-hockey", "icehockey_nhl", "USA/CAN", "NHL"),
    ],
    "american-football": [
        ("american-football", "americanfootball_nfl", "USA", "NFL"),
    ],
}


API_SPORTS_FOOTBALL_LEAGUES = {
    "K리그1": 292, "K리그2": 293,
    "J1": 98, "J2": 99,
    "EPL": 39, "챔피언십": 40,
    "라리가": 140, "세군다": 141,
    "세리에A": 135, "세리에B": 136,
    "분데스리가": 78, "분데스리가2": 79,
    "리그1": 61, "리그2": 62,
    "MLS": 253,
    "챔피언스리그": 2, "유로파리그": 3, "컨퍼런스리그": 848,
    "월드컵": 1, "월드컵 예선": 32, "네이션스리그": 5,
    "친선경기": 10,
}


BMBETS_URLS = {
    "football": "https://www.bmbets.com/matches/football/",
    "baseball": "https://www.bmbets.com/matches/baseball",
    "basketball": "https://www.bmbets.com/matches/basketball",
    "volleyball": "https://www.bmbets.com/matches/volleyball",
    "ice-hockey": "https://www.bmbets.com/matches/ice-hockey",
    "american-football": "https://www.bmbets.com/matches/american-football/",
}
