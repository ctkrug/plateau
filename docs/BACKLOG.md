# Backlog

Epics and stories for the build. Every story has 1–3 verifiable acceptance criteria — concrete
checks, not vibes. Epic 1, story 1 is the wow moment and must be reachable before anything else
in the backlog is built.

## Epic 1 — Instant Plateau Detection (the wow moment)

- [x] **Paste-to-insight: instant plateau classification (the wow moment)**
  - Pasting a squat log whose last 5 weeks of estimated-1RM are flat (within noise) labels
    squat "stalled for 5 weeks" in the results view.
  - Pasting a log with a clearly increasing trend across the window labels that lift "trending
    up", not stalled.
  - The result renders in the same page load with no server round-trip (the Network tab shows
    no request after the initial page/Pyodide load).

- [x] **Rolling-window linear regression over estimated-1RM history**
  - Given ≥6 sessions for one exercise, the regression is computed over a trailing window
    (default: last 6 sessions) and refit as new sessions are added.
  - Unit test: synthetic perfectly-flat data returns a slope of ~0.
  - Unit test: synthetic monotonically-increasing data returns a positive slope.

- [x] **Noise-aware significance threshold on the regression slope**
  - A lift is classified "plateaued" only when the slope's confidence interval (e.g. 90%)
    includes zero over the window; otherwise "trending up" or "trending down".
  - Unit test: synthetic data with high session-to-session noise but no real trend is
    classified plateaued, not trending, despite a nonzero raw slope.
  - The weeks-stalled count reflects how many consecutive trailing sessions fall inside a flat
    regression window.

- [x] **Multi-exercise classification in one pass**
  - Pasting a log containing squat, bench, and deadlift entries classifies each independently
    and lists all three in the results.
  - An exercise with too few sessions to fit a window (<4) is labeled "insufficient data"
    rather than misclassified.

## Epic 2 — Visualization & Multi-Lift Dashboard

- [x] **Per-lift regression chart with confidence band**
  - Chart draws the estimated-1RM scatter, the fitted regression line, and a shaded confidence
    band for the active exercise.
  - Chart recomputes and redraws on window resize at `devicePixelRatio` for crisp rendering.

- [x] **Lift status summary strip**
  - Each classified exercise shows as a labeled badge (stalled Xwk / trending up / trending
    down / insufficient data) beneath the chart.
  - Clicking a badge switches the chart to that exercise.

- [x] **Design polish: interaction states across all controls**
  - Every control (textarea, button, badge) has themed hover/focus-visible/active states per
    `docs/DESIGN.md` tokens.
  - Squint test and 1440/768/390 resize pass with no unstyled native widgets remaining.

## Epic 3 — Data Handling & Robustness

- [ ] **"Try it now" demo dataset loader**
  - A visible button loads a realistic multi-exercise sample log and immediately runs analysis.
  - Works before the user has pasted anything (the first-visit empty state offers it).

- [ ] **Persist last-pasted log in localStorage**
  - Reloading the page restores the previously pasted log and its classification without
    re-pasting.
  - Replacing the textarea contents and re-analyzing overwrites the stored value.

- [x] **Graceful handling of sparse/irregular logging**
  - A log with missed weeks (gaps >14 days between sessions for one exercise) still classifies
    without crashing, and the weeks-stalled count accounts for calendar time, not just session
    count.
  - Unit test covers a gap-containing synthetic log.

## Epic 4 — Polish, Accessibility & Ship

- [ ] **Full responsive pass**
  - No horizontal scroll or overlapping elements at 390px, 768px, and 1440px.
  - Chart and paste panel both remain usable (no dead empty margins) at all three widths.

- [ ] **Accessibility pass**
  - Full keyboard-only flow: paste, tab to Analyze, tab through badges, no keyboard trap.
  - Status updates announce via the existing `aria-live` region; text contrast ≥4.5:1 verified
    against `docs/DESIGN.md` tokens.

- [ ] **Ship gate: design + QA sign-off**
  - Page matches `docs/DESIGN.md` direction and tokens (favicon present, wordmark styled, no
    anti-generic bans present).
  - CI green on `main`; all other backlog stories checked off or explicitly deferred with a
    stated reason.
