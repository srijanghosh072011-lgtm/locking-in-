#!/usr/bin/env bash
# Cron entry point. One run = audit, mockups, replies, then send.
#
# Cron gets a near-empty environment, so anything the pipeline needs is set
# here rather than assumed from an interactive shell.
set -euo pipefail

cd "$(dirname "$0")"

# Homebrew python / pipx live here and cron's default PATH misses them.
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"

mkdir -p logs

# Keep one log per day; the send decisions are worth being able to look back at.
LOG="logs/daily-$(date +%F).log"

{
  echo "===== $(date '+%Y-%m-%d %H:%M:%S %Z') ====="
  python3 src/cli.py daily
  echo "exit: $?"
} >> "$LOG" 2>&1
