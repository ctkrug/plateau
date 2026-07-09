# Vision

## The problem

Lifters who track their training end up staring at a spreadsheet or app trying to answer one
question: "is this lift actually stuck, or does it just look flat because last week was a bad
day?" The honest answer requires separating signal from noise — session-to-session variance in
weight, reps, sleep, and stress is large enough that eyeballing a table or a single-week
comparison gives false positives and false negatives both. Existing lift trackers log the data
well but don't answer this question; they show a graph and leave the interpretation to you.

## Who it's for

Intermediate-to-advanced lifters who already log their training somewhere (a notes app, a
spreadsheet, a dedicated tracker with export) and want a straight statistical answer about
which lifts have genuinely stalled, without migrating their existing log into a new app or
creating an account.

## The core idea

Paste a log — date, exercise, weight, reps — and get back, per exercise, one of: trending up,
trending down, or plateaued for N weeks. The classification comes from a rolling linear
regression fit over each exercise's estimated-1RM history: if the regression slope's confidence
interval includes zero over the recent window, the lift is statistically indistinguishable from
flat, and that's a real plateau, not vibes. This is the one thing the tool does, and it does it
well — no workout planning, no social features, no logging UI to replace what the lifter
already uses.

## Key design decisions

- **Entirely client-side.** The statistical core is plain Python, executed via Pyodide in the
  browser. Nothing pasted ever leaves the page — no server, no account, no data retention
  concerns, and it costs nothing to run at any scale.
- **Works with data you already have.** The input is a generic date/exercise/weight/reps paste
  (CSV or TSV), not a proprietary log format — the edge over incumbent trackers is exactly that
  there's nothing to migrate.
- **Real statistics, not a threshold.** "Did the max go up this week" is a single noisy sample;
  a rolling regression with a significance test on the slope is the minimum rigor needed to
  call something a plateau with any confidence.
- **One question, answered well.** No feature creep into programming, macros, or social —
  scope stays narrow so the core analysis stays trustworthy and the UI stays simple.

## What "v1 done" looks like

- Paste a multi-exercise log and, within one interaction, see each lift labeled trending up /
  trending down / plateaued-for-N-weeks, backed by the rolling-regression significance test
  (not a naive week-over-week comparison).
- A per-lift chart shows the estimated-1RM history with the fitted regression line and its
  confidence band, so the classification is visually legible, not just a text label.
- Malformed or sparse log rows degrade gracefully (inline errors, not a crash) rather than
  blocking the whole paste.
- The page is fully responsive (phone through desktop), matches `docs/DESIGN.md`'s blueprint
  direction, and ships with a designed empty/loading/error state — no unstyled native controls.
- CI is green on every push; the statistical core has unit test coverage for the regression and
  significance logic, not just parsing.
