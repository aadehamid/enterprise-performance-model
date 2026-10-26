#!/usr/bin/env bash
# Keep Entire (https://entire.io) local to this clone. Optional: a clone without Entire never runs
# this, and its hooks (`git config core.hooksPath scripts/hooks`) work as before.
#
# Entire writes its git hooks into git's hook folder, which here is the tracked scripts/hooks, and
# rewrites them there on every agent turn. Run this once after `entire enable` or `entire agent add`.
# It points this clone's hook folder at <git dir>/entire-hooks, outside the working tree, and puts
# back scripts/hooks from git. Entire leaves a hook that carries its marker line ("Entire CLI
# hooks") as it is, so the hooks written here stay. Their pre-push runs scripts/hooks/pre-push first,
# then Entire, and gives both git's ref list: a failed check stops the push before Entire uploads
# anything, and a push that only deletes branches still skips the checks. Every Entire line is
# skipped when `entire` is not on PATH. The script also lists Entire's config files in
# .git/info/exclude, so they stay out of commits.
#
#   scripts/entire-local.sh           set up, or repair after Entire rewrote scripts/hooks
#   scripts/entire-local.sh --remove  go back to scripts/hooks
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
COMMON="$(cd "$(git rev-parse --git-common-dir)" && pwd)"
HOOKS="$COMMON/entire-hooks"
ENTIRE_HOOKS=(prepare-commit-msg commit-msg post-commit post-rewrite pre-push)

# Undo what Entire did to scripts/hooks. Only files carrying its marker are touched, so an edit of
# your own to a tracked hook stays: a tracked one goes back to git's copy, an untracked one is
# deleted. <hook>.pre-entire is a tracked hook Entire moved aside.
restore_tracked_hooks() {
  local f
  for f in scripts/hooks/*; do
    [ -f "$f" ] || continue
    case "$f" in *.pre-entire) rm "$f"; continue ;; esac
    grep -q "Entire CLI hooks" "$f" || continue
    if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then git checkout -- "$f"; else rm "$f"; fi
  done
}

if [ "${1:-}" = "--remove" ]; then
  git config core.hooksPath scripts/hooks
  rm -rf "$HOOKS"
  restore_tracked_hooks
  echo "entire-local: hooks are scripts/hooks again; Entire's config files stay excluded"
  exit 0
fi

# Write the hooks and switch the hook folder before restoring scripts/hooks: Entire checks the
# hook folder on each agent turn, and would otherwise write into scripts/hooks again.
mkdir -p "$HOOKS"

hook() {
  local name="$1" body="$2"
  printf '#!/bin/sh\n# Entire CLI hooks, written by scripts/entire-local.sh (see there)\n%s\n' "$body" > "$HOOKS/$name"
  chmod +x "$HOOKS/$name"
}
# The four commit hooks run Entire the way its own hooks do, ignoring its failures.
hook prepare-commit-msg 'if command -v entire >/dev/null 2>&1; then entire hooks git prepare-commit-msg "$1" "$2" 2>/dev/null || true; fi'
hook commit-msg 'if command -v entire >/dev/null 2>&1; then entire hooks git commit-msg "$1" || true; fi'
hook post-commit 'if command -v entire >/dev/null 2>&1; then entire hooks git post-commit 2>/dev/null || true; fi'
hook post-rewrite 'if command -v entire >/dev/null 2>&1; then entire hooks git post-rewrite "$1" 2>/dev/null || true; fi'
# pre-push saves git's ref list, gives it to the repo's hook, and gives it to Entire only after the
# repo's hook passes. Entire's failure stops the push, as its own hook does.
hook pre-push 'refs="$(mktemp "${TMPDIR:-/tmp}/epm-pre-push.XXXXXX")" || exit 1
trap '\''rm -f "$refs"'\'' EXIT
cat > "$refs" || exit 1
"$(git rev-parse --show-toplevel)/scripts/hooks/pre-push" "$@" < "$refs" || exit $?
if command -v entire >/dev/null 2>&1; then
  ENTIRE_PRE_PUSH_STDIN_REFS=1 entire hooks git pre-push "$1" < "$refs" || exit $?
fi'

git config core.hooksPath "$HOOKS"
restore_tracked_hooks

exclude="$COMMON/info/exclude"
mkdir -p "$COMMON/info"
touch "$exclude"
for path in .entire/ .claude/settings.json .codex/hooks.json .cursor/hooks.json .pi/extensions/entire/; do
  grep -qxF "$path" "$exclude" || echo "$path" >> "$exclude"
done
echo "entire-local: hooks are in $HOOKS; scripts/hooks is as tracked"
