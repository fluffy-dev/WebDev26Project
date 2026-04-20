#!/usr/bin/env bash
# =============================================================================
#  health-check.sh — Check health of all Typecat services
# =============================================================================
#  Can be run standalone or sourced by the typecat CLI.
#  Exit code: 0 if all services healthy, 1 if any degraded.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_URL="${TYPECAT_BASE_URL:-http://localhost:8000}"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

all_healthy=true

check_service() {
  local name="$1"
  local url="$2"

  printf "  %-25s" "$name"
  
  local response
  local http_code
  http_code=$(curl -s -o /tmp/typecat_health_resp -w "%{http_code}" --connect-timeout 3 --max-time 5 "$url" 2>/dev/null || echo "000")
  
  if [[ "$http_code" == "200" ]]; then
    local status
    status=$(python3 -c "import json,sys; d=json.load(open('/tmp/typecat_health_resp')); print(d.get('status','?'))" 2>/dev/null || echo "ok")
    local message
    message=$(python3 -c "import json,sys; d=json.load(open('/tmp/typecat_health_resp')); print(d.get('message',''))" 2>/dev/null || echo "")
    local uptime
    uptime=$(python3 -c "import json,sys; d=json.load(open('/tmp/typecat_health_resp')); print(d.get('uptime_seconds','?'))" 2>/dev/null || echo "?")
    echo -e "${GREEN}✓ $status${RESET}  (up ${uptime}s)"
    echo -e "                           ${CYAN}$message${RESET}"
  elif [[ "$http_code" == "503" ]]; then
    local message
    message=$(python3 -c "import json,sys; d=json.load(open('/tmp/typecat_health_resp')); print(d.get('message',''))" 2>/dev/null || echo "degraded")
    echo -e "${YELLOW}⚠ degraded${RESET}"
    echo -e "                           ${YELLOW}$message${RESET}"
    all_healthy=false
  else
    echo -e "${RED}✗ unreachable${RESET}  (HTTP $http_code)"
    all_healthy=false
  fi
}

check_dependency() {
  local name="$1"
  local host="$2"
  local port="$3"
  
  printf "  %-25s" "$name"
  if nc -z -w3 "$host" "$port" 2>/dev/null; then
    echo -e "${GREEN}✓ reachable${RESET}  ($host:$port)"
  else
    echo -e "${RED}✗ unreachable${RESET}  ($host:$port)"
    all_healthy=false
  fi
}

echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  Typecat Health Check                             ${RESET}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

echo -e "${BOLD}Services (via Traefik):${RESET}"
check_service "auth_service"        "$BASE_URL/auth/health"
check_service "level_service"       "$BASE_URL/level/health"
check_service "balance_service"     "$BASE_URL/balance/health"
check_service "leaderboard_service" "$BASE_URL/leaderboard/health"

echo ""
echo -e "${BOLD}Monitoring Stack:${RESET}"
check_dependency "Prometheus"       "localhost" "9090"
check_dependency "Loki"             "localhost" "3100"
check_dependency "Tempo"            "localhost" "3200"

echo ""
echo -e "${BOLD}Infrastructure:${RESET}"
check_dependency "Traefik dashboard" "localhost" "8080"

echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

if $all_healthy; then
  echo -e "  ${GREEN}${BOLD}All systems go! 🚀${RESET}"
else
  echo -e "  ${YELLOW}${BOLD}Some services need attention. ⚠️${RESET}"
fi

echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

$all_healthy

