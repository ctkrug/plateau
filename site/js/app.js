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
2026-05-06,bench,180,5
2026-04-01,deadlift,315,5
2026-04-08,deadlift,305,5
2026-04-15,deadlift,300,5
2026-04-22,deadlift,290,5
2026-04-29,deadlift,285,5
2026-05-06,deadlift,275,5`;

const ACCENT = "#5ee7ff";
const TEXT = "#eaf2fb";
const TEXT_MUTED = "#8fa8c2";
const ACCENT_BAND = "rgba(94, 231, 255, 0.14)";

const STORAGE_KEY = "plateau:last-log";

function saveLastLog(text) {
  try {
    localStorage.setItem(STORAGE_KEY, text);
  } catch {
    // Storage unavailable (private browsing, disabled cookies) — analysis still works, just isn't persisted.
  }
}

function loadLastLog() {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

const TREND_LABELS = {
  stalled: (c) => `Stalled ${c.weeks_stalled}wk`,
  trending_up: () => "Trending up",
  trending_down: () => "Trending down",
  insufficient_data: () => "Insufficient data",
};

const logInput = document.getElementById("log-input");
const analyzeBtn = document.getElementById("analyze-btn");
const demoBtn = document.getElementById("demo-btn");
const statusLine = document.getElementById("status-line");
const tableWrap = document.getElementById("table-wrap");
const statusStrip = document.getElementById("status-strip");
const chart = document.getElementById("chart");

let lastClassifications = [];
let activeExercise = null;

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
    tableWrap.innerHTML =
      '<p class="empty-state">No valid rows parsed yet — paste a log above, or click "Try it now".</p>';
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
    statusStrip.innerHTML =
      '<p class="empty-state">No classifications yet — paste a log above, or click "Try it now".</p>';
    return;
  }

  statusStrip.innerHTML = classifications
    .map((c) => {
      const cssClass = c.trend.replace(/_/g, "-");
      const label = TREND_LABELS[c.trend](c);
      const pressed = c.exercise === activeExercise;
      return `
        <button class="badge-btn" type="button" data-exercise="${c.exercise}" aria-pressed="${pressed}">
          <span class="exercise-name">${c.exercise}</span>
          <span class="badge ${cssClass}">${label}</span>
        </button>`;
    })
    .join("");

  statusStrip.querySelectorAll(".badge-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      activeExercise = btn.dataset.exercise;
      renderBadges(lastClassifications);
      drawChart(lastClassifications.find((c) => c.exercise === activeExercise));
    });
  });
}

function drawChart(classification) {
  const dpr = window.devicePixelRatio || 1;
  const rect = chart.getBoundingClientRect();
  chart.width = rect.width * dpr;
  chart.height = rect.height * dpr;
  const ctx = chart.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, rect.width, rect.height);

  if (!classification || classification.points.length === 0) return;

  const points = classification.points;
  const padding = 32;
  const dates = points.map((p) => new Date(p.date).getTime());
  const values = points.map((p) => p.estimated_1rm);
  const minX = Math.min(...dates);
  const maxX = Math.max(...dates);
  const minY = Math.min(...values) * 0.95;
  const maxY = Math.max(...values) * 1.05;

  const xScale = (t) =>
    padding + (maxX === minX ? (rect.width - padding * 2) / 2 : ((t - minX) / (maxX - minX)) * (rect.width - padding * 2));
  const yScale = (v) =>
    rect.height - padding - ((v - minY) / (maxY - minY || 1)) * (rect.height - padding * 2);

  if (classification.slope !== null && classification.sessions_used >= 3) {
    const windowPoints = points.slice(-classification.sessions_used);
    const windowDates = windowPoints.map((p) => new Date(p.date).getTime());
    const windowValues = windowPoints.map((p) => p.estimated_1rm);
    const meanX = windowDates.reduce((a, b) => a + b, 0) / windowDates.length;
    const meanY = windowValues.reduce((a, b) => a + b, 0) / windowValues.length;
    const dayMs = 86400000;
    const valueAt = (t, slopePerDay) => meanY + slopePerDay * ((t - meanX) / dayMs);

    const x0 = windowDates[0];
    const x1 = windowDates[windowDates.length - 1];

    ctx.fillStyle = ACCENT_BAND;
    ctx.beginPath();
    ctx.moveTo(xScale(x0), yScale(valueAt(x0, classification.slope_ci_low)));
    ctx.lineTo(xScale(x1), yScale(valueAt(x1, classification.slope_ci_low)));
    ctx.lineTo(xScale(x1), yScale(valueAt(x1, classification.slope_ci_high)));
    ctx.lineTo(xScale(x0), yScale(valueAt(x0, classification.slope_ci_high)));
    ctx.closePath();
    ctx.fill();

    ctx.strokeStyle = ACCENT;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(xScale(x0), yScale(valueAt(x0, classification.slope)));
    ctx.lineTo(xScale(x1), yScale(valueAt(x1, classification.slope)));
    ctx.stroke();
  }

  ctx.fillStyle = TEXT;
  points.forEach((p) => {
    const x = xScale(new Date(p.date).getTime());
    const y = yScale(p.estimated_1rm);
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
  });

  ctx.font = "12px monospace";
  ctx.fillStyle = TEXT_MUTED;
  ctx.fillText(classification.exercise, padding, padding - 12);
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

  lastClassifications = data.classifications;
  if (!lastClassifications.some((c) => c.exercise === activeExercise)) {
    activeExercise = lastClassifications.length > 0 ? lastClassifications[0].exercise : null;
  }

  renderTable(data.rows, data.errors);
  renderBadges(lastClassifications);
  drawChart(lastClassifications.find((c) => c.exercise === activeExercise));
  saveLastLog(text);

  setStatus(`Parsed ${data.rows.length} session(s), ${data.errors.length} error(s).`, "ready");
}

async function boot() {
  setStatus("Booting Python runtime (Pyodide)…");
  try {
    const pyodide = await loadPlateauPackage();
    setStatus("Ready — paste a log or try the sample data.", "ready");
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze";
    demoBtn.disabled = false;

    analyzeBtn.addEventListener("click", () => {
      analyzeBtn.disabled = true;
      setStatus("Analyzing…");
      runAnalysis(pyodide)
        .catch((err) => setStatus(`Error: ${err.message}`, "error"))
        .finally(() => {
          analyzeBtn.disabled = false;
        });
    });

    demoBtn.addEventListener("click", () => {
      logInput.value = SAMPLE_LOG;
      analyzeBtn.click();
    });

    const storedLog = loadLastLog();
    if (storedLog) {
      logInput.value = storedLog;
      analyzeBtn.click();
    }
  } catch (err) {
    setStatus(`Failed to load Python runtime: ${err.message}`, "error");
  }
}

renderTable([], []);
renderBadges([]);
drawChart(null);
boot();
