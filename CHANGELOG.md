# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Rolling-window regression (`fit_trend`) with a 90% confidence interval on the slope, and
  `classify_exercise`/`classify_log` to label each exercise stalled / trending up / trending
  down / insufficient data — the project's wow moment.
- Lift-status badge strip and a focused per-lift chart (scatter, fitted trend line, shaded
  confidence band) that switches exercise on badge click.
- "Try it now" sample-dataset button and localStorage persistence of the last-pasted log.
- `docs/ARCHITECTURE.md` mapping the codebase and data flow.
- Project scaffold: `plateau` Python package (log parsing, estimated-1RM calculation), pytest
  suite, and a static Pyodide-powered site under `site/`.
- Vision, design direction, and build backlog docs.

### Fixed

- CSS grid tracks and an unwrapped results table caused horizontal overflow at phone widths.
- Clicking a lift-status badge dropped keyboard focus to `<body>` on rebuild.
