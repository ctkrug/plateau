---
title: "I built a statistical plateau detector for lifters that runs entirely in the browser"
published: false
tags: python, webdev, pyodide, datascience
---

If you lift and keep a log, you have probably had this argument with yourself: is this lift
actually stuck, or did I just have a bad week? I built [Plateau](https://apps.charliekrug.com/plateau/)
to answer that with a test instead of a vibe. You paste your log (date, exercise, weight, reps)
and it tells you which lifts have genuinely stalled and for how many weeks. The whole thing runs
client-side, so nothing you paste ever leaves the page.

Here are the two build decisions I found most interesting.

## The plateau definition is a confidence interval, not a threshold

The naive version of this tool compares last week's top set to this week's and calls it. That
falls apart immediately, because a single top set is a noisy sample. Sleep, stress, bar speed,
and how honest your last rep was all move your estimated one-rep max around by more than a real
week of progress would.

So Plateau treats it as a signal-versus-noise problem. Each session becomes an estimated one-rep
max via the Epley formula (`weight * (1 + reps / 30)`), which puts sets of different rep counts
on one scale. Then it fits an ordinary least-squares regression of estimated 1RM against calendar
day over a trailing window, and computes a 90% confidence interval on the slope. The classification
falls out of one check:

```python
if fit.slope_ci_low <= 0 <= fit.slope_ci_high:
    # zero is a plausible slope given the noise: this lift is flat
    trend = Trend.STALLED
else:
    trend = Trend.TRENDING_UP if fit.slope > 0 else Trend.TRENDING_DOWN
```

If zero sits inside the interval, the lift is statistically indistinguishable from flat, and
that is what "plateaued" should mean. A lift can have a nonzero raw slope and still be called
plateaued, because the noise in the data swamps it. That is the whole point.

One detail I like: weeks-stalled is measured from the calendar span of the window, not the
session count. If you missed two weeks, that gap counts, so the number matches how long it has
actually been since the lift moved.

## No numpy, no scipy, on purpose

The stats core is plain Python running in the browser through
[Pyodide](https://pyodide.org). Pyodide can load numpy and scipy, but each one is another
multi-megabyte fetch before the first result renders, and I wanted the "paste and see" moment to
be fast.

It turns out you do not need them. The regression and its confidence interval are about thirty
lines of `math`. The only thing scipy would normally give you is the Student's-t critical value,
and since the window is only four to six sessions, the degrees of freedom are always small and
known ahead of time. So I hardcoded a t-table:

```python
_T90_TABLE = {1: 6.314, 2: 2.920, 3: 2.353, 4: 2.132, 5: 2.015, ...}
```

Beyond 30 degrees of freedom the normal approximation (1.645) is accurate to three decimals, and
in this app you never get close to that. A dependency-free core also means the exact same Python
is unit-tested natively with pytest in CI, and shipped to the browser unchanged by a tiny build
script that copies the package into the site and writes a manifest Pyodide reads at load.

## What I would do differently

The chart draws the scatter, the fitted line, and a shaded confidence band, but it has no
numbered axes yet. On graph-paper styling that reads fine, but a real y-scale would make the
band easier to reason about, and that is the first thing I would add next. I would also like to
handle a few more paste formats, since everyone's tracker exports something slightly different.

If you lift and log, try it on your own numbers: [apps.charliekrug.com/plateau](https://apps.charliekrug.com/plateau/).
Code is on [GitHub](https://github.com/ctkrug/plateau). I would genuinely like to know whether
the plateau calls match what your training feels like.
</content>
