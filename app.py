
from flask import Flask, jsonify, render_template, request
from datetime import datetime, timedelta, timezone
import os

from collectors.pipeline import collect_games
from core.analyzer import analyze_games
from core.recommender import build_recommendations

app = Flask(__name__, template_folder="templates", static_folder="static")

KST = timezone(timedelta(hours=9))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "odds-ai-v22",
        "time_kst": datetime.now(KST).isoformat()
    })

@app.route("/api/live-games")
def live_games():
    sport = request.args.get("sport", "all")
    games, excluded, meta = collect_games(sport=sport)
    return jsonify({
        "mode": meta.get("mode"),
        "notice": meta.get("notice"),
        "sources": meta.get("sources"),
        "count": len(games),
        "excluded_count": len(excluded),
        "games": games,
        "excluded": excluded[:80],
    })

@app.route("/api/recommendations")
def recommendations():
    sport = request.args.get("sport", "all")
    games, excluded, meta = collect_games(sport=sport)
    picks = analyze_games(games)
    combos, top5, no_bet = build_recommendations(picks)

    summary = {
        "total_games": len(games),
        "total_picks": len(picks),
        "top_pick_count": len(top5),
        "recommendation_count": len(combos),
        "excluded_count": len(excluded),
        "no_bet": no_bet,
        "mode": meta.get("mode"),
        "sources": meta.get("sources"),
        "message": "추천 가능" if not no_bet else "조건에 맞는 2폴더 조합이 없습니다.",
    }

    return jsonify({
        "mode": meta.get("mode"),
        "notice": meta.get("notice"),
        "sources": meta.get("sources"),
        "summary": summary,
        "top_picks": top5,
        "combos": combos,
        "recommendations": combos,
        "excluded": excluded[:80],
    })

@app.route("/<path:path>")
def catch_all(path):
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
