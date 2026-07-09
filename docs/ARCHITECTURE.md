# Architecture

A concise map of the codebase for anyone (including a future session) picking this up cold.

## Overview

Plateau is a static, client-side site. The statistical core is a small, dependency-free Python
package (`plateau/`) executed in the browser via [Pyodide](https://pyodide.org). Nothing pasted
by the user ever reaches a server — the same Python is also tested natively with `pytest`.

```
plateau/            core Python package (parsing, statistics)
  parsing.py         parse_log() — text -> list[Entry] + errors
  analysis.py         estimate_one_rep_max(), fit_trend(), classify_exercise(), classify_log()
tests/               pytest suite mirroring the package (native Python, runs in CI)
site/                static site: what actually ships
  index.html          page markup — input panel, chart panel, results (badge) panel, table panel
  css/style.css       blueprint/technical design tokens + component styles (see docs/DESIGN.md)
  js/app.js           all page behavior: talks to Pyodide, renders table/badges/chart
  js/pyodide-loader.js loads Pyodide + copies plateau/ into its virtual filesystem
  vendor/             generated — plateau/ copied in by scripts/build_site.py (gitignored)
scripts/build_site.py the site's "build step": copies plateau/*.py into site/vendor/plateau/
docs/                VISION.md, BACKLOG.md, DESIGN.md, this file
```

## Data flow (paste to insight)

1. User pastes a log (or clicks "Try it now") and clicks Analyze (or presses Enter on it).
2. `app.js` hands the raw textarea text into Pyodide as a global (`log_text`) and runs an
   inline Python snippet:
   - `parsing.parse_log(text)` → `ParseResult(entries, errors)`. Malformed rows are collected
     as errors, not raised — a paste with a few typos still yields a usable partial result.
   - `analysis.classify_log(entries)` groups entries by exercise and calls
     `classify_exercise()` on each independently.
   - `classify_exercise()` sorts an exercise's sessions by date, takes the trailing window
     (default 6 sessions, minimum 4 to attempt a fit), converts each session to an
     estimated-1RM via the Epley formula, and fits `analysis.fit_trend()` — an ordinary
     least-squares regression of 1RM against calendar-day offset, with a 90% confidence
     interval on the slope (Student's-t, hardcoded critical-value table since the runtime has
     no scipy/numpy). If zero falls inside that interval, the lift is `stalled` (weeks_stalled
     = calendar span of the window, not session count); otherwise `trending_up` /
     `trending_down`. Fewer than 4 sessions → `insufficient_data`.
3. The Python snippet returns a plain dict (rows, errors, classifications — each classification
   carries its full point series for charting) which `app.js` converts to a JS object via
   `pyodide.toJs()`.
4. `app.js` renders three regions from that one result: the raw session table, the per-exercise
   badge strip (`renderBadges`), and the focused chart for the active exercise (`drawChart`) —
   scatter + fitted line + confidence band, pivoted at the trailing window's mean session so all
   three candidate slope lines (low/mid/high) cross at the same point.
5. Clicking a badge sets `activeExercise` and redraws the chart against the already-computed
   classifications — no re-run of Python.
6. On success, the pasted text is saved to `localStorage` (`plateau:last-log`); on the next page
   load `boot()` restores and re-analyzes it automatically.

## Why no numpy/scipy

`pyproject.toml` declares zero runtime dependencies deliberately: Pyodide can load extra
packages, but every extra package is another network fetch and version to pin before the "wow
moment" renders. The regression and its confidence interval are ~30 lines of stdlib `math`, and
the significance table only needs to cover small `dof` (the window is 4–6 sessions), so a
hardcoded Student's-t critical-value table is simpler and faster than pulling in scipy.

## Running things

```
pip install -e ".[dev]"
pytest                          # native Python test suite
ruff check .                    # lint

python3 scripts/build_site.py   # copy plateau/ into site/vendor/ (self-contained site build)
python3 -m http.server --directory site 8000   # serve locally; fetches vendor/ at runtime
```

`site/` is deployed as-is to `apps.charliekrug.com/plateau/` — a subpath, so every asset
reference in `index.html`/`app.js` is relative, never a leading-slash absolute path.

## Design system

`docs/DESIGN.md` is the single source of truth for the blueprint/technical direction (tokens,
layout intent, signature detail). `css/style.css` implements it directly — component classes
(`.panel`, `.badge`, `.badge-btn`, `.chart-panel`) map to sections of that doc.
