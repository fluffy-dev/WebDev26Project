#!/usr/bin/env bash
# =============================================================================
#  metrics-dump.sh — Dump Prometheus metrics for a service
# =============================================================================
#  Usage: ./scripts/metrics-dump.sh <service> [--filter PATTERN]
#
#  Examples:
#    ./scripts/metrics-dump.sh auth_service
#    ./scripts/metrics-dump.sh leaderboard_service --filter django_http
#    ./scripts/metrics-dump.sh balance_service --filter kafka
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE="docker compose -f $PROJECT_DIR/docker-compose.yml"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

SERVICE="${1:?Usage: metrics-dump.sh <service> [--filter PATTERN]}"
FILTER=""

shift
while [[ $# -gt 0 ]]; do
  case "$1" in
    --filter) FILTER="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

echo -e "${BOLD}${CYAN}Prometheus metrics — $SERVICE${RESET}"
echo -e "${YELLOW}$(date)${RESET}"
echo ""

if [[ -n "$FILTER" ]]; then
  echo -e "${BOLD}Filter: ${FILTER}${RESET}"
  echo ""
  $COMPOSE exec -T "$SERVICE" sh -c "wget -qO- http://localhost:8000/metrics" \
    | grep -v '^#' \
    | grep "$FILTER" \
    | sort \
    | awk '{printf "  %-60s %s\n", $1, $2}'
else
  $COMPOSE exec -T "$SERVICE" sh -c "wget -qO- http://localhost:8000/metrics" \
    | grep -v '^#' \
    | sort
fi

echo ""
echo -e "${GREEN}Done.${RESET}"
