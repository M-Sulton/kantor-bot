#!/bin/bash
# Contoh update status bot:
# ./update_agent.sh hermes working "Fixing production bug" desk
# ./update_agent.sh muse1 idle "Ngopi di bar pantry" coffee
# ./update_agent.sh cue idle "Berenang santai" pool

AGENT_ID="${1:-hermes}"
STATUS="${2:-working}"
TASK="${3:-Sedang memproses tugas}"
LOCATION="${4:-desk}"

curl -s -X POST "http://127.0.0.1:8010/api/update" \
  -H "Content-Type: application/json" \
  -d "{\"agent_id\":\"$AGENT_ID\",\"status\":\"$STATUS\",\"task\":\"$TASK\",\"location\":\"$LOCATION\"}"
echo ""
