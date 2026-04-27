#!/usr/bin/env bash
# claude-prove-done installer.
#
# One-liner usage (no clone needed):
#   curl -fsSL https://raw.githubusercontent.com/xiaogeli/claude-prove-done/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/xiaogeli/claude-prove-done/main/install.sh | bash -s -- --project
#
# Or run from a local clone:
#   ./install.sh
#   ./install.sh --project
#
# Flags:
#   --personal       install to $HOME/.claude (default; affects every project)
#   --project        install to ./.claude (commit alongside the current repo)
#   --target <dir>   install into <dir>/.claude (override; useful for testing)
#   -h, --help       show this help and exit
#
# What it does:
#   1. Clone the repo to a temp dir.
#   2. Copy .claude/skills/prove-done/ and the two .claude/hooks/prove-done-check.* files
#      into <claude-dir>/skills/ and <claude-dir>/hooks/.
#   3. Merge the Stop-hook entry from .claude/settings.json into <claude-dir>/settings.json.
#      Existing hooks are preserved; duplicate entries are not added.
#   4. Print a reminder to restart Claude Code so the hook registers.
#
# Requires: bash, git, python (3 preferred; python or py also fine).

set -euo pipefail

REPO_URL="https://github.com/xiaogeli/claude-prove-done.git"
SKILL_NAME="prove-done"
HOOK_FILES=("prove-done-check.sh" "prove-done-check.py")

SCOPE="personal"
TARGET=""

usage() {
  sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --personal) SCOPE="personal"; shift ;;
    --project)  SCOPE="project";  shift ;;
    --target)
      [ $# -ge 2 ] || { echo "--target needs a directory" >&2; exit 1; }
      TARGET="$2"; shift 2 ;;
    -h|--help)  usage 0 ;;
    *) echo "unknown flag: $1" >&2; usage 1 ;;
  esac
done

if [ -n "$TARGET" ]; then
  CLAUDE_DIR="$TARGET/.claude"
elif [ "$SCOPE" = "personal" ]; then
  CLAUDE_DIR="$HOME/.claude"
else
  CLAUDE_DIR="$PWD/.claude"
fi

# Pick a Python interpreter for JSON-merging settings.json.
PY=""
for cand in python3 python py; do
  if command -v "$cand" >/dev/null 2>&1; then PY="$cand"; break; fi
done
if [ -z "$PY" ]; then
  echo "ERROR: install.sh needs python (3 preferred) on PATH to merge settings.json." >&2
  echo "       Install Python 3, then re-run." >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git is required to download the skill." >&2
  exit 1
fi

echo "claude-prove-done installer"
echo "  scope:        $SCOPE"
echo "  install dir:  $CLAUDE_DIR"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git clone --depth 1 --quiet "$REPO_URL" "$TMP/repo"

mkdir -p "$CLAUDE_DIR/skills" "$CLAUDE_DIR/hooks"

# Copy skill folder.
SKILL_SRC="$TMP/repo/.claude/skills/$SKILL_NAME"
SKILL_DST="$CLAUDE_DIR/skills/$SKILL_NAME"
cp -r "$SKILL_SRC" "$CLAUDE_DIR/skills/"
echo "  skill:        $SKILL_DST"

# Copy hook files.
for f in "${HOOK_FILES[@]}"; do
  cp "$TMP/repo/.claude/hooks/$f" "$CLAUDE_DIR/hooks/"
done
chmod +x "$CLAUDE_DIR/hooks/${HOOK_FILES[0]}"
echo "  hooks:        $CLAUDE_DIR/hooks/${HOOK_FILES[0]} (+ .py)"

# Merge hooks block into settings.json.
SETTINGS_DST="$CLAUDE_DIR/settings.json"
SETTINGS_SRC="$TMP/repo/.claude/settings.json"
HOOKS_DIR_ABS="$(cd "$CLAUDE_DIR/hooks" && pwd)"

"$PY" - "$SETTINGS_DST" "$SETTINGS_SRC" "$HOOKS_DIR_ABS" "$SCOPE" <<'PY'
import json, os, re, sys

settings_path, template_path, hooks_dir_abs, scope = sys.argv[1:5]

if os.path.exists(settings_path):
    with open(settings_path, "r", encoding="utf-8") as f:
        try:
            existing = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: {settings_path} is not valid JSON: {e}", file=sys.stderr)
            sys.exit(1)
else:
    existing = {}

with open(template_path, "r", encoding="utf-8") as f:
    template = json.load(f)

# Rewrite each hook command so it points at the actual install location.
# Project scope: keep relative (./.claude/hooks/...), portable across machines.
# Personal scope: use absolute path so $HOME/.claude/settings.json works
# regardless of which project's directory Claude Code is launched from.
def rewrite(cmd):
    m = re.match(r"^\.?/?\.claude/hooks/(.+)$", cmd)
    if not m:
        return cmd
    filename = m.group(1)
    if scope == "personal":
        return os.path.join(hooks_dir_abs, filename).replace("\\", "/")
    return f"./.claude/hooks/{filename}"

template_hooks = template.get("hooks", {})
existing_hooks = existing.setdefault("hooks", {})

added = 0
for event_name, entries in template_hooks.items():
    bucket = existing_hooks.setdefault(event_name, [])
    for entry in entries:
        for h in entry.get("hooks", []):
            if "command" in h:
                h["command"] = rewrite(h["command"])
        new_cmds = sorted(h.get("command", "") for h in entry.get("hooks", []))
        already = any(
            sorted(h.get("command", "") for h in e.get("hooks", [])) == new_cmds
            and e.get("matcher", "") == entry.get("matcher", "")
            for e in bucket
        )
        if already:
            continue
        bucket.append(entry)
        added += 1

with open(settings_path, "w", encoding="utf-8") as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)
    f.write("\n")

word = "entry" if added == 1 else "entries"
print(f"  settings.json: merged {added} hook {word} into {settings_path}")
PY

cat <<EOF

Installed. Now restart Claude Code so the Stop hook registers.

To verify:
  - Ask Claude: "list your skills" — you should see prove-done.
  - Give it a tiny task and watch it cite Read/Grep output instead of
    asserting from memory.

Uninstall: remove $CLAUDE_DIR/skills/$SKILL_NAME and the
$CLAUDE_DIR/hooks/prove-done-check.* files, then delete the
prove-done entry from $CLAUDE_DIR/settings.json's "hooks.Stop" array.
EOF
