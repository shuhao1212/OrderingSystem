---
name: grill-me
description: A relentless interview to sharpen a plan or design.
disable-model-invocation: true
---

# Grill Me

Run a `/grilling` session: interview the user relentlessly about a plan or design until every branch of the decision tree is resolved.

## Process

1. Ask the user what they want to build or plan.
2. For each answer, ask probing questions:
   - "What happens if...?"
   - "How will this handle edge case X?"
   - "What's the fallback if this fails?"
   - "Is this the simplest approach?"
3. Continue until all branches of the decision tree are resolved.
4. Summarize the final plan with all decisions documented.
