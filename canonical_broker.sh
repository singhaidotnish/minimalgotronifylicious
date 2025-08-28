#!/usr/bin/env bash
# canonical_broker.sh — Normalize broker naming to the canonical id: angel_one
# Safely replaces occurrences of alias names in GIT-TRACKED files only.
#
# Aliases normalized:
#   smart_connect  -> angel_one   (default)
#   smart-connect  -> angel_one   (when --all-aliases)
#   smartconnect   -> angel_one   (when --all-aliases)
#   angelone       -> angel_one   (when --all-aliases)
#
# Usage:
#   ./canonical_broker.sh                 # dry run (shows matches for smart_connect)
#   ./canonical_broker.sh apply           # apply only smart_connect -> angel_one
#   ./canonical_broker.sh --all-aliases   # dry run for all aliases
#   ./canonical_broker.sh apply --all-aliases    # apply all alias mappings
#
# Notes:
# - Works only inside a git repository (safer).
# - Skips untracked/build artifacts automatically.
# - Compatible with GNU sed and BSD/macOS sed.
# - Review the diff and commit after applying.
#
# Tips:
#   git diff --name-only
#   git add -A && git commit -m "chore(broker): canonicalize broker id to 'angel_one'"
set -euo pipefail

# --- Args ---
MODE="dry"
ALL_ALIASES="false"

for arg in "$@"; do
  case "$arg" in
    apply) MODE="apply" ;;
    --all-aliases) ALL_ALIASES="true" ;;
    -h|--help)
      sed -n '1,120p' "$0"
      exit 0
      ;;
  esac
done

# --- Preconditions ---
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: not inside a git repository." >&2
  exit 1
fi

# pick sed flavor
SED_BIN="sed"
if sed --version >/dev/null 2>&1; then
  SED_FLAVOR="gnu"
else
  SED_FLAVOR="bsd"
fi

# in-place args differ across sed flavors
if [[ "$SED_FLAVOR" == "gnu" ]]; then
  SED_INPLACE=(-i)
else
  # BSD/macOS sed needs a backup suffix argument; empty means no backup file
  SED_INPLACE=(-i "")
fi

# --- Mapping ---
declare -a FROM_LIST=("smart_connect")
declare -a TO_LIST=("angel_one")

if [[ "$ALL_ALIASES" == "true" ]]; then
  FROM_LIST=("smart_connect" "smart-connect" "smartconnect" "angelone")
  TO_LIST=("angel_one"     "angel_one"     "angel_one"     "angel_one")
fi

echo "Mode         : $MODE"
echo "All aliases  : $ALL_ALIASES"
echo "Repo         : $(git rev-parse --show-toplevel)"
echo "SED flavor   : $SED_FLAVOR ($SED_BIN)"
echo "Mappings     :"
for i in "${!FROM_LIST[@]}"; do
  printf "  - '%s' -> '%s'\n" "${FROM_LIST[$i]}" "${TO_LIST[$i]}"
done
echo "----"

# function: list matches with context
list_matches () {
  local pattern="$1"
  echo "# Searching for '${pattern}' ..."
  # Show file:line:content (colorized). Non-zero exit is fine if no matches.
  git grep -n --color=always --recurse-submodules "$pattern" || true
  echo
}

# function: apply replacement across all tracked files containing the pattern
apply_replace () {
  local pattern="$1"
  local replacement="$2"
  echo "# Applying: '${pattern}' -> '${replacement}'"
  # get NUL-delimited list of files that contain the pattern
  mapfile -d '' files < <(git grep -zl --recurse-submodules "$pattern" || true)
  if (( ${#files[@]} == 0 )); then
    echo "  No files to modify."
    return
  fi
  # Escape / and & in replacement/pattern for sed
  local pat_esc repl_esc
  pat_esc=$(printf '%s' "$pattern" | sed 's/[\/&]/\\&/g')
  repl_esc=$(printf '%s' "$replacement" | sed 's/[\/&]/\\&/g')
  # Apply per file (BSD sed portability)
  for f in "${files[@]}"; do
    if [[ "$SED_FLAVOR" == "gnu" ]]; then
      sed "${SED_INPLACE[@]}" -e "s/${pat_esc}/${repl_esc}/g" "$f"
    else
      # shellcheck disable=SC2068
      sed ${SED_INPLACE[@]} -e "s/${pat_esc}/${repl_esc}/g" "$f"
    fi
    echo "  changed: $f"
  done
}

# --- Main ---
if [[ "$MODE" == "dry" ]]; then
  for i in "${!FROM_LIST[@]}"; do
    list_matches "${FROM_LIST[$i]}"
  done
  echo "Dry run complete. To apply, run: $0 apply${ALL_ALIASES:+ --all-aliases}"
  exit 0
fi

# Apply mode
for i in "${!FROM_LIST[@]}"; do
  apply_replace "${FROM_LIST[$i]}" "${TO_LIST[$i]}"
done

echo "----"
echo "Replacement done."
echo "Changed files (per git):"
git diff --name-only --diff-filter=M || true
echo
echo "Next:"
echo "  git add -A && git commit -m \"chore(broker): canonicalize broker id to 'angel_one'\""
