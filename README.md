# claude-prove-done

> **"Done" ≠ done.**
> *Memory is not evidence — and the agent runs on memory by default.*

A Claude Code **skill + hook** that blocks completion claims (`done`, `fixed`, `added`, `已修`, `已加`...) and negative-existence claims (`no tests for X`, `doesn't exist`, `没测试`...) until the agent has verified them with a tool call in the same turn. Pairs naturally with [`claude-think-twice`](https://github.com/xiaogeli/claude-think-twice): *think-twice* stops `--rushed` before `git push`; *prove-done* stops `--imagined` before "I'm done."

---

## The problem

The agent regularly says things like:

- *"Fixed it."* — but didn't.
- *"Added to the pending list."* — but only added 2 of 5 items.
- *"No tests for that module."* — there are six, in a file it just read.
- *"Already committed."* — `git status` shows uncommitted changes.

The failure mode is consistent: the agent **remembers intending to do it** and reports from memory instead of from disk. By the time the user catches it, trust is already spent — and "I said done and was wrong" damages the relationship more than the original missing work.

## What this project really is

Two layers, same as [`claude-think-twice`](https://github.com/xiaogeli/claude-think-twice):

**1. The skill (soft layer)** — `.claude/skills/prove-done/SKILL.md`. When the agent is about to write a completion claim, the skill instructs it to first Read / Grep / run a command, then **cite the evidence inline** (file:line, command output, hit count). No citation → no claim.

**2. The Stop hook (hard layer)** — `.claude/hooks/prove-done-check.sh`. Fires after every assistant turn. If the just-finished message contains a trigger phrase but the turn made **zero** Read/Grep/Glob/Bash tool calls, the hook exits 2 and feeds back: *"you claimed X — show your evidence."* The agent gets one shot to verify and try again. The `stop_hook_active` flag prevents infinite loops.

The skill alone is a soft constraint — the agent has to obey it. The hook is the deterministic backstop that catches the cases where it doesn't. Same reason `think-twice` ships both halves: the prompt teaches the principle, the hook enforces it when the prompt fails.

## Triggers

**Completion (English):** done, fixed, added, removed, deleted, updated, committed, pushed, scanned, checked, tested, ran, implemented, wired up, hooked up, in place, sorted, handled.

**Completion (Chinese):** 已修 / 已加 / 已扫 / 已记 / 已删 / 已改 / 已写 / 已 commit / 已 push / 已经做了 / 已经有了 / 搞定了 / 处理好了.

**Negative existence:** doesn't exist, no tests, zero tests, missing, not implemented, 不存在, 没测试, 没文档, 没有…实现.

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

## How the hook decides

For each Stop event:

1. Parse the hook payload from stdin → get `transcript_path` and `stop_hook_active`.
2. If `stop_hook_active` is true (we already fired and Claude is re-stopping), exit 0. This is the loop guard.
3. Read the transcript JSONL. Walk back to the last user message; everything after it is "this turn."
4. Concat the assistant text blocks; collect the names of all `tool_use` blocks.
5. Regex-match the text against ~30 trigger patterns (English + Chinese, completion + negative-existence).
6. If trigger matched **and** no `Read` / `Grep` / `Glob` / `Bash` tool was used this turn → exit 2 with a stderr message naming the matched triggers. Claude Code feeds stderr back to the agent, which then has a chance to verify and re-respond.
7. Otherwise exit 0.

Step 6 is intentionally lenient: **any** evidence-gathering tool call this turn passes the check. The point is to catch pure-memory claims, not to police every word.

## Why two repos, not one

`claude-think-twice` and `claude-prove-done` solve adjacent failure modes that benefit from being separately installable:

- **think-twice** intercepts **before `git push`** — agent confused fast with efficient.
- **prove-done** intercepts **before "done"** — agent confused memory with evidence.

Use both. Or just the one that hurts you most.

## Origin

Built after a real session where the agent claimed an item was logged to a pending file (it wasn't — only partial), then on a follow-up scan claimed a clause was missing — when it sat on lines 171–173 of the file it had just read. Two consecutive lookups, two wrong answers, both confidently delivered from memory. The fix is mechanical: re-read every time, cite every time, and have a hook that notices when you didn't.

## License

MIT
