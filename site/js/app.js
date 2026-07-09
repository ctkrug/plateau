const SAMPLE_LOG = `date,exercise,weight,reps
2026-04-01,squat,225,5
2026-04-08,squat,230,5
2026-04-15,squat,232,5
2026-04-22,squat,230,5
2026-04-29,squat,231,5
2026-05-06,squat,230,5
2026-04-01,bench,155,5
2026-04-08,bench,160,5
2026-04-15,bench,165,5
2026-04-22,bench,170,5
2026-04-29,bench,175,5
2026-05-06,bench,180,5`;

const EXERCISE_COLORS = ["#5ee7ff", "#ffb347", "#6ee7b7", "#ff6b6b"];

const TREND_LABELS = {
  stalled: (c) => `Stalled ${c.weeks_stalled}wk`,
  trending_up: () => "Trending up",
  trending_down: () => "Trending down",
  insufficient_data: () => "Insufficient data",
};

const logInput = document.getElementById("log-input");
const analyzeBtn = document.getElementById("analyze-btn");
const statusLine = document.getElementById("status-line");
const tableWrap = document.getElementById("table-wrap");
const statusStrip = document.getElementById("status-strip");
const chart = document.getElementById("chart");

logInput.value = SAMPLE_LOG;

function setStatus(message, state) {
  statusLine.textContent = message;
  if (state) {
    statusLine.dataset.state = state;
  } else {
    delete statusLine.dataset.state;
  }
}

function renderTable(rows, errors) {
  if (rows.length === 0) {
    tableWrap.innerHTML = '<p class="empty-state">No valid rows parsed yet — paste a log above.</p>';
    return;
  }

  const body = rows
    .map(
      (row) => `
        <tr>
          <td>${row.date}</td>
          <td>${row.exercise}</td>
          <td>${row.weight}</td>
          <td>${row.reps}</td>
          <td>${row.estimated_1rm}</td>
        </tr>`
    )
    .join("");

  const errorList =
    errors.length > 0
      ? `<p class="status-line" data-state="error">${errors.length} row(s) skipped: ${errors.join("; ")}</p>`
      : "";

  tableWrap.innerHTML = `
    <table>
      <thead>
        <tr><th>Date</th><th>Exercise</th><th>Weight</th><th>Reps</th><th>Est. 1RM</th></tr>
      </thead>
      <tbody>${body}</tbody>
    </table>
    ${errorList}
  `;
}

function renderBadges(classifications) {
  if (classifications.length === 0) {
    statusStrip.innerHTML = '<p class="empty-state">No classifications yet — paste a log above.</p>';
    return;
  }

  statusStrip.innerHTML = classifications
    .map((c) => {
      const cssClass = c.trend.replace(/_/g, "-");
      const label = TREND_LABELS[c.trend](c);
      return `
        <button class="badge-btn" type="button" data-exercise="${c.exercise}" aria-pressed="false">
          <span class="exercise-name">${c.exercise}</span>
          <span class="badge ${cssClass}">${label}</span>
        </button>`;
    })
    .join("");
}

function drawChart(rows) {
  const dpr = window.devicePixelRatio || 1;
  const rect = chart.getBoundingClientRect();
  chart.width = rect.width * dpr;
  chart.height = rect.height * dpr;
  const ctx = chart.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, rect.width, rect.height);

  if (rows.length === 0) return;

  const padding = 32;
  const dates = rows.map((r) => new Date(r.date).getTime());
  const values = rows.map((r) => r.estimated_1rm);
  const minX = Math.min(...dates);
  const maxX = Math.max(...dates);
  const minY = Math.min(...values) * 0.95;
  const maxY = Math.max(...values) * 1.05;

  const xScale = (t) =>
    padding + (maxX === minX ? 0 : ((t - minX) / (maxX - minX)) * (rect.width - padding * 2));
  const yScale = (v) =>
    rect.height - padding - ((v - minY) / (maxY - minY || 1)) * (rect.height - padding * 2);

  const exercises = [...new Set(rows.map((r) => r.exercise))];

  exercises.forEach((exercise, i) => {
    const color = EXERCISE_COLORS[i % EXERCISE_COLORS.length];
    const points = rows
      .filter((r) => r.exercise === exercise)
      .sort((a, b) => new Date(a.date) - new Date(b.date));

    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    points.forEach((p, idx) => {
      const x = xScale(new Date(p.date).getTime());
      const y = yScale(p.estimated_1rm);
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    ctx.fillStyle = color;
    points.forEach((p) => {
      const x = xScale(new Date(p.date).getTime());
      const y = yScale(p.estimated_1rm);
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fill();
    });

    ctx.font = "12px monospace";
    ctx.fillText(exercise, padding, padding - 12 + i * 14);
  });
}

async function runAnalysis(pyodide) {
  const text = logInput.value;
  pyodide.globals.set("log_text", text);

  const result = pyodide.runPython(`
from plateau.parsing import parse_log
from plateau.analysis import classify_log, estimate_one_rep_max

_result = parse_log(log_text)
_classifications = classify_log(_result.entries)
{
    "rows": [
        {
            "date": str(e.date),
            "exercise": e.exercise,
            "weight": e.weight,
            "reps": e.reps,
            "estimated_1rm": round(estimate_one_rep_max(e.weight, e.reps), 1),
        }
        for e in _result.entries
    ],
    "errors": _result.errors,
    "classifications": [
        {
            "exercise": c.exercise,
            "trend": c.trend.value,
            "weeks_stalled": c.weeks_stalled,
            "slope": c.slope,
            "slope_ci_low": c.slope_ci_low,
            "slope_ci_high": c.slope_ci_high,
            "sessions_used": c.sessions_used,
            "points": [
                {"date": str(e.date), "estimated_1rm": round(estimate_one_rep_max(e.weight, e.reps), 1)}
                for e in sorted(
                    (e for e in _result.entries if e.exercise == c.exercise), key=lambda e: e.date
                )
            ],
        }
        for c in _classifications
    ],
}
`);

  const data = result.toJs({ dict_converter: Object.fromEntries });
  result.destroy();

  renderTable(data.rows, data.errors);
  renderBadges(data.classifications);
  drawChart(data.rows);

  setStatus(`Parsed ${data.rows.length} session(s), ${data.errors.length} error(s).`, "ready");
}

async function boot() {
  setStatus("Booting Python runtime (Pyodide)…");
  try {
    const pyodide = await loadPlateauPackage();
    setStatus("Ready.", "ready");
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze";

    analyzeBtn.addEventListener("click", () => {
      analyzeBtn.disabled = true;
      setStatus("Analyzing…");
      runAnalysis(pyodide)
        .catch((err) => setStatus(`Error: ${err.message}`, "error"))
        .finally(() => {
          analyzeBtn.disabled = false;
        });
    });

    // Run once immediately so the page isn't empty on load.
    analyzeBtn.click();
  } catch (err) {
    setStatus(`Failed to load Python runtime: ${err.message}`, "error");
  }
}

boot();
