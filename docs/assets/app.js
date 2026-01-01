async function loadData() {
  const res = await fetch("./data.json", { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load data.json");
  return await res.json();
}

function fmtPct(x) {
  const v = (x * 100);
  return `${v.toFixed(1)}%`;
}

function pill(text) {
  const s = document.createElement("span");
  s.className = "pill";
  s.textContent = text;
  return s;
}

function renderTable(rows) {
  const tbody = document.querySelector("#rows");
  tbody.innerHTML = "";

  for (const r of rows) {
    const tr = document.createElement("tr");

    const tdSym = document.createElement("td");
    tdSym.innerHTML = `
      <div class="rowtitle">
        <strong>${r.ticker}</strong>
        <span class="muted">${r.company}</span>
      </div>
      <div class="small muted">${r.sector}</div>
      <div class="small"><a href="./ticker.html?t=${encodeURIComponent(r.ticker)}">View details →</a></div>
    `;

    const tdScore = document.createElement("td");
    tdScore.innerHTML = `<div class="score">${r.score.toFixed(1)}</div>
      <div class="small muted">base ${r.base_score.toFixed(1)} · news ${r.news_score.toFixed(1)}</div>`;

    const tdPrice = document.createElement("td");
    tdPrice.innerHTML = `$${r.close.toFixed(2)}`;

    const tdHi = document.createElement("td");
    const wrap = document.createElement("div");
    wrap.appendChild(pill(`20d ${fmtPct(r.ret_20)}`));
    wrap.appendChild(pill(`60d ${fmtPct(r.ret_60)}`));
    wrap.appendChild(pill(`RSI ${r.rsi14.toFixed(1)}`));
    if (r.news_score !== 0) wrap.appendChild(pill(`News ${r.news_score.toFixed(1)}`));
    tdHi.appendChild(wrap);

    tr.appendChild(tdSym);
    tr.appendChild(tdScore);
    tr.appendChild(tdPrice);
    tr.appendChild(tdHi);

    tbody.appendChild(tr);
  }
}

function unique(arr) {
  return Array.from(new Set(arr)).sort();
}

function applyFilters(allRows) {
  const q = (document.querySelector("#q").value || "").toLowerCase();
  const sector = document.querySelector("#sector").value;
  const minScore = parseFloat(document.querySelector("#minScore").value || "0");
  const sort = document.querySelector("#sort").value;

  let rows = allRows.filter(r => {
    const matchesText =
      r.ticker.toLowerCase().includes(q) ||
      (r.company || "").toLowerCase().includes(q);
    const matchesSector = sector === "ALL" || r.sector === sector;
    const matchesScore = r.score >= minScore;
    return matchesText && matchesSector && matchesScore;
  });

  if (sort === "score_desc") rows.sort((a,b)=>b.score-a.score);
  if (sort === "score_asc") rows.sort((a,b)=>a.score-b.score);
  if (sort === "ret20_desc") rows.sort((a,b)=>b.ret_20-a.ret_20);
  if (sort === "ret60_desc") rows.sort((a,b)=>b.ret_60-a.ret_60);
  if (sort === "news_desc") rows.sort((a,b)=>b.news_score-a.news_score);

  renderTable(rows);
  document.querySelector("#count").textContent = `${rows.length} shown`;
}

async function main() {
  const data = await loadData();
  const allRows = data.rows || [];

  document.querySelector("#updated").textContent = data.updated_utc || "(unknown)";

  // Populate sectors
  const sectors = unique(allRows.map(r => r.sector).filter(Boolean));
  const sel = document.querySelector("#sector");
  for (const s of sectors) {
    const opt = document.createElement("option");
    opt.value = s;
    opt.textContent = s;
    sel.appendChild(opt);
  }

  // Wire controls
  for (const id of ["q","sector","minScore","sort"]) {
    document.querySelector(`#${id}`).addEventListener("input", () => applyFilters(allRows));
    document.querySelector(`#${id}`).addEventListener("change", () => applyFilters(allRows));
  }

  applyFilters(allRows);
}

main().catch(err => {
  console.error(err);
  document.querySelector("#error").textContent = err.message;
});
