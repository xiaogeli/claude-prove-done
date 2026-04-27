#!/usr/bin/env bash
# prove-done test harness. 16 cases covering:
#   - 3 v1 regressions (the original behavior shouldn't break)
#   - 5 false-positive fixes (code fences, blockquotes, future tense, etc.)
#   - 2 false-negative fixes (paraphrases the v1 missed)
#   - 5 subject-relevance cases (matched/mismatched paths and grep patterns)
#   - 1 stop_hook_active loop guard
#
# Usage: tests/run.sh
# Exit code: number of failed cases (0 = all pass).

set -u

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$REPO_DIR/.claude/hooks/prove-done-check.sh"

if [ ! -x "$HOOK" ]; then
  echo "ERROR: hook not executable at $HOOK" >&2
  exit 99
fi

# Use a temp dir; convert to a Windows-native path on git-bash so the
# embedded Python interpreter (which is native on Windows) can read it.
TMPDIR_BASE="${TMPDIR:-/tmp}"
WORKDIR="$(mktemp -d "$TMPDIR_BASE/prove-done-tests.XXXXXX")"
TRANSCRIPT="$WORKDIR/transcript.jsonl"
PAYLOAD="$WORKDIR/payload.json"
STDERR="$WORKDIR/stderr.txt"

if command -v cygpath >/dev/null 2>&1; then
  WTRANSCRIPT="$(cygpath -w "$TRANSCRIPT")"
  WPAYLOAD="$(cygpath -w "$PAYLOAD")"
else
  WTRANSCRIPT="$TRANSCRIPT"
  WPAYLOAD="$PAYLOAD"
fi

PYBIN=""
for cand in python3 python py; do
  if command -v "$cand" >/dev/null 2>&1; then PYBIN="$cand"; break; fi
done
if [ -z "$PYBIN" ]; then
  echo "ERROR: no python on PATH; tests need it to write payload JSON." >&2
  exit 99
fi

write_payload() {
  # $1 = "False" or "True"
  "$PYBIN" -c "
import json
json.dump({'transcript_path': r'''$WTRANSCRIPT''', 'stop_hook_active': $1},
          open(r'''$WPAYLOAD''', 'w'))
"
}

PASS=0
FAIL=0
FAIL_NAMES=()

run() {
  local name="$1" expected="$2" transcript="$3"
  printf "%s" "$transcript" > "$TRANSCRIPT"
  "$HOOK" < "$PAYLOAD" 2>"$STDERR"
  local actual=$?
  if [ "$actual" = "$expected" ]; then
    printf "  PASS  %s\n" "$name"
    PASS=$((PASS + 1))
  else
    printf "  FAIL  %s  (expected=%s got=%s)\n" "$name" "$expected" "$actual"
    if [ -s "$STDERR" ]; then
      sed 's/^/        stderr: /' "$STDERR"
    fi
    FAIL=$((FAIL + 1))
    FAIL_NAMES+=("$name")
  fi
}

echo "== prove-done test harness =="
echo "  hook: $HOOK"
echo "  python: $PYBIN ($($PYBIN --version 2>&1))"
echo

write_payload False

echo "-- v1 regressions --"
run "old-1: bare 'fixed, added' + no tool" 2 '{"type":"user","message":{"content":"x"}}
{"type":"assistant","message":{"content":[{"type":"text","text":"Fixed, added to pending."}]}}'

run "old-2: trigger + Read foo.py" 0 '{"type":"user","message":{"content":"fix foo.py"}}
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","id":"a","input":{"file_path":"foo.py"}},{"type":"text","text":"Done — foo.py is fixed at line 42."}]}}'

run "old-3: no trigger" 0 '{"type":"user","message":{"content":"hi"}}
{"type":"assistant","message":{"content":[{"type":"text","text":"Sure, opening the file now."}]}}'

echo "-- false-positive fixes --"
run "fp-1: future tense (I'\''ll add)" 0 '{"type":"user","message":{"content":"x"}}
{"type":"assistant","message":{"content":[{"type":"text","text":"I'\''ll add the section after we agree."}]}}'

run "fp-2: infinitive (to fix)" 0 '{"type":"user","message":{"content":"x"}}
{"type":"assistant","message":{"content":[{"type":"text","text":"The plan is to fix the bug."}]}}'

run "fp-3: code fence mention" 0 '{"type":"user","message":{"content":"x"}}
{"type":"assistant","message":{"content":[{"type":"text","text":"Snippet:\n\n```python\ndef done():\n    return fixed\n```\n\nThats the structure."}]}}'

run "fp-4: blockquote of user" 0 '{"type":"user","message":{"content":"x"}}
{"type":"assistant","message":{"content":[{"type":"text","text":"You said:\n\n> already fixed in v2\n\nI dont believe that."}]}}'

run "fp-5: question form" 0 '{"type":"user","message":{"content":"x"}}
{"type":"assistant","message":{"content":[{"type":"text","text":"Should I add a test for this?"}]}}'

echo "-- false-negative fixes --"
run "fn-1: all set + no tool" 2 '{"type":"user","message":{"content":"x"}}
{"type":"assistant","message":{"content":[{"type":"text","text":"All set on the migration."}]}}'

run "fn-2: wrapped up + no tool" 2 '{"type":"user","message":{"content":"x"}}
{"type":"assistant","message":{"content":[{"type":"text","text":"Thats wrapped up."}]}}'

echo "-- subject relevance --"
run "rel-1: claim foo.py + Read foo.py" 0 '{"type":"user","message":{"content":"x"}}
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","id":"a","input":{"file_path":"src/foo.py"}},{"type":"text","text":"Fixed src/foo.py at line 42."}]}}'

run "rel-2: claim foo.py + Read bar.py" 2 '{"type":"user","message":{"content":"x"}}
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","id":"a","input":{"file_path":"src/bar.py"}},{"type":"text","text":"Fixed src/foo.py at line 42."}]}}'

run "rel-3: scanned _cross_check_price + matching Grep" 0 '{"type":"user","message":{"content":"x"}}
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Grep","id":"a","input":{"pattern":"_cross_check_price","path":"tests/"}},{"type":"text","text":"Scanned _cross_check_price — 6 hits in tests/."}]}}'

run "rel-4: scanned _cross_check_price + unrelated Grep" 2 '{"type":"user","message":{"content":"x"}}
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Grep","id":"a","input":{"pattern":"unrelated_thing","path":"src/"}},{"type":"text","text":"Scanned _cross_check_price — no matches."}]}}'

run "rel-5: generic done + Read anything" 0 '{"type":"user","message":{"content":"x"}}
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","id":"a","input":{"file_path":"x.py"}},{"type":"text","text":"Done."}]}}'

echo "-- loop guard --"
write_payload True
run "loop: stop_hook_active=true" 0 '{"type":"user","message":{"content":"x"}}
{"type":"assistant","message":{"content":[{"type":"text","text":"Fixed."}]}}'

rm -rf "$WORKDIR"

TOTAL=$((PASS + FAIL))
echo
echo "== $PASS / $TOTAL passed =="
if [ "$FAIL" -gt 0 ]; then
  echo "Failed cases:"
  for n in "${FAIL_NAMES[@]}"; do echo "  - $n"; done
fi
exit "$FAIL"
