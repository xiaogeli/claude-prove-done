# prove-done

A Claude Code skill that blocks "done / fixed / added / scanned" claims until they're verified with a tool call.

## The problem

Claude (and every other coding agent) regularly says things like:

- "Fixed it." — but didn't.
- "Added to the pending list." — but only added 2 of 5 items.
- "No tests for that module." — there are six, in a file you just read.
- "Already committed." — uncommitted in `git status`.

The failure mode is consistent: the model **remembers intending to do it** and reports from memory instead of from disk. Memory is not evidence. By the time the user catches it, trust is already spent.

## What this skill does

When your draft reply contains a completion claim ("done", "已修", "added", "fixed"...) or a negative-existence claim ("no tests", "X doesn't exist", "没有"...), the skill activates and requires you to:

1. **Read / Grep / Run** to verify the claim against current state.
2. **Cite the evidence inline** — file:line, grep hit count, command output.

No citation → no claim. If you can't verify, say "not yet" instead.

## Triggers

**Completion (English):** done, fixed, added, removed, deleted, updated, committed, pushed, scanned, checked, ran, tested, implemented, wired up, in place, sorted, handled.

**Completion (Chinese):** 已修 / 已加 / 已扫 / 已记 / 已删 / 已改 / 已写 / 已 commit / 已 push / 已经做了 / 已经有了 / 搞定了 / 处理好了.

**Negative existence:** "doesn't exist", "no X", "missing", "0 tests", "X 不存在", "没测试".

## Install

### Per-project (recommended for trying it out)

```bash
mkdir -p .claude/skills
git clone https://github.com/<your-fork>/prove-done.git .claude/skills/prove-done
```

### Global (all projects)

**macOS / Linux:**
```bash
mkdir -p ~/.claude/skills
git clone https://github.com/<your-fork>/prove-done.git ~/.claude/skills/prove-done
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills"
git clone https://github.com/<your-fork>/prove-done.git "$env:USERPROFILE\.claude\skills\prove-done"
```

After install, restart Claude Code. The skill auto-loads from the `skills/` directory and activates on its triggers.

## Verify it's installed

Ask Claude: *"List your available skills."* You should see `prove-done` in the list. Or just give it a small task and watch it cite a `Read` / `Grep` result instead of asserting from memory.

## Origin

Built after a real session where the agent claimed an item was logged to a pending file (it wasn't — partial), then on a follow-up scan claimed a clause was missing (it was on lines 171–173 of the file just read). Two consecutive lookups, two wrong answers from memory. The fix is mechanical: re-read every time, cite every time.

## License

MIT
