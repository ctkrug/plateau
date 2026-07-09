# Plateau

Paste your logged lift numbers — date, exercise, weight, reps — and Plateau tells you which
lifts have **actually** stalled, and for how long. No app to migrate your log into, no account,
no server: it runs a real rolling-regression statistical test entirely in your browser.

## Why

"Did this week's max go up?" is a noisy question — one good or bad session either way can make
a lift look plateaued or trending when it isn't. Plateau instead fits a rolling linear
regression over your estimated-1RM history per exercise and asks a sharper question: is the
slope over the recent window statistically distinguishable from zero, given the noise in your
own data? If it isn't, that lift is plateaued — and Plateau reports for how many weeks.

## How it works

1. Paste a log: `date, exercise, weight, reps` (one session per line, CSV or TSV).
2. Each session is converted to an estimated one-rep max (Epley formula).
3. A rolling-window linear regression is fit over each exercise's 1RM history.
4. A noise-aware significance threshold (confidence interval on the slope) decides whether the
   trend is real movement or noise around a flat line.
5. Each lift is labeled — trending up, trending down, or plateaued for N weeks — in one glance.

## Stack

Plateau is a static, client-side site. The statistical core is plain Python
(`plateau/`), executed in the browser via [Pyodide](https://pyodide.org) — no server, no build
step, no data ever leaves your machine. The same Python package is tested natively with
`pytest` in CI.

```
plateau/        core Python package: parsing, 1RM estimation, rolling regression
tests/          pytest suite for plateau/
site/           static site (HTML/CSS/JS) that loads plateau/ into Pyodide
docs/           vision, backlog, and design direction
```

## Status

Early scaffold — see [`docs/VISION.md`](docs/VISION.md) for the plan and
[`docs/BACKLOG.md`](docs/BACKLOG.md) for what's built vs. planned.

## Local development

```
pip install -e ".[dev]"
pytest
```

The site under `site/` is plain static HTML/JS — open `site/index.html` via any local static
file server (it fetches the Python source at runtime, so `file://` won't work with most
browsers' CORS rules):

```
python3 -m http.server --directory site 8000
```

## License

MIT — see [`LICENSE`](LICENSE).
