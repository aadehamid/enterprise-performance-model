#!/usr/bin/env bash
# Keep Entire (https://entire.io) local to this clone. Optional: a clone without Entire never runs
# this, and its hooks (`git config core.hooksPath scripts/hooks`) work as before.
#
# Entire writes its git hooks into git's hook folder, which here is the tracked scripts/hooks, moving
# a hook already there to <hook>.pre-entire. On each agent turn it reinstalls any hook that lacks its
# marker line, "Entire CLI hooks" (entireio/cli v0.12.2, 2026-10-26, cmd/entire/cli/strategy/hooks.go:
# gitHookStateInHooksDir). Run this once after `entire enable` or `entire agent add`. It points this
# clone's hook folder at <git dir>/entire-hooks, outside the working tree, and undoes Entire's changes
# to scripts/hooks. The hooks it writes carry the marker, so Entire leaves them alone. Their pre-push
# runs scripts/hooks/pre-push first, then Entire, and gives both git's ref list: a failed check stops
# the push before Entire uploads anything, and a push that only deletes branches still skips the
# checks. Entire reads the list only when ENTIRE_PRE_PUSH_STDIN_REFS=1, which entireio/cli main
# added after v0.12.2 (hooks.go: PrePushStdinRefsEnv); v0.12.2 ignores the variable. Every Entire
# line is skipped when `entire` is not on PATH. The script also lists Entire's config files in
# .git/info/exclude, so they stay out of commits. .cursor/install.sh keeps this hook folder.
#
#   scripts/entire-local.sh           set up, or repair after Entire rewrote scripts/hooks
#   scripts/entire-local.sh --remove  go back to scripts/hooks
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
COMMON="$(cd "$(git rev-parse --git-common-dir)" && pwd)"
HOOKS="$COMMON/entire-hooks"

# Undo what Entire did to scripts/hooks without losing anything. Each file carrying Entire's marker is
# first copied to <git dir>/entire-local-saved, since you may have edited it. Then a <hook>.pre-entire
# (the file Entire moved aside, edits included) goes back in place when its hook is Entire's or
# missing; a tracked hook with no backup goes back to git's copy; an untracked one is deleted. A
# backup beside a hook that is not Entire's is left alone.
restore_tracked_hooks() {
  local f hook saved="$COMMON/entire-local-saved" stamp
  stamp="$(date +%Y%m%d-%H%M%S)-$$"
  for f in scripts/hooks/*; do
    [ -f "$f" ] && grep -q "Entire CLI hooks" "$f" || continue
    mkdir -p "$saved"
    cp "$f" "$saved/$(basename "$f").$stamp"
    echo "entire-local: saved $f to $saved/$(basename "$f").$stamp"
  done
  for f in scripts/hooks/*.pre-entire; do
    [ -f "$f" ] || continue
    hook="${f%.pre-entire}"
    if [ ! -e "$hook" ] || grep -q "Entire CLI hooks" "$hook"; then mv "$f" "$hook"; fi
  done
  for f in scripts/hooks/*; do
    [ -f "$f" ] && grep -q "Entire CLI hooks" "$f" || continue
    if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then git checkout -- "$f"; else rm "$f"; fi
  done
}

# Restore scripts/hooks before switching the hook folder, in both directions: set -e then stops the
# script with the folder unchanged if a save or restore fails, so pushes keep the hooks they had.
if [ "${1:-}" = "--remove" ]; then
  restore_tracked_hooks
  git config core.hooksPath scripts/hooks
  rm -rf "$HOOKS"
  echo "entire-local: hooks are scripts/hooks again; Entire's config files stay excluded"
  exit 0
fi

restore_tracked_hooks
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
# repo's hook passes. Entire's failure stops the push, as its own hook does. It runs a copy of
# scripts/hooks/pre-push, so what it checks is what it runs. If that copy is Entire's hook (a failed
# run of this script, or Entire writing between its steps), the push stops, since it would not run
# the checks.
hook pre-push 'repo_hook="$(git rev-parse --show-toplevel)/scripts/hooks/pre-push"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/epm-pre-push.XXXXXX")" || exit 1
trap '\''rm -rf "$tmp"'\'' EXIT
cp "$repo_hook" "$tmp/pre-push" && chmod +x "$tmp/pre-push" || exit 1
if grep -q "Entire CLI hooks" "$tmp/pre-push"; then
  echo "pre-push: $repo_hook is Entire'\''s hook, not the repo'\''s; run scripts/entire-local.sh, then push again" >&2
  exit 1
fi
cat > "$tmp/refs" || exit 1
"$tmp/pre-push" "$@" < "$tmp/refs" || exit $?
if command -v entire >/dev/null 2>&1; then
  ENTIRE_PRE_PUSH_STDIN_REFS=1 entire hooks git pre-push "$1" < "$tmp/refs" || exit $?
fi'

git config core.hooksPath "$HOOKS"

exclude="$COMMON/info/exclude"
mkdir -p "$COMMON/info"
touch "$exclude"
for path in .entire/ .claude/settings.json .codex/hooks.json .cursor/hooks.json .pi/extensions/entire/; do
  grep -qxF "$path" "$exclude" || echo "$path" >> "$exclude"
done
echo "entire-local: hooks are in $HOOKS; scripts/hooks is as tracked"
