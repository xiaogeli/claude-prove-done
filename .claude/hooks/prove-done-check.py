#!/usr/bin/env python3
"""
prove-done Stop hook.

Reads the just-finished assistant turn from the transcript. If it contains a
completion/existence claim ("done", "fixed", "已修", "no tests", ...) but the
turn made zero Read/Grep/Glob/Bash tool calls, block the Stop and ask the
agent to verify with evidence before claiming.

Exits:
  0  — no trigger, or trigger backed by tool-call evidence; allow stop
  2  — trigger without evidence; stderr message is fed back to the model
"""

from __future__ import annotations

import json
import os
import re
import sys


# Loose regexes — false positives here just cost one extra verify, which is
# the whole point. Better to over-trigger than under-trigger.
TRIGGER_PATTERNS = [
    # English completion
    r"\bdone\b",
    r"\bfixed\b",
    r"\b(added|removed|deleted|updated)\b",
    r"\b(committed|pushed)\b",
    r"\b(scanned|checked|tested|ran)\b",
    r"\b(implemented|wired up|hooked up)\b",
    r"\b(in place|sorted|handled|taken care of)\b",
    # English negative existence
    r"\bdoesn't exist\b",
    r"\bdo(es)? not exist\b",
    r"\bno tests?\b",
    r"\bzero tests?\b",
    r"\b0 tests?\b",
    r"\bmissing\b",
    r"\bnot implemented\b",
    # Chinese completion (literal — no \b on CJK)
    r"已修",
    r"已加",
    r"已扫",
    r"已记",
    r"已删",
    r"已改",
    r"已写",
    r"已 ?commit",
    r"已 ?push",
    r"已经做了",
    r"已经有了",
    r"搞定了",
    r"处理好了",
    # Chinese negative existence
    r"不存在",
    r"没测试",
    r"没文档",
    r"没有.{0,8}(测试|文档|实现)",
]

EVIDENCE_TOOLS = {"Read", "Grep", "Glob", "Bash"}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    # Avoid infinite loop: if Claude Code already re-fired Stop because of us,
    # let it stop this time.
    if payload.get("stop_hook_active"):
        return 0

    transcript_path = payload.get("transcript_path")
    if not transcript_path or not os.path.exists(transcript_path):
        return 0

    with open(transcript_path, "r", encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]

    # Find the last user message — the current assistant turn is everything
    # after it.
    last_user_idx = -1
    for i in range(len(entries) - 1, -1, -1):
        if entries[i].get("type") == "user":
            last_user_idx = i
            break

    assistant_text_parts: list[str] = []
    tool_names: list[str] = []
    for entry in entries[last_user_idx + 1:]:
        if entry.get("type") != "assistant":
            continue
        content = entry.get("message", {}).get("content", [])
        if isinstance(content, str):
            assistant_text_parts.append(content)
            continue
        for block in content:
            btype = block.get("type")
            if btype == "text":
                assistant_text_parts.append(block.get("text", ""))
            elif btype == "tool_use":
                tool_names.append(block.get("name", ""))

    text = "\n".join(assistant_text_parts)
    if not text:
        return 0

    matched = []
    for pat in TRIGGER_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            matched.append(pat)
            if len(matched) >= 3:
                break

    if not matched:
        return 0

    if any(t in EVIDENCE_TOOLS for t in tool_names):
        # Some verification effort happened this turn — accept it.
        return 0

    hits = ", ".join(p.replace(r"\b", "") for p in matched)
    print(
        "prove-done: your reply contains completion/existence claims "
        f"({hits}) but this turn made no Read/Grep/Bash tool call to verify "
        "them. Re-read the file or grep the symbol, then cite evidence "
        "(file:line, command output, or hit count) before claiming it's done. "
        "If you can't verify, say 'not yet' instead.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
