# Design direction

## Aesthetic direction

**Plateau is a blueprint/technical instrument.** Deep blueprint-navy canvas, hairline cyan
grid and rule lines, monospace annotations — it should feel like a drafting table for your
training data, not a fitness-app dashboard. The point is precision: this tool exists because
"did the number go up" isn't rigorous enough, and the visual language says so before a single
chart renders.

This is a deliberate departure from the soft-depth dark-glass and neo-brutalist directions used
on recent ships — blueprint direction hasn't been used yet and fits a statistics tool naturally
(graph paper is already a plotting surface).

## Tokens

| Token | Value | Use |
|---|---|---|
| `--bg` | `#0b1f33` | page background — deep blueprint navy |
| `--surface-1` | `#0f2942` | panels, cards |
| `--surface-2` | `#15334f` | raised panels, input fields |
| `--text` | `#eaf2fb` | primary text |
| `--text-muted` | `#8fa8c2` | secondary text, labels, axis ticks |
| `--accent` | `#5ee7ff` | primary accent — grid lines, links, trending-up |
| `--accent-support` | `#ffb347` | secondary accent — plateaued/stalled flag |
| `--success` | `#6ee7b7` | trending up confirmation |
| `--danger` | `#ff6b6b` | parse errors, invalid input |
| `--font-display` | "Space Mono", ui-monospace, monospace | wordmark, headings, data labels |
| `--font-body` | "Inter", system-ui, sans-serif | body copy, inputs, table text |
| `--space` | 8px base scale (8/16/24/32/48/64) | all spacing |
| `--radius` | 2px | sharp, drafted corners — never pill-shaped |
| `--edge` | 1px solid rgba(94, 231, 255, 0.35) | hairline borders instead of drop shadows |
| `--glow` | 0 0 12px rgba(94, 231, 255, 0.25) | focus/active annotation glow, used sparingly |
| `--motion-ui` | 160ms ease-out | control transitions |
| `--motion-feedback` | 90ms ease-out | chart/badge state changes |

Surfaces get depth from the hairline edge + faint grid overlay (a repeating linear-gradient at
1px intervals, 4% opacity) rather than soft shadows — blueprints are flat with drafted lines,
not glassy.

## Layout intent

The hero is the **per-lift trend chart** — a rolling-regression line with a shaded confidence
band, drawn on a graph-paper grid, taking the majority of the viewport. A compact paste-in
panel (textarea + "Analyze" button) sits alongside it on desktop; a lift-status summary strip
(exercise name, badge, weeks-stalled count) runs beneath.

- **1440×900 desktop:** two-column layout — paste panel + lift list in a ~360px left rail,
  chart canvas filling the remaining ~1080px (≥60vh tall). Status strip spans full width below.
- **390×844 phone:** single column, stacked top-to-bottom — paste panel first (collapsed to a
  compact input by default), chart full-width beneath at a minimum 50vh, status strip last.
  No dead margins: the chart canvas always fills its container edge-to-edge.

## Signature detail

The wordmark "PLATEAU" renders over a faint animated topographic contour line that draws itself
in (stroke-dashoffset animation, ~1.2s, once on load) beneath the letters — a literal flatline
motif that also doubles as the loading indicator while Pyodide boots.

## Games/toys juice plan

Not applicable — Plateau is a data tool, not a game or playful toy.
