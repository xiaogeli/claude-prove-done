---
name: Trigger miss or false fire
about: A claim slipped past the hook (false negative), or the hook fired on something that wasn't a claim (false positive)
title: "trigger: <short description>"
labels: trigger
---

## Direction

- [ ] **Missed** a real claim (false negative — hook should have fired and didn't)
- [ ] **Fired** on something that wasn't a claim (false positive — hook fired and shouldn't have)

## The phrase

The exact text the agent wrote, copied from a real transcript (paraphrased ok if you can't share):

> <paste here>

## Context

What was the agent actually doing? Was there a tool call this turn, and what was its input?

- Tool calls this turn: <e.g. `Read src/foo.py` / none>
- The claim referred to: <file / function / "nothing specific" / etc.>

## Why the current logic mishandles it

(Optional but very helpful.) Which part of the pipeline is wrong?

- Trigger regex didn't match? Match the right pattern but it was inside a code fence / blockquote / future-tense clause? Subject extraction missed the identifier? Subject was extracted but didn't substring-match a tool input?

## Proposed fix

(Optional.) New regex, new intent-marker, addition to `EVIDENCE_TOOLS`, etc.
