# claude-prove-done

[English](#english) · [简体中文](#中文)

---

<a id="english"></a>

> **Memory ≠ evidence.**
> *The missing beat between "I'm done" and "you can verify."*

A Claude Code **skill + hook** that makes AI coding agents see the one mistake under every false "done": the silent belief that *remembering having intended to do it* is the same as *having actually done it*. It isn't. From inside the agent's head, the two leave the same trace — a working-memory token that reads "taken care of." From outside, on disk, they're radically different. The user pays the gap. This project does exactly one thing — in the moment before the agent writes "done" or "fixed", it makes the agent read the difference right-way-up.

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

### One-liner (recommended)

Personal scope (all your projects):

```bash
curl -fsSL https://raw.githubusercontent.com/xiaogeli/claude-prove-done/main/install.sh | bash
```

Project scope (commit `.claude/` alongside this repo so the team shares it):

```bash
curl -fsSL https://raw.githubusercontent.com/xiaogeli/claude-prove-done/main/install.sh | bash -s -- --project
```

The installer clones to a temp dir, copies the skill + hooks into `~/.claude/` (or `./.claude/` with `--project`), merges the Stop-hook entry into `settings.json` while preserving any existing hooks, and rewrites the hook command path to absolute (personal) or relative (project) so it resolves correctly. Re-running is idempotent — duplicate entries are detected and skipped. Source: [`install.sh`](./install.sh).

> **Restart Claude Code afterwards.** Skills hot-reload, but hooks register only at session start.

### Manual install (if you'd rather see every step)

<details>
<summary>Project-local (recommended for teams)</summary>

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

</details>

<details>
<summary>Personal (all your projects)</summary>

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

</details>

### Windows

The one-liner above works in **git-bash** or **WSL**. (Claude Code already requires one of those, so you have one.) PowerShell users can run the curl-pipe-bash inside git-bash, or use the manual PowerShell flow below.

<details>
<summary>Manual install via PowerShell</summary>

```powershell
git clone https://github.com/xiaogeli/claude-prove-done.git $env:TEMP\claude-prove-done
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills","$env:USERPROFILE\.claude\hooks"
Copy-Item -Recurse "$env:TEMP\claude-prove-done\.claude\skills\prove-done" "$env:USERPROFILE\.claude\skills\"
Copy-Item "$env:TEMP\claude-prove-done\.claude\hooks\prove-done-check.*" "$env:USERPROFILE\.claude\hooks\"
# Merge the hooks block from $env:TEMP\claude-prove-done\.claude\settings.json into $env:USERPROFILE\.claude\settings.json
```

</details>

After **any** install method, restart Claude Code so the hook registers. To verify: restart → ask Claude *"list your skills"* (should include `prove-done`) → give it a tiny task and watch it cite Read/Grep output instead of asserting from memory.

## Requirements

- **Python 3** on PATH (the hook prefers `python3`, falls back to `python`, then `py`). If no Python is found, the hook degrades to a no-op rather than blocking everything.
- A POSIX-ish shell (`bash`). On Windows that means git-bash or WSL — Claude Code already needs one.

## Tests

```bash
tests/run.sh
```

16 cases covering v1 regressions, false-positive fixes (code fences, blockquotes, future tense, questions), false-negative fixes (paraphrases the v1 missed), subject-relevance matched/mismatched, and the `stop_hook_active` loop guard. Exit code is the number of failures, so it drops into CI as-is. Forks should run it before changing the trigger list, the intent-marker filter, or the relevance logic.

---

## How it works

### The skill (the prompt half)

Lives at `.claude/skills/prove-done/SKILL.md`. When loaded, it teaches the agent the rule in words: *before saying done / fixed / added, run a Read or Grep that touches the thing you're claiming about, then cite the result inline (file:line, command output, hit count). If you can't verify, say "not yet" instead.* The skill also names the specific failure mode — re-claiming "done" about something you already scanned this conversation, when the working-memory token feels truthy but the file hasn't been re-examined this turn.

### The hook (the backstop half)

`.claude/hooks/prove-done-check.sh` (a thin bash launcher) → `.claude/hooks/prove-done-check.py` (the logic). Wired as a Claude Code **Stop hook** in `.claude/settings.json` — fires once per assistant turn, just before the message is finalized.

For each Stop event:

1. Parse the hook payload from stdin → get `transcript_path` and `stop_hook_active`. If `stop_hook_active` is true (we already fired and Claude is re-stopping), exit 0 — that's the loop guard.
2. Read the transcript JSONL. Walk back to the last user message; everything after it is "this turn." Concat the assistant text blocks; collect every `tool_use` block (name **and** input).
3. Strip whole-text constructs that aren't real claims: fenced code (`` ``` ``…`` ``` ``), blockquote lines (`> ...`).
4. Split into sentences, and per sentence strip inline backticks for trigger detection only — keep the original sentence around for subject extraction.
5. For each sentence, find trigger words against ~25 patterns (completion + negative-existence). Skip a trigger if a future/intent marker (`I'll`, `to fix`, `going to`, `should`, `would`, `if`, `how do I`) sits within 30 characters before it.
6. From each surviving claim sentence, extract **subjects**: file paths (`foo.py`, `src/x/y.ts`), backticked tokens, snake_case / camelCase / `_prefixed` identifiers (`_cross_check_price`), and `line N` references.
7. Decide:
   - **Specific claim, relevant evidence:** subjects exist and at least one appears as a substring in some Read/Grep/Glob/Bash input this turn → exit 0.
   - **Specific claim, no relevant evidence:** subjects exist but no tool input mentions any of them → exit 2 with a stderr that names both the matched triggers and the unmatched subjects.
   - **Generic claim, some evidence:** no subjects extracted (bare *"Done."*) but at least one Read/Grep/Glob/Bash call happened → exit 0 (lenient fallback).
   - **Generic claim, zero evidence:** no subjects, no evidence-tool call → exit 2.

The relevance check is the part that makes this hook bite. *"Any tool call passes"* is too easy to game (a Read of an unrelated file would satisfy it); *"every word must be cited"* is too noisy. The middle ground — *if you named something specific, your tool call has to have touched it* — catches the actual failure mode.

---

## Triggers

**Completion:** done, fixed, added, removed, deleted, updated, patched, reverted, moved, renamed, merged, applied, shipped, committed, pushed, scanned, checked, tested, ran, verified, implemented, wired up, hooked up, set up, sorted, handled, taken care of, in place, all set, good to go, wrapped up, ready to go, *it's/that's/now (done|fixed|ready|complete|working)*.

**Negative existence:** doesn't exist, no tests, zero tests, missing, not implemented, *isn't (implemented|tested|covered|there)*.

The full list lives in `TRIGGER_PATTERNS` in [`.claude/hooks/prove-done-check.py`](./.claude/hooks/prove-done-check.py). New phrases land via PRs that cite a real-world transcript line — see [`CONTRIBUTING.md`](./CONTRIBUTING.md).

---

## Limitations (read before installing)

Honest accounting of what the hook can and can't do, after the v2 rewrite.

**What the hook now does correctly (covered by tests):**
- Strips fenced code blocks and blockquote lines before scanning, so code mentions of `done` / `fixed` and quoted user text don't trigger.
- Strips inline backticked code per sentence — same reason.
- Skips triggers preceded by future/intent markers within ~30 chars: *"I'll add"*, *"to fix"*, *"going to"*, *"should/would/could"*, *"if"*, *"how do I"*.
- Catches paraphrases the v1 missed: *"all set"*, *"wrapped up"*, *"good to go"*, *"taken care of"*, *"isn't tested"*.
- Does **subject-relevance matching**: when a claim mentions a specific file path, backticked token, snake_case / camelCase / `_prefixed` identifier, or `line N`, the hook requires that subject to appear in some Read/Grep/Glob/Bash input from the same turn. Reading an unrelated file no longer satisfies a claim about a different file.
- Falls back to "any evidence-tool call passes" only for purely generic claims (e.g. bare *"done."*) where no specific subject was extracted.

**What the hook still can't do:**

**1. Stop hook semantics depend on Claude Code's version.** The hook exits 2 with a stderr message; what Claude Code does with that stderr (re-prompt the model? log and ignore? show to the user?) is the platform's call, and we can't make it harder than that from our side. Treat the hook as a strong nudge, not a hard block — the skill prompt is what carries most of the weight.

**2. Subject extraction is heuristic.** It looks for things that *look like* identifiers — `foo.py`, `_cross_check_price`, backticked tokens, "line 47". Claims that name their subject in plain prose ("the auth middleware", "that test") won't have an extracted subject and will fall back to the generic rule. Adding NLP-grade entity extraction is out of scope.

**3. Relevance match is substring-based.** If your tool input mentions the subject at all, the hook accepts it. A Read of the right file followed by a confident lie about line numbers will still pass. The hook can prove the agent *touched* the relevant file; it can't prove what the agent *concluded* was correct.

**4. Multi-turn drift is still on the human.** The original incident was *"scanned three times, missed the same content three times"* — each turn individually looked fine. This hook fires per-turn and can't reason across turns. If you want cross-turn checking, that's a separate tool.

If the defaults are too noisy or too quiet for your project, the trigger list, intent-marker list, and identifier regex are all in [`.claude/hooks/prove-done-check.py`](./.claude/hooks/prove-done-check.py) — fork and tune.

---

## Porting to other agents

The hook (`.claude/hooks/prove-done-check.*`) is Claude-Code-specific — it reads Claude Code's transcript JSONL and is wired through Claude Code's Stop hook event. **The skill prompt (`SKILL.md`) is portable**, and most of the failure mode this project addresses isn't Claude-Code-specific.

If you're using a different agent and want the soft layer, lift `.claude/skills/prove-done/SKILL.md` and drop it where your agent reads its system / persistent instructions:

- **Cursor** — paste into `.cursorrules` or your project rules.
- **Aider** — paste into the conventions section of your `CONVENTIONS.md` (or whatever Aider points at via `--read`).
- **Continue** — paste into `~/.continue/config.json` under `systemMessage`, or include via a custom slash command.
- **Plain Claude API / Agent SDK** — append to your system prompt.

The hard layer (the Stop hook) needs an agent-specific port: read its transcript format, identify the equivalent of Claude Code's `Stop` event (or the closest "before sending" hook the platform exposes), and adapt `prove-done-check.py`'s pipeline. PRs welcome — open an issue first to discuss the agent's hook surface.

---

## Origin

Built after a real session where the agent claimed an item was logged to a pending file (it wasn't — only partial), then on a follow-up scan claimed a clause was missing — when it sat on lines 171–173 of the file it had just read. Two consecutive lookups, two wrong answers, both confidently delivered from memory. The fix is mechanical: re-read every time, cite every time, and have a hook that notices when you didn't.

## License

MIT

---

[↑ Back to top](#claude-prove-done) · [English](#english) · [简体中文](#中文)

---

<a id="中文"></a>

> **记忆 ≠ 证据。**
> *"我做完了" 和 "你可以核对" 之间缺的那一拍。*

一个 Claude Code 的 **skill + hook**，让 AI 编码 agent 看见每一次"假完成"背后的同一个错误：把"记得自己打算做这件事"和"真的做完了"当成同一回事。它们不是。从 agent 自己头脑里看，两者留下的痕迹一样 —— 工作记忆里都写着"已处理"。从外面看，在硬盘上，两者天差地别。这个差是用户在埋单。这个项目只做一件事 —— 在 agent 准备写"done"或"fixed"那一瞬间，让它把这个差读正过来。

天然搭配 [`claude-think-twice`](https://github.com/xiaogeli/claude-think-twice)：*think-twice* 在 `git push` 前拦住 `--rushed`；*prove-done* 在 "I'm done" 前拦住 `--imagined`。

---

## 两分钟版的故事

Agent 早就知道规则：*没法证明就别说做完了。*被问到时它能把这条规则一字不差背出来。然而做完一个多步任务后：

1. 完成第 4 步（共 5 步）打算做第 5 步，但被用户对第 2 步的反馈打断。
2. 一轮之后总结：*"五项全部加进了 pending 列表。"* 实际上第 5 项没加。
3. 用户说 *"你确定？再扫一次。"*
4. Agent 重扫，命中文件，**还是**漏了那条明明在那的内容 —— 因为这时候工作记忆里写着"扫过了，没问题"，那个 token 比文件实际内容更响。
5. 用户在第三轮才抓到。Agent 第一轮少花的 20 秒，变成用户接下来 2 小时对其他所有事的不信任。

账算反了，跟 [`claude-think-twice`](https://github.com/xiaogeli/claude-think-twice) 里描述的同一种反 —— agent 在自己账上记了一笔节省（"我记得做了"），代价记到了用户账上（"我得复核你说的"）。从 agent 内部看，工作记忆 token *I'm done* 和硬盘事实 *it's done* 像同一件事。它们不是。

`claude-prove-done` 就是逼 agent 在发消息前把这两件事区分开的那一拍。

---

## 这到底是什么

不是 linter。Linter 检查代码。**这个工具检查 agent 是不是把"记得"当成了"知道"。**

失败模式不是懒或健忘 —— agent 知道规则。它运行在一个无声的信念上：*只要我的表征里写着"done"，那就是 done。*这个信念是错的，因为这个表征在 agent *打算做*某件事时会被写一次，**真的做完后**也会被写一次，从内部看没有信号能区分这两次写。只有硬盘有判别信号。所以规则是机械的：**说"done"前先读硬盘；引用你读到的内容。**

一旦 agent 在同一拍里把工作记忆 token *I'm done* 和它声称改过的那个文件读到一起，它就会自我修正。不是 hook 强迫它改，而是这两个东西不再吻合。**记忆不是证据。**这就是全部论点；其他都是周边。

---

## Demo（中文）

> **用户：** 把 `risk_manager`、`data_guardian`、`multi_agent` 加到 pending 列表。
>
> **Agent：** 编辑 `pending.md`，起草："Done — added all three to the pending list."
>
> Stop hook 触发：
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
> Agent 重读 `pending.md` → 发现 `multi_agent` 不在 —— 之前的编辑只落地了三行里的两行 → 补上 → 用引用确认："Done — `pending.md:14-16` now contains all three. Verified by re-read."

第三项如果没有这一拍，就会变成一句*"yes, all done"*，然后用户一两轮后才发现 —— 那时候用户的注意力已经从这件事上移开了。Skill 是教会 agent 做这个区分的*提示*；hook 是 skill 没生效那一轮兜底的*backstop*。

---

## 为什么不用 pre-commit / lint / git-guardrails？

都用，它们是互补的，不是替代关系。

- **pre-commit、husky、lefthook** 跑 linter 和测试。它们检查*代码*。它们不会发现 agent *说*代码修好了但其实根本没跑 linter。
- **[git-guardrails](https://github.com/mattpocock/skills/tree/main/git-guardrails-claude-code)** 拦 `git push --force`、`git reset --hard` 等破坏性命令。它检查*shell 命令里的恶意或失误*。它不检查 assistant 的自然语言输出。
- **[claude-think-twice](https://github.com/xiaogeli/claude-think-twice)** 检查 agent 在 `git push` 前是不是把**快**和**高效**搞混了。不同节拍，不同时刻。
- **claude-prove-done** 检查 agent 在 *"I'm done"* 前是不是把**记忆**和**证据**搞混了。它扫 agent 自己的输出散文里的完成声明，问这一轮里有没有 disk-touching 的工具调用真的碰过声明里的具体对象。

一句话：*git-guardrails 拦 `--force`。think-twice 拦 `--rushed`。prove-done 拦 `--imagined`。*

---

## 安装

### 一行命令（推荐）

个人级（影响你所有项目）：

```bash
curl -fsSL https://raw.githubusercontent.com/xiaogeli/claude-prove-done/main/install.sh | bash
```

项目级（把 `.claude/` 提交进当前仓库给团队共享）：

```bash
curl -fsSL https://raw.githubusercontent.com/xiaogeli/claude-prove-done/main/install.sh | bash -s -- --project
```

安装脚本会 clone 到临时目录、把 skill + hook 文件复制到 `~/.claude/`（或 `--project` 时复制到 `./.claude/`）、把 Stop hook 条目 merge 进 `settings.json`（保留你已有的所有 hook，重复的不会重复加），并根据 scope 把 hook 命令路径改写成绝对路径（个人级）或相对路径（项目级）以便在任何工作目录都能解析。重复运行是幂等的。源码：[`install.sh`](./install.sh)。

> **装完重启 Claude Code。** Skill 会热加载，hook 只在 session 启动时注册。

### 手动安装（想看每一步的话）

<details>
<summary>项目级（推荐团队使用）</summary>

把 `.claude/` 提交进仓库，团队成员共享同一个 backstop：

```bash
git clone https://github.com/xiaogeli/claude-prove-done.git /tmp/claude-prove-done
mkdir -p .claude/skills .claude/hooks
cp -r /tmp/claude-prove-done/.claude/skills/prove-done .claude/skills/
cp /tmp/claude-prove-done/.claude/hooks/prove-done-check.sh .claude/hooks/
cp /tmp/claude-prove-done/.claude/hooks/prove-done-check.py .claude/hooks/
chmod +x .claude/hooks/prove-done-check.sh
```

然后把 `/tmp/claude-prove-done/.claude/settings.json` 里的 `hooks` 块 merge 进你项目的 `.claude/settings.json`，再把 `.claude/skills/prove-done/`、两个 `.claude/hooks/prove-done-check.*`、以及更新后的 `settings.json` 一起 commit。

</details>

<details>
<summary>个人级（所有项目）</summary>

把 skill 和 hook 放到 `~/.claude/`：

```bash
git clone https://github.com/xiaogeli/claude-prove-done.git /tmp/claude-prove-done
mkdir -p ~/.claude/skills ~/.claude/hooks
cp -r /tmp/claude-prove-done/.claude/skills/prove-done ~/.claude/skills/
cp /tmp/claude-prove-done/.claude/hooks/prove-done-check.sh ~/.claude/hooks/
cp /tmp/claude-prove-done/.claude/hooks/prove-done-check.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/prove-done-check.sh
# 把 /tmp/claude-prove-done/.claude/settings.json 里的 `hooks` 块 merge 进 ~/.claude/settings.json
```

</details>

### Windows

上面的一行命令在 **git-bash** 或 **WSL** 里能直接跑（Claude Code 本身就要其中之一）。PowerShell 用户可以在 git-bash 里跑 curl 那条，或者用下面的手动 PowerShell 流程。

<details>
<summary>PowerShell 手动安装</summary>

```powershell
git clone https://github.com/xiaogeli/claude-prove-done.git $env:TEMP\claude-prove-done
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills","$env:USERPROFILE\.claude\hooks"
Copy-Item -Recurse "$env:TEMP\claude-prove-done\.claude\skills\prove-done" "$env:USERPROFILE\.claude\skills\"
Copy-Item "$env:TEMP\claude-prove-done\.claude\hooks\prove-done-check.*" "$env:USERPROFILE\.claude\hooks\"
# 把 $env:TEMP\claude-prove-done\.claude\settings.json 里的 hooks 块 merge 进 $env:USERPROFILE\.claude\settings.json
```

</details>

不管用哪种方式装，装完都要重启 Claude Code 让 hook 注册。验证：重启 → 让 Claude *"list your skills"*（应该看到 `prove-done`）→ 给一个小任务，看它会不会引用 Read/Grep 的输出而不是凭记忆断言。

## 依赖

- **Python 3** 在 PATH 上（hook 优先 `python3`，回退 `python`，再回退 `py`）。找不到 Python 时 hook 退化为 no-op，不会把所有响应都拦掉。
- POSIX 风格的 shell（`bash`）。Windows 上意味着 git-bash 或 WSL —— Claude Code 本来就需要其中之一。

## 测试

```bash
tests/run.sh
```

16 个 case，覆盖 v1 回归、误触发修复（代码块、blockquote、未来时态、问句）、漏触发修复（v1 漏掉的同义词）、subject 相关性匹配/不匹配、`stop_hook_active` 循环防护。退出码等于失败数，可以直接接 CI。Fork 后改 trigger list、intent-marker 过滤、相关性逻辑之前应该跑一下。

---

## 工作原理

### Skill（提示半边）

位于 `.claude/skills/prove-done/SKILL.md`。加载后用语言教 agent 这条规则：*说 done / fixed / added 之前，跑一个 Read 或 Grep 碰一下你声称的那个东西，然后把结果引用嵌在回复里（file:line、命令输出、命中数）。如果没法验证，就说 "not yet"。* Skill 还点名了那个具体失败模式 —— 在同一对话里就某个东西重复声称"done"，工作记忆 token 觉得真，但这一轮根本没重新检查文件。

### Hook（兜底半边）

`.claude/hooks/prove-done-check.sh`（一个薄 bash launcher）→ `.claude/hooks/prove-done-check.py`（实际逻辑）。在 `.claude/settings.json` 里以 Claude Code **Stop hook** 形式接入 —— 每次 assistant turn 收尾、消息定稿之前触发一次。

每个 Stop event：

1. 从 stdin 解析 hook payload → 取 `transcript_path` 和 `stop_hook_active`。如果 `stop_hook_active` 为 true（我们刚触发过、Claude 在重新尝试 stop），exit 0 —— 这是循环防护。
2. 读 transcript JSONL。回溯到最后一条 user message；之后的全是"这一轮"。拼接 assistant text 块；收集每一个 `tool_use` 块（name **和** input）。
3. 剥掉整段不算真声明的结构：fenced code（`` ``` ``…`` ``` ``）、blockquote 行（`> ...`）。
4. 切句子，每一句单独剥 inline backtick 用于 trigger 检测 —— 但保留原句以供 subject 抽取。
5. 每个句子里查约 25 个 trigger 模式（completion + 否定存在）。trigger 前 30 个字符内有未来/意图标记（`I'll`、`to fix`、`going to`、`should`、`would`、`if`、`how do I`）就跳过。
6. 在每个存活的声明句里抽**主体**：文件路径（`foo.py`、`src/x/y.ts`）、反引号 token、snake_case / camelCase / `_前缀`标识符（`_cross_check_price`）、`line N` 引用。
7. 决策：
   - **具体声明、相关证据**：抽到了主体且至少一个作为子串出现在这一轮某个 Read/Grep/Glob/Bash 输入里 → exit 0。
   - **具体声明、没相关证据**：抽到了主体但没有工具输入提到任何一个 → exit 2，stderr 同时列出命中的触发词和未匹配的主体。
   - **泛声明、有证据**：没抽到主体（裸 *"Done."*）但至少有一个 Read/Grep/Glob/Bash 调用 → exit 0（宽容回退）。
   - **泛声明、零证据**：没主体、没 evidence-tool 调用 → exit 2。

相关性那一步是这个 hook 真有牙的部分。*"任何工具调用就放行"*太容易绕（Read 个无关文件就够）；*"每个词都必须引用"*太吵。中间地带 —— *点名了具体东西，工具调用就得碰过它* —— 抓的是真正的失败模式。

---

## 触发词

> 触发词是 hook 实际匹配的 **英文** 字面模式 —— 中文用户也读得到提示，因为 agent 输出本身大概率是英文的，而且 hook 只配了英文。完整列表见 [`prove-done-check.py`](./.claude/hooks/prove-done-check.py) 里的 `TRIGGER_PATTERNS`。

**完成声明：** done, fixed, added, removed, deleted, updated, patched, reverted, moved, renamed, merged, applied, shipped, committed, pushed, scanned, checked, tested, ran, verified, implemented, wired up, hooked up, set up, sorted, handled, taken care of, in place, all set, good to go, wrapped up, ready to go, *it's/that's/now (done|fixed|ready|complete|working)*。

**否定存在：** doesn't exist, no tests, zero tests, missing, not implemented, *isn't (implemented|tested|covered|there)*。

新词通过 PR 加入，必须引用真实 transcript 里的句子 —— 见 [`CONTRIBUTING.md`](./CONTRIBUTING.md)。

---

## 局限性（装之前先读）

如实交代 v2 之后这个 hook 能做什么、不能做什么。

**hook 现在能做对的（有测试覆盖）：**
- 扫描前先剥掉 fenced code 块和 blockquote 行 —— 代码示例里的 `done` / `fixed`、用户引用都不会触发。
- 每句单独剥 inline 反引号 —— 同理。
- 跳过前 30 字符内有未来/意图标记的触发：*"I'll add"*、*"to fix"*、*"going to"*、*"should/would/could"*、*"if"*、*"how do I"*。
- 抓 v1 漏掉的同义词：*"all set"*、*"wrapped up"*、*"good to go"*、*"taken care of"*、*"isn't tested"*。
- 做**主体相关性匹配**：声明里点了具体文件路径、反引号 token、snake_case / camelCase / `_前缀` 标识符或 `line N` 时，hook 要求那个主体必须出现在这一轮某个 Read/Grep/Glob/Bash 输入里。读了无关文件不再算数。
- 只在纯泛化声明（裸 *"done."*，没具体主体）时回退到"任何 evidence-tool 调用都行"。

**hook 现在仍然做不到的：**

**1. Stop hook 的语义跟 Claude Code 版本走。** Hook 用 exit 2 + stderr 信号给模型，但 Claude Code 怎么处理 stderr（重 prompt？记日志忽略？给用户看？）是平台决定的，我们这边硬不到平台之上。把 hook 当作一个有力的提醒，不是硬墙 —— skill 提示才是真正承重的部分。

**2. 主体抽取是启发式的。** 它找的是*看起来像*标识符的东西 —— `foo.py`、`_cross_check_price`、反引号 token、"line 47"。声明里只用普通短语指代主体（"the auth middleware"、"that test"）就抽不到，会回退到泛规则。NLP 级的实体抽取不在范围内。

**3. 相关性匹配是字符串子串。** 工具输入只要提到主体就放行。Read 对了文件但接下来在行号上自信地撒谎 —— 还是会过。Hook 能证明 agent *碰过*相关的文件，证明不了它*得出的结论*正确。

**4. 跨轮漂移仍归人管。** 原始 incident 是 *"扫了三次都漏了同一段内容"* —— 每一轮单看都过得去。这个 hook 是 per-turn 的，没法跨轮推理。要跨轮检查那是另一个工具的事。

如果默认值在你项目里太吵或太静，trigger list、intent-marker list、identifier 正则都在 [`.claude/hooks/prove-done-check.py`](./.claude/hooks/prove-done-check.py) 里 —— fork 自己调。

---

## 移植到其他 agent

Hook（`.claude/hooks/prove-done-check.*`）是 Claude Code 特有的 —— 它读的是 Claude Code 的 transcript JSONL，接的是 Claude Code 的 Stop hook event。**Skill 提示（`SKILL.md`）是可移植的**，这个项目要解决的失败模式本身也不是 Claude Code 特有的。

如果你用别的 agent 想要软层那部分，把 `.claude/skills/prove-done/SKILL.md` 拿出来放到对方读 system / 持久化指令的位置：

- **Cursor** —— 粘到 `.cursorrules` 或你的项目规则里。
- **Aider** —— 粘到 `CONVENTIONS.md` 的约定段落（或 Aider 通过 `--read` 指向的任意文件）。
- **Continue** —— 粘到 `~/.continue/config.json` 的 `systemMessage`，或通过自定义 slash command 引入。
- **裸 Claude API / Agent SDK** —— 追加到 system prompt。

硬层（Stop hook）需要 agent-specific 移植：读它的 transcript 格式、找到平台等价的"发消息前"hook event（或最接近的），改写 `prove-done-check.py` 的 pipeline。欢迎 PR —— 先开 issue 讨论那个 agent 的 hook 表面。

---

## 起源

诞生于一次真实 session：agent 声称某一项已记到一个 pending 文件里（实际只记了部分），后续一次扫描又声称某条款"缺" —— 而它就在 agent 刚读过的文件 171–173 行。两次连续查找，两次自信的错答案，全部从记忆来。修法是机械的：每次重读、每次引用，再加一个 hook 在没引用时戳一下。

## License

MIT

---

[↑ 回到顶部](#claude-prove-done) · [English](#english) · [简体中文](#中文)
