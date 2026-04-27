---
name: prove-done
description: Before claiming a task is done/fixed/added/scanned, verify with a tool call. Triggers on completion claims ("done", "fixed", "added", "scanned", "committed", "all set", "wrapped up") and forces a verification checklist. Also catches negative-existence claims ("X doesn't exist", "no tests for Y", "missing", "0 tests"). Use this skill whenever you are about to assert that something has been completed, that something exists, or that something does not exist.
---

# prove-done

You are about to make a claim about state — that something is done, present, or absent. **Memory is not evidence.** This skill blocks the claim until you have verified it with a tool call in this turn.

## When this skill activates

Activate **before sending** any message that contains a phrase asserting completion or non-existence. Common triggers:

**Completion claims:** done, fixed, added, removed, deleted, updated, patched, reverted, moved, renamed, merged, applied, shipped, committed, pushed, scanned, checked, tested, ran, verified, implemented, wired up, hooked up, set up, sorted, handled, taken care of, in place, all set, good to go, wrapped up.

**Negative-existence claims:** "X doesn't exist", "no tests for Y", "there's no Z", "missing", "0 tests", "not implemented", "X isn't tested", "X isn't covered".

**Past-state claims about your own work:** "I already did X", "I scanned that", "I checked earlier", "we discussed this before".

If your draft message contains any of these, stop and run the checklist below before sending.

## The verification checklist

For every triggering claim, do **one of**:

1. **Read the file** — open the exact path and confirm the change/content is present at the line you claim.
2. **Grep the symbol** — search for the function/flag/string across the relevant scope. A claim of "0 tests for X" requires `grep -r "X" tests/`.
3. **Run the command** — for "I committed", run `git log -1`. For "I pushed", run `git status` / `git log @{u}..`. For "tests pass", actually run them.

Then in your reply, **cite the evidence** inline: file path + line number, command + exit code, or grep hit count. No citation, no claim.

## What counts as evidence

- ✅ `Read src/foo.py:42-58 — the early-return is on line 47`
- ✅ `git log -1 → commit abc1234 "fix: ..."` 
- ✅ `Grep "_cross_check_price" tests/ → 6 matches in tests/test_executor.py`
- ❌ "I'm sure I added it"
- ❌ "Based on what I did earlier"
- ❌ "It should be there"

## Relevance matters — not just "any tool call"

The companion Stop hook does **subject-relevance matching**, not just "did this turn use a tool". If you claim something specific (a file path, a function name, a line number, a backticked symbol), the hook expects to see that subject appear in a Read/Grep/Glob/Bash input from the same turn. Reading an unrelated file does **not** satisfy a claim about a different file.

Practical consequence: when you make a specific claim, the tool call you cite must actually touch the thing you're claiming about. If you grep for a function, the grep pattern should be the function name (or include it). If you assert "fixed src/foo.py:47", a Read of `src/foo.py` is the evidence; a Read of `src/bar.py` is not.

For purely generic claims ("done.", "all set."), any evidence-tool call this turn passes the check, but those generic claims are also the easiest for the user to push back on — prefer specific claims with citations.

## Special trap: re-scanning the same file

A file you scanned one turn ago is **not** verified for this turn. Memory of "I just looked at this" is exactly the failure mode this skill exists to prevent. Re-read every time the claim is made fresh. Two seconds of Read beats one round of being caught wrong.

## Why this exists

Saying "done" and being wrong is worse than saying "not yet". The first destroys trust; the second just costs a turn. This skill enforces the cheap check that prevents the expensive failure.

## Scope

Applies to claims about:
- Files, code, tests, commits, branches, deploys
- Memory entries, pending lists, todo items
- Documentation, configs, environment
- Anything where "is it actually there?" can be answered by a tool call

Does **not** apply to opinions, recommendations, or future-tense plans ("I will add X") — only to assertions of current or past state.
