# claude-prove-done

[English](README.md) · **简体中文**

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

## Demo

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

### 项目级（推荐团队使用）

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

### 个人级（所有项目）

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

### Windows (PowerShell)

```powershell
git clone https://github.com/xiaogeli/claude-prove-done.git $env:TEMP\claude-prove-done
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills","$env:USERPROFILE\.claude\hooks"
Copy-Item -Recurse "$env:TEMP\claude-prove-done\.claude\skills\prove-done" "$env:USERPROFILE\.claude\skills\"
Copy-Item "$env:TEMP\claude-prove-done\.claude\hooks\prove-done-check.*" "$env:USERPROFILE\.claude\hooks\"
# 把 $env:TEMP\claude-prove-done\.claude\settings.json 里的 hooks 块 merge 进 $env:USERPROFILE\.claude\settings.json
```

> **重要 —— 装完重启 Claude Code。** Skill 会热加载，但 **hook 只在 session 启动时注册**。重启之前完成声明**不会**被拦。验证装对了的方法：重启 → 让 Claude *"list your skills"*（应该看到 `prove-done`）→ 给一个小任务，看它会不会引用 Read/Grep 的输出而不是凭记忆断言。

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
