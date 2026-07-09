
from datetime import timedelta
from .normalizer import now_kst

def demo_games(sport="all"):
    now = now_kst()
    games = [
        {
            "sport": "baseball", "source": "Demo", "league": "MLB", "league_key": "baseball_mlb", "country": "USA",
            "home": "LA Dodgers", "away": "Milwaukee Brewers",
            "starts_at": (now + timedelta(minutes=220)).isoformat(),
            "markets": [
                {"pick": "LA Dodgers", "type": "Moneyline", "odds": 1.82, "open_odds": 1.94, "pinnacle_odds": 1.80, "market_avg": 1.86, "bookmaker": "Pinnacle", "is_pinnacle": True, "source": "demo"},
                {"pick": "Milwaukee Brewers", "type": "Moneyline", "odds": 2.05, "open_odds": 1.96, "pinnacle_odds": 2.02, "market_avg": 2.00, "bookmaker": "Pinnacle", "is_pinnacle": True, "source": "demo"},
            ],
            "data_quality": "demo",
        },
        {
            "sport": "baseball", "source": "Demo", "league": "KBO", "league_key": "baseball_kbo", "country": "KR",
            "home": "LG Twins", "away": "KIA Tigers",
            "starts_at": (now + timedelta(minutes=260)).isoformat(),
            "markets": [
                {"pick": "KIA Tigers", "type": "Moneyline", "odds": 2.12, "open_odds": 2.25, "pinnacle_odds": 2.08, "market_avg": 2.17, "bookmaker": "Pinnacle", "is_pinnacle": True, "source": "demo"},
                {"pick": "LG Twins", "type": "Moneyline", "odds": 1.76, "open_odds": 1.68, "pinnacle_odds": 1.74, "market_avg": 1.72, "bookmaker": "Pinnacle", "is_pinnacle": True, "source": "demo"},
            ],
            "data_quality": "demo",
        },
        {
            "sport": "football", "source": "Demo", "league": "친선경기", "league_key": "soccer_international_friendlies", "country": "INT",
            "home": "Japan", "away": "South Korea",
            "starts_at": (now + timedelta(minutes=300)).isoformat(),
            "markets": [
                {"pick": "South Korea", "type": "1X2", "odds": 2.45, "open_odds": 2.70, "pinnacle_odds": 2.38, "market_avg": 2.55, "bookmaker": "Pinnacle", "is_pinnacle": True, "source": "demo"},
                {"pick": "Draw", "type": "1X2", "odds": 3.20, "open_odds": 3.10, "pinnacle_odds": 3.15, "market_avg": 3.18, "bookmaker": "Pinnacle", "is_pinnacle": True, "source": "demo"},
            ],
            "data_quality": "demo",
        },
        {
            "sport": "football", "source": "Demo", "league": "EPL", "league_key": "soccer_epl", "country": "UK",
            "home": "Arsenal", "away": "Chelsea",
            "starts_at": (now + timedelta(minutes=340)).isoformat(),
            "markets": [
                {"pick": "Arsenal", "type": "1X2", "odds": 1.78, "open_odds": 1.91, "pinnacle_odds": 1.74, "market_avg": 1.84, "bookmaker": "Pinnacle", "is_pinnacle": True, "source": "demo"},
                {"pick": "Chelsea", "type": "1X2", "odds": 4.25, "open_odds": 4.50, "pinnacle_odds": 4.10, "market_avg": 4.32, "bookmaker": "Pinnacle", "is_pinnacle": True, "source": "demo"},
            ],
            "data_quality": "demo",
        },
        {
            "sport": "baseball", "source": "BadFeed", "league": "BROKEN Korea NPB", "league_key": "broken",
            "country": "KR", "home": "Sidama Bunna", "away": "Welwalo Adigrat",
            "starts_at": (now + timedelta(minutes=240)).isoformat(),
            "markets": [
                {"pick": "X", "type": "1X2", "odds": 3.10, "open_odds": 3.10, "pinnacle_odds": 3.10, "market_avg": 3.25, "bookmaker": "BadFeed", "source": "demo"},
            ],
            "data_quality": "bad",
        },
    ]

    if sport != "all":
        games = [g for g in games if g["sport"] == sport]
    return games
