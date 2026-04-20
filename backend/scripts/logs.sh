#!/usr/bin/env bash
# =============================================================================
#  logs.sh — Pretty log viewer with service selection and JSON formatting
# =============================================================================
#  Usage: ./scripts/logs.sh [service] [--level LEVEL] [--last N] [--json]
#
#  Examples:
#    ./scripts/logs.sh                          # all app services, last 50 lines
#    ./scripts/logs.sh leaderboard_service      # leaderboard only
#    ./scripts/logs.sh auth_service --level ERROR
#    ./scripts/logs.sh --last 200 --json
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE="docker compose -f $PROJECT_DIR/docker-compose.yml"

APP_SERVICES=(auth_service level_service balance_service leaderboard_service)

SERVICE=""
LEVEL_FILTER=""
LAST=50
JSON_MODE=false

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --level)  LEVEL_FILTER="$2"; shift 2 ;;
    --last)   LAST="$2";        shift 2 ;;
    --json)   JSON_MODE=true;   shift ;;
    -*)       echo "Unknown option: $1"; exit 1 ;;
    *)        SERVICE="$1"; shift ;;
  esac
done

# Determine services to show
if [[ -n "$SERVICE" ]]; then
  SERVICES=("$SERVICE")
else
  SERVICES=("${APP_SERVICES[@]}")
fi

format_log() {
  if $JSON_MODE; then
    cat  # pass through raw JSON
  elif command -v jq &>/dev/null; then
    # Pretty-print JSON log lines, fall back to raw for non-JSON lines
    while IFS= read -r line; do
      # Strip docker-compose service prefix (e.g. "auth_service  | ...")
      content="${line#*| }"
      parsed=$(echo "$content" | jq -r '
        . as $r |
        if type == "object" then
          "\(.asctime // .timestamp // "") [\(.levelname // .level // "INFO")] \(.name // .logger // "-") — \(.message // "")"
        else
          .
        end
      ' 2>/dev/null) || parsed="$content"
      
      # Colourize by level
      if [[ "$parsed" == *"[ERROR]"* ]] || [[ "$parsed" == *"[CRITICAL]"* ]]; then
        echo -e "\033[0;31m$parsed\033[0m"
      elif [[ "$parsed" == *"[WARNING]"* ]]; then
        echo -e "\033[1;33m$parsed\033[0m"
      elif [[ "$parsed" == *"[DEBUG]"* ]]; then
        echo -e "\033[0;36m$parsed\033[0m"
      else
        echo "$parsed"
      fi
    done
  else
    cat
  fi
}

if [[ -n "$LEVEL_FILTER" ]]; then
  $COMPOSE logs -f --tail="$LAST" "${SERVICES[@]}" | grep --line-buffered "\"$LEVEL_FILTER\"" | format_log
else
  $COMPOSE logs -f --tail="$LAST" "${SERVICES[@]}" | format_log
fi
