
const sportEl = document.getElementById("sport");
const resultsEl = document.getElementById("results");
const statusEl = document.getElementById("status");

document.getElementById("gamesBtn").addEventListener("click", loadGames);
document.getElementById("analyzeBtn").addEventListener("click", analyze);

function params() {
  return `sport=${encodeURIComponent(sportEl.value)}`;
}

function setStatus(text) {
  statusEl.innerHTML = text ? `<div class="notice">${text}</div>` : "";
}

function n(v, fallback = 0) {
  const x = Number(v);
  return Number.isFinite(x) ? x : fallback;
}

function riskLabel(risk) {
  if (risk === "low") return "낮음";
  if (risk === "medium") return "보통";
  if (risk === "high") return "높음";
  return risk || "-";
}

function decisionBadge(decision) {
  if (decision === "BET") return `<span class="badge bet">BET</span>`;
  if (decision === "WATCH") return `<span class="badge watch">WATCH</span>`;
  return `<span class="badge no">NO BET</span>`;
}

function rankIcon(i) {
  if (i === 0) return "💎";
  if (i === 1) return "🥇";
  if (i === 2) return "🥈";
  if (i === 3) return "🥉";
  return "⭐";
}

function comboIcon(type) {
  if (type === "안정형") return "🟢";
  if (type === "평균형") return "🟡";
  if (type === "도전형") return "🔴";
  return "📌";
}

function confidenceBar(score) {
  score = Math.max(0, Math.min(100, n(score)));
  return `
    <div class="meter"><div class="meter-fill" style="width:${score}%"></div></div>
    <small>AI 신뢰도 ${score}%</small>
  `;
}

function stakeGuide(p) {
  const k = n(p.kelly);
  if (p.risk === "high") return "No Bet 또는 관찰";
  if (k >= 10) return "실전 추천 비중 5~8%";
  if (k >= 5) return "실전 추천 비중 3~5%";
  if (k >= 1) return "실전 추천 비중 1~2%";
  return "소액 또는 관찰";
}

function renderSources(sources) {
  if (!sources || sources.length === 0) return "";
  return `
    <article class="card">
      <h2>데이터 소스 상태</h2>
      <div class="source-grid">
        ${sources.map(s => `
          <div>
            <small>${s.name}</small>
            <b>${s.count ?? 0}건</b>
            <p>${s.status || "-"}</p>
          </div>
        `).join("")}
      </div>
    </article>
  `;
}

function renderSummary(summary, sources) {
  if (!summary) return renderSources(sources);
  return `
    ${renderSources(sources)}
    <article class="card highlight">
      <h2>오늘 분석 요약</h2>
      <div class="summary-grid">
        <div><small>정상 경기</small><b>${summary.total_games ?? 0}</b></div>
        <div><small>분석픽</small><b>${summary.total_picks ?? 0}</b></div>
        <div><small>단일픽 TOP</small><b>${summary.top_pick_count ?? 0}</b></div>
        <div><small>2폴더 조합</small><b>${summary.recommendation_count ?? 0}</b></div>
        <div><small>제외</small><b>${summary.excluded_count ?? 0}</b></div>
        <div><small>모드</small><b>${summary.mode || "-"}</b></div>
      </div>
      <p class="reason">${summary.message || ""}</p>
    </article>
  `;
}

function renderGameHeader(game) {
  return `
    <div class="game-head">
      <div>
        <div class="tag">${(game.sport || "").toUpperCase()} · ${game.country || "-"} · ${game.league || "-"} · ${game.source || "-"}</div>
        <h2>${game.home || "-"} <span>vs</span> ${game.away || "-"}</h2>
      </div>
      <div class="timebox">
        <b>${game.kst_time || "-"}</b>
        <small>시작까지 ${game.start_in_minutes ?? "-"}분</small>
      </div>
    </div>
  `;
}

function renderGames(games, excluded, sources) {
  if ((!games || games.length === 0) && (!excluded || excluded.length === 0)) {
    resultsEl.innerHTML = renderSources(sources) + "<div class='card'>조건에 맞는 경기가 없습니다.</div>";
    return;
  }

  const gamesHtml = (games || []).map(game => `
    <article class="card">
      ${renderGameHeader(game)}
      <div class="market-table">
        <div class="row head">
          <span>마켓</span><span>픽</span><span>현재</span><span>초기</span><span>Pinnacle</span><span>시장평균</span><span>북메이커</span>
        </div>
        ${(game.markets || []).map(m => `
          <div class="row">
            <span>${m.type || "-"}</span>
            <span><b>${m.pick || "-"}</b></span>
            <span>${m.odds ?? "-"}</span>
            <span>${m.open_odds ?? "-"}</span>
            <span>${m.pinnacle_odds ?? "-"}</span>
            <span>${m.market_avg ?? "-"}</span>
            <span>${m.bookmaker || "-"}</span>
          </div>
        `).join("")}
      </div>
    </article>
  `).join("");

  resultsEl.innerHTML = renderSources(sources) + gamesHtml + renderExcluded(excluded);
}

async function loadGames() {
  try {
    setStatus("오늘 경기 불러오는 중...");
    resultsEl.innerHTML = "<div class='card'>불러오는 중...</div>";
    const res = await fetch(`/api/live-games?${params()}`);
    const data = await res.json();
    setStatus(`${data.notice || ""} / 정상 ${data.count || 0}경기 / 제외 ${data.excluded_count || 0}건`);
    renderGames(data.games, data.excluded, data.sources);
  } catch (err) {
    console.error(err);
    resultsEl.innerHTML = "<div class='card danger'>경기를 불러오지 못했습니다.</div>";
  }
}

function renderPick(p, i) {
  const confidence = p.confidence ?? p.score ?? 0;
  return `
    <div class="pick">
      <div class="rank">${rankIcon(i)} 추천순위 ${i + 1} ${decisionBadge(p.decision)} <span class="ai-icon">${p.confidence_icon || ""}</span></div>
      ${p.pattern_tag ? `<div class="sharp-tag">${p.pattern_tag}</div>` : ""}
      ${p.is_value_bet ? `<div class="sharp-tag">⭐ Value Bet</div>` : ""}
      ${p.is_underdog_value ? `<div class="sharp-tag">⭐ 역배 가치픽</div>` : ""}
      <div class="tag">${(p.sport || "").toUpperCase()} · ${p.country || "-"} · ${p.league || "-"} · ${p.type || ""} · ${p.source || "-"} · 위험도 ${riskLabel(p.risk)}</div>
      <h3>${p.home || "-"} <span>vs</span> ${p.away || "-"}</h3>
      <p class="time">KST ${p.kst_time || "-"} / 시작까지 ${p.start_in_minutes ?? "-"}분</p>
      ${confidenceBar(confidence)}
      <p><b>추천: ${p.pick || "-"}</b></p>
      <p>등급: <b>${p.grade || "-"}</b></p>
      <div class="summary-grid">
        <div><small>현재배당</small><b>${p.odds ?? "-"}</b></div>
        <div><small>초기배당</small><b>${p.open_odds ?? "-"}</b></div>
        <div><small>Pinnacle</small><b>${p.pinnacle_odds ?? "-"}</b></div>
        <div><small>시장평균</small><b>${p.market_avg ?? "-"}</b></div>
        <div><small>하락률</small><b>${p.drop_rate ?? "-"}%</b></div>
        <div><small>AI 예상승률</small><b>${p.ai_probability ?? "-"}%</b></div>
        <div><small>시장확률</small><b>${p.market_probability ?? "-"}%</b></div>
        <div><small>AI Edge</small><b>${p.ai_edge ?? "-"}%</b></div>
        <div><small>AI 점수</small><b>${p.score ?? "-"}</b></div>
        <div><small>Sharp</small><b>${p.sharp_score ?? "-"}점</b></div>
        <div><small>Steam</small><b>${p.steam_score ?? "-"}점</b></div>
        <div><small>CLV</small><b>${p.clv_score ?? "-"}점</b></div>
        <div><small>EV</small><b>${p.ev ?? "-"}%</b></div>
        <div><small>Kelly</small><b>${p.kelly ?? "-"}%</b></div>
      </div>
      <p class="reason">${(p.reasons || []).join(" · ")}</p>
      <p class="reason">배팅금액 가이드: ${stakeGuide(p)}</p>
    </div>
  `;
}

function renderCombos(combos) {
  if (!combos || combos.length === 0) {
    return `<article class="card danger"><h2>No Bet</h2><p>현재 조건에서는 추천 2폴더 조합이 없습니다.</p></article>`;
  }

  return combos.map((combo) => `
    <article class="card highlight">
      <h2>${comboIcon(combo.type)} 2폴더 ${combo.type || "추천 조합"}</h2>
      <div class="summary-grid">
        <div><small>폴더수</small><b>2폴더</b></div>
        <div><small>총배당</small><b>${combo.total_odds ?? "-"}</b></div>
        <div><small>평균점수</small><b>${combo.avg_score ?? "-"}</b></div>
        <div><small>평균신뢰도</small><b>${combo.avg_confidence ?? "-"}%</b></div>
        <div><small>평균EV</small><b>${combo.avg_ev ?? "-"}%</b></div>
        <div><small>평균Kelly</small><b>${combo.avg_kelly ?? "-"}%</b></div>
        <div><small>위험도</small><b>${combo.risk || "-"}</b></div>
        <div><small>배팅비중</small><b>${combo.stake_guide || "-"}</b></div>
      </div>
      <p class="reason">${(combo.reasons || []).join(" · ")}</p>
      ${(combo.picks || []).map((p, i) => renderPick(p, i)).join("")}
    </article>
  `).join("");
}

function renderTopPicks(topPicks) {
  if (!topPicks || topPicks.length === 0) return "";
  return `<article class="card"><h2>💎 오늘의 단일픽 TOP 5</h2>${topPicks.slice(0, 5).map((p, i) => renderPick(p, i)).join("")}</article>`;
}

function renderExcluded(excluded) {
  if (!excluded || excluded.length === 0) return "";
  return `
    <article class="card danger">
      <h2>제외/미수집 사유</h2>
      <div class="market-table">
        <div class="row head"><span>소스</span><span>종목</span><span>리그</span><span>경기/마켓</span><span>사유</span></div>
        ${excluded.slice(0, 80).map(g => `
          <div class="row">
            <span>${g.source || "-"}</span>
            <span>${g.sport || "-"}</span>
            <span>${g.league || "-"}</span>
            <span>${g.game || g.type || "-"} / ${g.pick || "-"}</span>
            <span>${g.reason || ""}</span>
          </div>
        `).join("")}
      </div>
    </article>
  `;
}

async function analyze() {
  try {
    setStatus("AI 분석 중...");
    resultsEl.innerHTML = "<div class='card'>AI 분석 중...</div>";
    const res = await fetch(`/api/recommendations?${params()}`);
    const data = await res.json();
    setStatus(`${data.notice || "AI 분석 완료"} / 제외 ${data.summary?.excluded_count || 0}건`);
    resultsEl.innerHTML =
      renderSummary(data.summary, data.sources) +
      renderTopPicks(data.top_picks) +
      renderCombos(data.combos || data.recommendations || []) +
      renderExcluded(data.excluded);
  } catch (err) {
    console.error(err);
    resultsEl.innerHTML = "<div class='card danger'>AI 분석 실패</div>";
  }
}
