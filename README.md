# Plateau

**▶ Live demo — [apps.charliekrug.com/plateau](https://apps.charliekrug.com/plateau/)**

[![CI](https://github.com/ctkrug/plateau/actions/workflows/ci.yml/badge.svg)](https://github.com/ctkrug/plateau/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

See which lifts have actually stalled. Paste your logged numbers (date, exercise, weight, reps)
and Plateau runs a real rolling-regression significance test, per exercise, and tells you which
lifts are genuinely plateaued and for how many weeks. No account, no server, no migrating your
log into another app: it runs entirely in your browser.

## Who it's for

Intermediate and advanced lifters who already log every session somewhere (a spreadsheet, a
notes app, a tracker you can export) and keep hitting the same weights. If you've ever stared at
a column of numbers wondering "is this lift actually stuck, or did I just have a bad week?",
that's the question Plateau answers.

## Why a regression instead of "did the number go up"

One week over another is a single noisy sample. Sleep, stress, bar speed, and rep quality move
your top set around enough that one comparison gives both false alarms and false comfort. Plateau
fits a rolling linear regression over each exercise's estimated-1RM history and asks a sharper
question: over the recent window, is the slope statistically distinguishable from zero given the
noise in *your own* data? If it isn't, the lift is plateaued, and Plateau reports for how long.

## What you get back

Paste a multi-exercise log and every lift is classified independently in one pass:

```
squat      Stalled 5wk       slope inside the 90% CI band around zero
bench      Trending up       estimated 1RM rising 4.2 lb/week
deadlift   Trending down     estimated 1RM falling, CI clear of zero
overhead   Insufficient data fewer than 4 sessions to fit a window
```

Each lift also gets a chart: the estimated-1RM scatter, the fitted trend line, and a shaded
confidence band, so the call is visually legible and not just a label.

## How it works

1. Paste a log: `date, exercise, weight, reps` (one session per line, CSV or TSV).
2. Each session becomes an estimated one-rep max via the Epley formula.
3. A rolling-window linear regression is fit over each exercise's 1RM history.
4. A 90% confidence interval on the slope decides real movement vs. noise around a flat line.
5. Each lift is labeled trending up, trending down, plateaued for N weeks, or insufficient data.

## Stack

Plateau is a static, client-side site. The statistical core is plain Python (`plateau/`) with
zero runtime dependencies, executed in the browser via [Pyodide](https://pyodide.org). No server,
no data ever leaves your machine. The same Python package is tested natively with `pytest` in CI.

```
plateau/        core Python package: parsing, 1RM estimation, rolling regression
tests/          pytest suite for plateau/
site/           static site (HTML/CSS/JS) that loads plateau/ into Pyodide
docs/           vision, backlog, design direction, and architecture map
```

## Run it locally

```
pip install -e ".[dev]"
pytest                          # native Python test suite
ruff check .                    # lint
```

The site under `site/` is plain static HTML/JS. Build the self-contained bundle and serve it (it
fetches the Python source at runtime, so `file://` won't work with most browsers' CORS rules):

```
python3 scripts/build_site.py                  # copy plateau/ into site/vendor/
python3 -m http.server --directory site 8000   # then open http://localhost:8000
```

## License

MIT. See [`LICENSE`](LICENSE).

---

More of Charlie's projects → [apps.charliekrug.com](https://apps.charliekrug.com)
</content>
</invoke>
