# claude-prove-done

> **Memory ≠ evidence.**
> *The missing beat between "I'm done" and "you can verify."*

A Claude Code **skill + hook** that makes AI coding agents see the one mistake under every false "done": the silent belief that *remembering having intended to do it* is the same as *having actually done it*. It isn't. From inside the agent's head, the two leave the same trace — a working-memory token that reads "taken care of." From outside, on disk, they're radically different. The user pays the gap. This project does exactly one thing — in the moment before the agent writes "done / fixed / 已修", it makes the agent read the difference right-way-up.

Pairs naturally with [`claude-think-twice`](https://github.com/xiaogeli/claude-think-twice): *think-twice* stops `--rushed` before `git push`; *prove-done* stops `--imagined` before "I'm done."

---

## The 2-minute story

The agent already knows the rule: *don't claim something is done unless you can prove it.* It will even quote that rule back when asked. And yet, after a multi-step task, the agent:

1. Finishes step 4 of 5, intends to do step 5, gets distracted by user feedback on step 2.
2. A turn later, summarizes: *"All five items are added to the pending list."* Step 5 is, in fact, missing.
3. User says *"are you sure? scan it again."*
4. Agent re-scans, hits the file, somehow still misses what's plainly there — because by now the working-memory token says "scanned, all good," and that token is louder than the file contents.
5. User catches it on the third pass. The 20 seconds the agent saved by not re-reading the first time become two hours of mistrust the user now spends double-checking everything else.

The account is inverted, the same way it is for [`claude-think-twice`](https://github.com/xiaogeli/claude-think-twice) — the agent booked one round-trip on its own ledger ("I remember doing it"); the user paid three or four on theirs ("I have to verify what you said"). From inside the agent's loop, the working-memory token *I'm done* and the disk reality *it's done* feel like the same fact. They aren't.

`claude-prove-done` is the beat that forces the agent to discriminate the two before sending the message.

---

## What this really is

This is not a linter. Linters check code. **This checks whether the agent confused remembering with knowing.**

The failure isn't laziness or forgetfulness — the agent knows the rule. It runs on one silent belief: *if my representation says "done", then it's done.* That belief is wrong because the representation gets written when the agent *intends* to do something and again when the agent *did* do something, and from inside there's no signal to tell the two writes apart. Only the disk has the discriminating signal. So the rule is mechanical: **before claiming "done", read the disk; cite what you read.**

Once an agent re-reads its own working-memory token *I'm done* in the same beat as the file it claims to have edited, it self-corrects. Not because the hook forced it. Because the two no longer match. **Memory is not evidence.** That is the whole thesis; the rest is plumbing.

---

## Demo

> **User:** add `risk_manager`, `data_guardian`, `multi_agent` to the pending list.
>
> **Agent:** edits `pending.md`, drafts: *"Done — added all three to the pending list."*
>
> Stop hook fires:
>
> ```
> prove-done: this turn claims completion (Done, added) about specific
> subjects (data_guardian, multi_agent, risk_manager, pending.md), but
> no Read/Grep/Glob/Bash call this turn referenced any of them. Open
> the file or grep the symbol so the claim has actual evidence behind
> it, then cite file:line or hit count. If you can't verify, say
> 'not yet' instead.
> ```
>
> Agent re-reads `pending.md` → finds `multi_agent` is missing — the edit only landed two of three lines → adds the third → confirms with citation: *"Done — `pending.md:14-16` now contains all three. Verified by re-read."*

That third item, without the beat, would have been a *"yes, all done"* that the user catches a turn later, after they've already stopped paying attention. The skill is the *prompt* that teaches the discrimination; the hook is the *backstop* that catches the turn where the prompt didn't fire.

---

## Why not pre-commit / lints / git-guardrails?

Use them all — they're complementary, not competitors.

- **pre-commit, husky, lefthook** run linters and tests. They check the *code*. They don't notice when an agent *says* the code is fixed but actually didn't run the linter.
- **[git-guardrails](https://github.com/mattpocock/skills/tree/main/git-guardrails-claude-code)** stops `git push --force`, `git reset --hard`, and other destructive commands. It checks for *malice or accidents in shell commands*. It doesn't check assistant prose.
- **[claude-think-twice](https://github.com/xiaogeli/claude-think-twice)** checks whether the agent confused **fast with efficient**, before `git push`. Different beat, different moment.
- **claude-prove-done** checks whether the agent confused **memory with evidence**, before *"I'm done."* It scans the agent's own outgoing prose for completion claims and asks whether the same turn produced any disk-touching tool call relevant to the claim's subject.

One line: *git-guardrails stops `--force`. think-twice stops `--rushed`. prove-done stops `--imagined`.*

---

## Install

### Project-local (recommended for teams)

Commit `.claude/` so everyone gets the same backstop:

```bash
git clone https://github.com/xiaogeli/claude-prove-done.git /tmp/claude-prove-done
mkdir -p .claude/skills .claude/hooks
cp -r /tmp/claude-prove-done/.claude/skills/prove-done .claude/skills/
cp /tmp/claude-prove-done/.claude/hooks/prove-done-check.sh .claude/hooks/
cp /tmp/claude-prove-done/.claude/hooks/prove-done-check.py .claude/hooks/
chmod +x .claude/hooks/prove-done-check.sh
```

Then merge the `hooks` block from `/tmp/claude-prove-done/.claude/settings.json` into your project's `.claude/settings.json`, and commit `.claude/skills/prove-done/`, both `.claude/hooks/prove-done-check.*`, and the updated `settings.json`.

### Personal (all your projects)

Drop the skill and hook under `~/.claude/`:

```bash
git clone https://github.com/xiaogeli/claude-prove-done.git /tmp/claude-prove-done
mkdir -p ~/.claude/skills ~/.claude/hooks
cp -r /tmp/claude-prove-done/.claude/skills/prove-done ~/.claude/skills/
cp /tmp/claude-prove-done/.claude/hooks/prove-done-check.sh ~/.claude/hooks/
cp /tmp/claude-prove-done/.claude/hooks/prove-done-check.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/prove-done-check.sh
# Merge the `hooks` block from /tmp/claude-prove-done/.claude/settings.json into ~/.claude/settings.json
```

### Windows (PowerShell)

```powershell
git clone https://github.com/xiaogeli/claude-prove-done.git $env:TEMP\claude-prove-done
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills","$env:USERPROFILE\.claude\hooks"
Copy-Item -Recurse "$env:TEMP\claude-prove-done\.claude\skills\prove-done" "$env:USERPROFILE\.claude\skills\"
Copy-Item "$env:TEMP\claude-prove-done\.claude\hooks\prove-done-check.*" "$env:USERPROFILE\.claude\hooks\"
# Merge the hooks block from $env:TEMP\claude-prove-done\.claude\settings.json into $env:USERPROFILE\.claude\settings.json
```

> **Important — restart Claude Code after install.** Skills hot-reload, but **hooks register only at session start**. Until you restart, completion claims will NOT be blocked. To verify both installed correctly: restart → ask Claude *"list your skills"* (should include `prove-done`) → give it a tiny task and watch it cite Read/Grep output instead of asserting from memory.

## Requirements

- **Python 3** on PATH (the hook prefers `python3`, falls back to `python`, then `py`). If no Python is found, the hook degrades to a no-op rather than blocking everything.
- A POSIX-ish shell (`bash`). On Windows that means git-bash or WSL — Claude Code already needs one.

---

## How it works

### The skill (the prompt half)

Lives at `.claude/skills/prove-done/SKILL.md`. When loaded, it teaches the agent the rule in words: *before saying done/fixed/已修, run a Read or Grep that touches the thing you're claiming about, then cite the result inline (file:line, command output, hit count). If you can't verify, say "not yet" instead.* The skill also names the specific failure mode — re-claiming "done" about something you already scanned this conversation, when the working-memory token feels truthy but the file hasn't been re-examined this turn.

### The hook (the backstop half)

`.claude/hooks/prove-done-check.sh` (a thin bash launcher) → `.claude/hooks/prove-done-check.py` (the logic). Wired as a Claude Code **Stop hook** in `.claude/settings.json` — fires once per assistant turn, just before the message is finalized.

For each Stop event:

1. Parse the hook payload from stdin → get `transcript_path` and `stop_hook_active`. If `stop_hook_active` is true (we already fired and Claude is re-stopping), exit 0 — that's the loop guard.
2. Read the transcript JSONL. Walk back to the last user message; everything after it is "this turn." Concat the assistant text blocks; collect every `tool_use` block (name **and** input).
3. Strip whole-text constructs that aren't real claims: fenced code (`` ``` ``…`` ``` ``), blockquote lines (`> ...`).
4. Split into sentences (English + Chinese punctuation), and per sentence strip inline backticks for trigger detection only — keep the original sentence around for subject extraction.
5. For each sentence, find trigger words against ~40 patterns (English + Chinese, completion + negative-existence). Skip a trigger if a future/intent marker (`I'll`, `to fix`, `going to`, `should`, `would`, `if`, `how do I`, Chinese 不/没/要/想/准备/打算) sits within 30 characters before it.
6. From each surviving claim sentence, extract **subjects**: file paths (`foo.py`, `src/x/y.ts`), backticked tokens, snake_case / camelCase / `_prefixed` identifiers (`_cross_check_price`), and `line N` references.
7. Decide:
   - **Specific claim, relevant evidence:** subjects exist and at least one appears as a substring in some Read/Grep/Glob/Bash input this turn → exit 0.
   - **Specific claim, no relevant evidence:** subjects exist but no tool input mentions any of them → exit 2 with a stderr that names both the matched triggers and the unmatched subjects.
   - **Generic claim, some evidence:** no subjects extracted (bare *"Done."*) but at least one Read/Grep/Glob/Bash call happened → exit 0 (lenient fallback).
   - **Generic claim, zero evidence:** no subjects, no evidence-tool call → exit 2.

The relevance check is the part that makes this hook bite. *"Any tool call passes"* is too easy to game (a Read of an unrelated file would satisfy it); *"every word must be cited"* is too noisy. The middle ground — *if you named something specific, your tool call has to have touched it* — catches the actual failure mode.

---

## Triggers

**Completion (English):** done, fixed, added, removed, deleted, updated, patched, reverted, moved, renamed, merged, applied, shipped, committed, pushed, scanned, checked, tested, ran, verified, implemented, wired up, hooked up, set up, sorted, handled, taken care of, in place, all set, good to go, wrapped up, ready to go, *it's/that's/now (done|fixed|ready|complete|working)*.

**Completion (Chinese):** 已修 / 已加 / 已扫 / 已记 / 已删 / 已改 / 已写 / 已 commit / 已 push / 已经做了 / 已经有了 / 搞定了 / 处理好了 / 完成了 / 加好了 / 修好了.

**Negative existence:** doesn't exist, no tests, zero tests, missing, not implemented, *isn't (implemented|tested|covered|there)*, 不存在 / 没测试 / 没文档 / 没实现 / 没有…(测试|文档|实现|覆盖).

The full list lives in `TRIGGER_PATTERNS` in [`.claude/hooks/prove-done-check.py`](./.claude/hooks/prove-done-check.py). New phrases land via PRs that cite a real-world transcript line — see [`CONTRIBUTING.md`](./CONTRIBUTING.md).

---

## Limitations (read before installing)

Honest accounting of what the hook can and can't do, after the v2 rewrite.

**What the hook now does correctly (covered by tests):**
- Strips fenced code blocks and blockquote lines before scanning, so code mentions of `done` / `fixed` and quoted user text don't trigger.
- Strips inline backticked code per sentence — same reason.
- Skips triggers preceded by future/intent markers within ~30 chars: *"I'll add"*, *"to fix"*, *"going to"*, *"should/would/could"*, *"if"*, *"how do I"*, plus Chinese 不/没/要/想/准备/打算.
- Catches paraphrases the v1 missed: *"all set"*, *"wrapped up"*, *"good to go"*, *"taken care of"*, *"isn't tested"*, plus 完成了/加好了/修好了.
- Does **subject-relevance matching**: when a claim mentions a specific file path, backticked token, snake_case / camelCase / `_prefixed` identifier, or `line N`, the hook requires that subject to appear in some Read/Grep/Glob/Bash input from the same turn. Reading an unrelated file no longer satisfies a claim about a different file.
- Falls back to "any evidence-tool call passes" only for purely generic claims (e.g. bare *"done."*) where no specific subject was extracted.

**What the hook still can't do:**

**1. Stop hook semantics depend on Claude Code's version.** The hook exits 2 with a stderr message; what Claude Code does with that stderr (re-prompt the model? log and ignore? show to the user?) is the platform's call, and we can't make it harder than that from our side. Treat the hook as a strong nudge, not a hard block — the skill prompt is what carries most of the weight.

**2. Subject extraction is heuristic.** It looks for things that *look like* identifiers — `foo.py`, `_cross_check_price`, backticked tokens, "line 47". Claims that name their subject in plain prose ("the auth middleware", "that test") won't have an extracted subject and will fall back to the generic rule. Adding NLP-grade entity extraction is out of scope.

**3. Relevance match is substring-based.** If your tool input mentions the subject at all, the hook accepts it. A Read of the right file followed by a confident lie about line numbers will still pass. The hook can prove the agent *touched* the relevant file; it can't prove what the agent *concluded* was correct.

**4. Multi-turn drift is still on the human.** The original incident was *"scanned three times, missed the same content three times"* — each turn individually looked fine. This hook fires per-turn and can't reason across turns. If you want cross-turn checking, that's a separate tool.

If the defaults are too noisy or too quiet for your project, the trigger list, intent-marker list, and identifier regex are all in [`.claude/hooks/prove-done-check.py`](./.claude/hooks/prove-done-check.py) — fork and tune.

---

## Origin

Built after a real session where the agent claimed an item was logged to a pending file (it wasn't — only partial), then on a follow-up scan claimed a clause was missing — when it sat on lines 171–173 of the file it had just read. Two consecutive lookups, two wrong answers, both confidently delivered from memory. The fix is mechanical: re-read every time, cite every time, and have a hook that notices when you didn't.

## License

MIT
