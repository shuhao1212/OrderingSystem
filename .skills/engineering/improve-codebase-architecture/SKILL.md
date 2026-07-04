---
name: improve-codebase-architecture
description: Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
disable-model-invocation: true
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones.

## Process

### 1. Explore
Walk the codebase and note where you experience friction:
- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts are untested, or hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it?

### 2. Present candidates as an HTML report
Write a self-contained HTML file. For each candidate, render a card with:
- **Files** — which files/modules are involved
- **Problem** — why the current architecture is causing friction
- **Solution** — plain English description of what would change
- **Benefits** — explained in terms of locality and leverage
- **Before / After diagram** — side-by-side
- **Recommendation strength** — `Strong`, `Worth exploring`, `Speculative`

### 3. Grilling loop
Once the user picks a candidate, run a grilling session to walk the design tree — constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.
