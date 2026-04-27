# Summary

<One-sentence description of the change.>

# Why

<What "I'm done" failure or false fire does this address? Cite the phrase or transcript line. Link to the issue if there is one.>

# Checklist

- [ ] If this changes the trigger list, both `.claude/hooks/prove-done-check.py` (`TRIGGER_PATTERNS`) and the *Triggers* section in `.claude/skills/prove-done/SKILL.md` are updated.
- [ ] If this adds a new pattern, it has at least one cited real-world phrasing (not invented).
- [ ] The 16 baseline test cases still pass (run the harness from the v2 commit; paste the summary).
- [ ] Commit messages explain the why, not just the what.
- [ ] Tone matches the project: direct, no hedging.
