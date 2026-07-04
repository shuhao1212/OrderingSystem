---
name: to-prd
description: Turn the current conversation into a PRD and publish it to the project issue tracker — no interview, just synthesis of what you've already discussed.
disable-model-invocation: true
---

# To PRD

This skill takes the current conversation context and codebase understanding and produces a PRD. Do NOT interview the user — just synthesize what you already know.

## Process

1. Explore the repo to understand the current state of the codebase.
2. Sketch out the seams at which you're going to test the feature.
3. Write the PRD using the template below.

## PRD Template

### Problem Statement
The problem that the user is facing, from the user's perspective.

### Solution
The solution to the problem, from the user's perspective.

### User Stories
A LONG, numbered list of user stories in the format:
1. As an <actor>, I want a <feature>, so that <benefit>

### Implementation Decisions
- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications
- Architectural decisions
- Schema changes
- API contracts

Do NOT include specific file paths or code snippets.

### Testing Decisions
- What makes a good test
- Which modules will be tested
- Prior art for the tests

### Out of Scope
A description of the things that are out of scope.

### Further Notes
Any further notes about the feature.
