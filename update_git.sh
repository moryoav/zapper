#!/usr/bin/env bash
# Push everything in the current Git repo after asking for a commit message.

set -e  # exit on first error

# ── 1. Make sure we're inside a Git work-tree ────────────────────────────────
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌  Not inside a Git repository."
  exit 1
fi

# ── 2. Get commit message from the user ─────────────────────────────────────
read -rp "Commit message: " MSG
if [[ -z "$MSG" ]]; then
  echo "⚠️   Empty message; aborting."
  exit 1
fi

# ── 3. Stage, commit, and push ──────────────────────────────────────────────
git add .
git commit -m "$MSG"

# Push to the current branch (safer than hard-coding 'main')
CURRENT_BRANCH="$(git symbolic-ref --quiet --short HEAD || echo main)"
git push origin "$CURRENT_BRANCH"

echo "✅  Pushed to origin/${CURRENT_BRANCH}"
