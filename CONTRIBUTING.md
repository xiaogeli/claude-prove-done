# Contributing to claude-prove-done

Thanks for taking *memory ≠ evidence* seriously enough to want to extend it.

## The high-value PR: a new trigger pattern (or a fix for a bad one)

Most "I'm done" failures are linguistic-specific. The trigger pattern list is how this project stays useful across the ways agents actually phrase claims, and tuning it is the single most valuable contribution.

A good trigger PR has:

1. **The phrase, with one real-world example.** *"all set on the migration"*, *"that's wrapped up"*, *"已经搞定"*. Cite a transcript line, even paraphrased — patterns added on theory rot fast.
2. **Direction: add or refine.**
   - **Add** if your phrase is a real claim that the current list misses (a false negative).
   - **Refine** if the current list fires on something that *isn't* a claim (a false positive — usually fixed by extending the intent-marker list, not by removing a trigger).
3. **A test case.** Add a row to the bash test block at the bottom of `CONTRIBUTING.md` (see *Testing* below) showing the input transcript, expected exit code, and what the hook should detect. The smoke harness in the repo runs ~16 cases today; one more is cheap.
4. **The edit, in both places.** `.claude/hooks/prove-done-check.py` (the regex) **and** `.claude/skills/prove-done/SKILL.md` (the human-readable trigger list in the *Triggers* section). Keeping them in sync is the deal.

Keep the trigger list **narrow but specific**. A pattern that catches 80% of real claims with near-zero false positives beats one that catches 100% but cries wolf — agents (and users) ignore noisy hooks within a week.

## Other welcome contributions

- **New languages.** Triggers in Japanese, Korean, German, Spanish, etc., if you use Claude Code in a non-English/Chinese workflow. Same rule: cite real phrasing, not theoretical.
- **Better subject extraction.** The current `IDENT_RE` and `PATH_RE` are conservative. If your stack uses identifiers the regex misses (Erlang atoms, Lisp symbols, Kubernetes resource names), propose a regex addition with examples.
- **Ports of the skill prompt to other agents** (Cursor, Aider, Copilot, Continue). The hook is Claude-Code-specific, but the SKILL.md prompt is portable. PR a link in the README.
- **Clearer writing in `SKILL.md` or `README.md`.** The tone is deliberately direct — *"memory is not evidence"*, not *"please consider verifying"*. Keep that.

## What this project will not accept

- A trigger pattern that fires on conversational use (*"that's done deal"*, *"good fixed bug"* matched out of context) without a tight intent-marker filter to back it out. Noisy hooks die.
- Semantic verification (*"prove the agent's conclusion is correct"*). Out of scope — the hook proves the agent *touched* the right artifact, not that what they wrote about it is true. That's still on the human.
- Features that pretend the hook can enforce what it cannot. If it can't verify, the README's *Limitations* section says so, and that section stays load-bearing.
- Changes that make the skill softer or more hedging. *"You said done — show evidence"* is the voice. A skill that apologizes cannot interrupt the failure mode.

## Workflow

1. Open an issue first for anything larger than a single trigger or regex tweak.
2. Fork, branch, PR against `main`.
3. One focused change per PR. A new trigger row is its own PR; a README fix is its own PR.
4. The commit message explains *why*, not just *what*.

## Testing

The repo doesn't (yet) ship a formal test suite — the smoke harness lives in commit messages and the regression block at the bottom of recent PRs. If you change `prove-done-check.py`, run the harness from the v2 commit (`git show 98cfede`) and paste the pass/fail summary into your PR. A change that fails any of the 16 baseline cases needs explicit justification.
