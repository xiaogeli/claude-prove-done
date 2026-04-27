---
name: prove-done
description: Before claiming a task is done/fixed/added/scanned, verify with a tool call. Triggers on completion claims ("done", "fixed", "added", "已修", "已加", "已扫", "已记", "已 commit") and forces a verification checklist. Also catches negative existence claims ("X doesn't exist", "no tests for Y", "X 没有 Y"). Use this skill whenever you are about to assert that something has been completed, that something exists, or that something does not exist.
---

# prove-done

You are about to make a claim about state — that something is done, present, or absent. **Memory is not evidence.** This skill blocks the claim until you have verified it with a tool call in this turn.

## When this skill activates

Activate **before sending** any message that contains, in any language, a phrase asserting completion or non-existence. Common triggers:

**Completion claims (English):** done, fixed, added, removed, deleted, updated, committed, pushed, scanned, checked, ran, tested, implemented, wired up, hooked up, in place, taken care of, sorted, handled.

**Completion claims (Chinese):** 已修 / 已加 / 已扫 / 已记 / 已删 / 已改 / 已写 / 已 commit / 已 push / 已经做了 / 已经有了 / 之前讨论过 / 搞定了 / 处理好了.

**Negative-existence claims:** "X doesn't exist", "no tests for Y", "there's no Z", "missing", "0 tests", "not implemented", "X 不存在", "X 没有 Y", "没测试", "没文档".

**Past-state claims about your own work:** "I already did X", "I scanned that", "I checked earlier", "上一轮做过了".

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
