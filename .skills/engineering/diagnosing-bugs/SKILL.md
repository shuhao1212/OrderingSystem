---
name: diagnosing-bugs
description: Diagnosis loop for hard bugs and performance regressions. Use when the user says "diagnose"/"debug this", or reports something broken/throwing/failing/slow.
---

# Diagnosing Bugs

A discipline for hard bugs. Skip phases only when explicitly justified.

## Phase 1 — Build a feedback loop

**This is the skill.** Everything else is mechanical. If you have a **tight** pass/fail signal for the bug — one that goes red on _this_ bug — you will find the cause.

Ways to construct one (try in roughly this order):
1. **Failing test** at whatever seam reaches the bug — unit, integration, e2e.
2. **Curl / HTTP script** against a running dev server.
3. **CLI invocation** with a fixture input, diffing stdout against a known-good snapshot.
4. **Headless browser script** (Playwright / Puppeteer).
5. **Replay a captured trace.**
6. **Throwaway harness.**
7. **Property / fuzz loop.**
8. **Bisection harness.**
9. **Differential loop.**

### Tighten the loop
- Can I make it faster?
- Can I make the signal sharper?
- Can I make it more deterministic?

**Completion criterion:** a tight loop that goes red. No red-capable command, no Phase 2.

## Phase 2 — Reproduce + minimise

Run the loop. Watch it go red. Minimise to the smallest scenario that still goes red.

## Phase 3 — Hypothesise

Generate **3–5 ranked hypotheses** before testing any of them. Each must be **falsifiable**: "If <X> is the cause, then <changing Y> will make the bug disappear."

**Show the ranked list to the user before testing.**

## Phase 4 — Instrument

Change **one variable at a time.** Tool preference:
1. **Debugger / REPL inspection** if the env supports it.
2. **Targeted logs** at the boundaries that distinguish hypotheses.
3. Never "log everything and grep".

**Tag every debug log** with a unique prefix, e.g. `[DEBUG-a4f2]`.

## Phase 5 — Fix + regression test

Write the regression test **before the fix** — but only if there is a **correct seam** for it. If no correct seam exists, that itself is the finding — flag it.

## Phase 6 — Cleanup + post-mortem

- [ ] Original repro no longer reproduces
- [ ] Regression test passes
- [ ] All `[DEBUG-...]` instrumentation removed
- [ ] The hypothesis that turned out correct is stated in the commit/PR message
