#!/usr/bin/env bash
# prove-done Stop hook entrypoint.
# Picks the best available Python and runs prove-done-check.py.

set -u

DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$DIR/prove-done-check.py"

if [ ! -f "$SCRIPT" ]; then
  echo "prove-done: hook script not found at $SCRIPT" >&2
  exit 0
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$SCRIPT"
elif command -v python >/dev/null 2>&1; then
  exec python "$SCRIPT"
elif command -v py >/dev/null 2>&1; then
  exec py "$SCRIPT"
else
  echo "prove-done: no python interpreter on PATH; hook is a no-op" >&2
  exit 0
fi
