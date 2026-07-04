---
name: code-review
description: Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Standards and Spec. Use when the user wants to review a branch, PR, or asks to "review since X".
---

# Code Review

Two-axis review of the diff between `HEAD` and a fixed point:

- **Standards** — does the code conform to this repo's documented coding standards?
- **Spec** — does the code faithfully implement the originating issue / PRD / spec?

Both axes run as **parallel sub-agents** so they don't pollute each other's context.

## Process

### 1. Pin the fixed point
Whatever the user said — a commit SHA, branch name, tag, `main`, `HEAD~5`, etc.

### 2. Identify the spec source
Look for the originating spec: issue references in commit messages, user-passed path, PRD/spec files under `docs/`, `specs/`, or `.scratch/`.

### 3. Identify the standards sources
Anything in the repo that documents how code should be written (`CODING_STANDARDS.md`, `CONTRIBUTING.md`). Always carry the **smell baseline**: Mysterious Name, Duplicated Code, Feature Envy, Data Clumps, Primitive Obsession, Repeated Switches, Shotgun Surgery, Divergent Change, Speculative Generality, Message Chains, Middle Man, Refused Bequest.

### 4. Spawn both sub-agents in parallel
- **Standards sub-agent**: report per file/hunk where the diff violates documented standards or baseline smells.
- **Spec sub-agent**: report requirements missing, scope creep, or implementation that looks wrong.

### 5. Aggregate
Present both reports under `## Standards` and `## Spec` headings. End with a one-line summary.

## Why two axes

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.
