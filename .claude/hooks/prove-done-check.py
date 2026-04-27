#!/usr/bin/env python3
"""
prove-done Stop hook.

Reads the just-finished assistant turn from the transcript. If it contains a
completion or negative-existence claim that is not backed by a tool call
relevant to the claim's subject, exit 2 and feed the agent a nudge to verify
with evidence.

Pipeline per turn:
  1. Concatenate assistant text blocks; collect tool_use blocks (name + input).
  2. Split text into sentences.
  3. For each sentence:
     - Build a "stripped" version (no code fences, inline code, or quote
       lines) for trigger matching — code mentions of "done"/"fixed" don't
       count as claims.
     - Skip the sentence if the trigger sits behind a future/intent marker
       ("I'll add", "to fix", "going to", "should", ...).
     - If a real claim survives, extract claim subjects from the *original*
       sentence: file paths, backticked tokens, snake_case / camelCase
       identifiers, line numbers.
  4. Decide:
     - No surviving claim       -> exit 0 (allow stop)
     - Claim has subjects + at least one subject appears in a tool's input
       (Read.file_path / Grep.pattern+path / Bash.command / Glob.pattern)
       -> exit 0 (relevant evidence found)
     - Claim has subjects but no tool input mentions any of them
       -> exit 2 (specific claim, no relevant verification)
     - Claim is generic (no extracted subjects) and zero Read/Grep/Glob/Bash
       calls happened this turn
       -> exit 2 (generic claim, zero effort)
     - Claim is generic but at least one evidence-tool call happened
       -> exit 0 (we can't verify relevance; give the benefit of the doubt)

Loop guard: if `stop_hook_active` is true in the payload, exit 0
unconditionally so we don't trap the agent in a Stop loop.
"""

from __future__ import annotations

import json
import os
import re
import sys


# Trigger patterns. English with \b word boundaries. Patterns are matched
# against the *stripped* sentence (no code fences / inline code / blockquotes).
TRIGGER_PATTERNS = [
    # --- English: completion ---
    r"\bdone\b",
    r"\bfixed\b",
    r"\b(added|removed|deleted|updated|patched|reverted|moved|renamed|merged|applied|shipped)\b",
    r"\b(committed|pushed)\b",
    r"\b(scanned|checked|tested|ran|verified)\b",
    r"\b(implemented|wired\s+up|hooked\s+up|set\s+up|sorted|handled|taken\s+care\s+of)\b",
    r"\b(in\s+place|all\s+set|good\s+to\s+go|wrapped\s+up|ready\s+to\s+go)\b",
    r"\b(it'?s|that'?s|now)\s+(done|fixed|ready|complete|working)\b",
    # --- English: negative existence ---
    r"\bdoesn'?t\s+exist\b",
    r"\bdo(?:es)?\s+not\s+exist\b",
    r"\bno\s+(?:tests?|docs?|documentation|coverage|implementation)\b",
    r"\bzero\s+tests?\b",
    r"\b0\s+tests?\b",
    r"\bnot\s+implemented\b",
    r"\bisn'?t\s+(?:implemented|tested|covered|there)\b",
]


# Skip a trigger if any of these markers appear within ~25 chars BEFORE it.
# Captures future tense, intent, hypothetical, questions — not actual claims.
FUTURE_OR_INTENT = re.compile(
    r"(?:"
    r"i'?ll\s+|"
    r"i\s+(?:will|would|could|might|may|should|plan\s+to|want\s+to|need\s+to|"
    r"intend\s+to|am\s+going\s+to|'?m\s+going\s+to)\s+|"
    r"let\s+me\s+|"
    r"going\s+to\s+|"
    r"about\s+to\s+|"
    r"plan\s+to\s+|"
    r"want\s+to\s+|"
    r"need\s+to\s+|"
    r"to\s+|"
    r"should\s+|would\s+|could\s+|might\s+|may\s+|"
    r"how\s+(?:do|to)\s+(?:i|you|we)\s+|"
    r"(?:can|do|did|would|could|should|will)\s+(?:i|you|we|it|this|that)\s+|"
    r"if\s+(?:i|you|we|it|this|that)\s+"
    r")$",
    re.IGNORECASE,
)


# File extensions worth treating as a claim subject when they appear in text.
_EXT = (
    r"py|js|ts|tsx|jsx|mjs|cjs|md|json|jsonl|yml|yaml|toml|ini|cfg|sh|bash|"
    r"zsh|fish|ps1|go|rs|java|kt|swift|c|cc|cpp|cxx|h|hpp|hxx|html|htm|css|"
    r"scss|sass|sql|rb|php|lua|r|jl|tex|txt|csv|tsv|xml|svg|proto|graphql"
)
PATH_RE = re.compile(rf"(?:[\w./\\-]+[/\\])?[\w.-]+\.(?:{_EXT})\b")
BACKTICK_RE = re.compile(r"`([^`\n]{2,80})`")
# snake_case (must contain underscore) or camelCase (lowercase then UpperCase)
IDENT_RE = re.compile(
    r"(?<!\w)("
    r"_*[a-z][a-z0-9]*(?:_[a-z0-9]+)+|"   # snake_case, possibly _-prefixed
    r"_*[a-z][a-z0-9]*[A-Z][a-zA-Z0-9]+"  # camelCase, possibly _-prefixed
    r")(?!\w)"
)
LINE_REF_RE = re.compile(r"\bline\s+(\d+(?:\s*[-–]\s*\d+)?)\b", re.IGNORECASE)

EVIDENCE_TOOLS = {"Read", "Grep", "Glob", "Bash"}


def strip_block_constructs(text: str) -> str:
    """Strip fenced code blocks and blockquote lines from the WHOLE text.

    Fenced blocks must be stripped before sentence splitting because their
    opener and closer often land in different sentences. Blockquotes are
    line-scoped, also pre-split.
    """
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"^\s*>.*$", "", text, flags=re.MULTILINE)
    return text


def strip_inline_code(text: str) -> str:
    """Strip inline `code` from a single sentence for trigger matching only.
    The original sentence is still used for subject extraction so backticked
    tokens remain available as subjects.
    """
    return re.sub(r"`[^`\n]+`", " ", text)


def split_sentences(text: str) -> list[str]:
    """Cheap sentence split on standard English punctuation and newlines."""
    parts = re.split(r"(?:[.!?;]+\s+|\n+|(?<=[.!?])$)", text)
    return [p.strip() for p in parts if p and p.strip()]


def has_intent_marker_before(stripped_sent: str, match_start: int) -> bool:
    """Look at up to 30 chars before the trigger for a future/intent marker."""
    window = stripped_sent[max(0, match_start - 30): match_start]
    return bool(FUTURE_OR_INTENT.search(window))


def find_real_triggers(stripped_sent: str) -> list[str]:
    """Return matched trigger strings that survive the intent-marker filter."""
    hits: list[str] = []
    for pat in TRIGGER_PATTERNS:
        for m in re.finditer(pat, stripped_sent, re.IGNORECASE):
            if has_intent_marker_before(stripped_sent, m.start()):
                continue
            hits.append(m.group(0))
            break  # one hit per pattern is enough
    return hits


def extract_subjects(original_sent: str) -> set[str]:
    """Extract identifiers/paths from the original (unstripped) sentence."""
    subjects: set[str] = set()
    for m in PATH_RE.finditer(original_sent):
        subjects.add(m.group(0))
    for m in BACKTICK_RE.finditer(original_sent):
        token = m.group(1).strip()
        # split on whitespace — backticked phrase may contain a path + args
        for piece in re.split(r"\s+", token):
            if len(piece) >= 2 and not piece.isdigit():
                subjects.add(piece)
    for m in IDENT_RE.finditer(original_sent):
        subjects.add(m.group(0))
    for m in LINE_REF_RE.finditer(original_sent):
        subjects.add(f"line {m.group(1)}")
    # Filter out trivial / extremely common tokens
    trivial = {
        "true", "false", "none", "null", "self", "this", "that", "they",
        "i_ll", "we_ll", "you_ll",
    }
    return {s for s in subjects if s.lower() not in trivial and len(s) >= 3}


def collect_tool_haystack(tool_uses: list[dict]) -> str:
    """Concat every input string value across this turn's tool_use blocks."""
    parts: list[str] = []
    for tu in tool_uses:
        inp = tu.get("input")
        if not isinstance(inp, dict):
            continue
        for v in inp.values():
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, (list, tuple)):
                parts.extend(str(x) for x in v)
    return "\n".join(parts)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    if payload.get("stop_hook_active"):
        return 0

    transcript_path = payload.get("transcript_path")
    if not transcript_path or not os.path.exists(transcript_path):
        return 0

    with open(transcript_path, "r", encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]

    last_user_idx = -1
    for i in range(len(entries) - 1, -1, -1):
        if entries[i].get("type") == "user":
            last_user_idx = i
            break

    text_parts: list[str] = []
    tool_uses: list[dict] = []
    for entry in entries[last_user_idx + 1:]:
        if entry.get("type") != "assistant":
            continue
        content = entry.get("message", {}).get("content", [])
        if isinstance(content, str):
            text_parts.append(content)
            continue
        for block in content:
            btype = block.get("type")
            if btype == "text":
                text_parts.append(block.get("text", ""))
            elif btype == "tool_use":
                tool_uses.append(block)

    full_text = "\n".join(text_parts)
    if not full_text.strip():
        return 0

    block_stripped = strip_block_constructs(full_text)
    sentences = split_sentences(block_stripped)
    surviving_hits: list[str] = []
    subjects: set[str] = set()

    for sent in sentences:
        for_triggers = strip_inline_code(sent)
        if not for_triggers.strip():
            continue
        hits = find_real_triggers(for_triggers)
        if not hits:
            continue
        surviving_hits.extend(hits)
        subjects |= extract_subjects(sent)

    if not surviving_hits:
        return 0

    tool_names = {tu.get("name", "") for tu in tool_uses}
    has_evidence_tool = bool(tool_names & EVIDENCE_TOOLS)
    haystack = collect_tool_haystack(tool_uses).lower()

    if subjects:
        # Specific claim — require at least one subject to appear in tool inputs.
        matched_subjects = [s for s in subjects if s.lower() in haystack]
        if matched_subjects:
            return 0
        unique_hits = ", ".join(sorted(set(surviving_hits))[:4])
        unique_subjects = ", ".join(sorted(subjects)[:5])
        print(
            f"prove-done: this turn claims completion/non-existence "
            f"({unique_hits}) about specific subjects ({unique_subjects}), "
            f"but no Read/Grep/Glob/Bash call this turn referenced any of "
            f"them. Open the file or grep the symbol so the claim has actual "
            f"evidence behind it, then cite file:line or hit count. If you "
            f"can't verify, say 'not yet' instead.",
            file=sys.stderr,
        )
        return 2

    # Generic claim (no specific subject extracted) — fall back to old rule.
    if has_evidence_tool:
        return 0
    unique_hits = ", ".join(sorted(set(surviving_hits))[:4])
    print(
        f"prove-done: your reply contains completion/existence claims "
        f"({unique_hits}) but this turn made no Read/Grep/Glob/Bash call to "
        f"verify them. Re-read the file or grep the symbol, then cite "
        f"evidence (file:line, command output, or hit count) before claiming "
        f"it's done. If you can't verify, say 'not yet' instead.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
