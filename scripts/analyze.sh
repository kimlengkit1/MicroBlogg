#!/usr/bin/env bash
set -euo pipefail

# ---------- Config ----------
BASE="${BASE:-http://localhost:8080}"
ITER="${ITER:-10}"            # per-scenario latency samples
PARALLEL_N="${PARALLEL_N:-100}" # parallel requests for quick throughput/error-rate snapshot
CHAOS_FAIL="${CHAOS_FAIL:-0.10}"
CHAOS_DELAY_MS="${CHAOS_DELAY_MS:-100}"
CHAOS_DELAY_PCT="${CHAOS_DELAY_PCT:-0.30}"

TS="$(date +%Y%m%d_%H%M%S)"
LOG_DIR="logs"
LOG="${LOG_DIR}/analysis_${TS}.log"
mkdir -p "$LOG_DIR"

# ---------- Helpers ----------
log() {
  printf '%s %s\n' "$(date -Iseconds)" "$*" | tee -a "$LOG"
}

req_timing() {
  # usage: req_timing <url>
  # prints: ttfb=<sec> total=<sec> code=<http_code>
  local url="$1"
  curl -sS -o /dev/null -w 'ttfb=%{time_starttransfer} total=%{time_total} code=%{http_code}\n' "$url"
}

avg_from_stream() {
  # Reads "name value" lines, prints mean
  # usage: ... | avg_from_stream
  awk '{sum+=$2; n+=1} END { if (n>0) printf("%.4f", sum/n); else print "NaN" }'
}

code_dist() {
  # stdin: http codes (one per line)
  sort | uniq -c | awk '{printf "  %s x %s\n", $1, $2}'
}

need() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing dependency: $1"; exit 1; }
}

wait_http_ok() {
  # usage: wait_http_ok <url> <timeout_sec>
  local url="$1" timeout="${2:-30}"
  local start=$(date +%s)
  while true; do
    if curl -sS -o /dev/null -w '%{http_code}\n' "$url" | grep -q '^200$'; then
      return 0
    fi
    if (( $(date +%s) - start > timeout )); then
      return 1
    fi
    sleep 1
  done
}

post_json() {
  # usage: post_json <url> <json>
  curl -sS -X POST "$1" -H "Content-Type: application/json" -d "$2"
}

hr() { echo "------------------------------------------------------------" | tee -a "$LOG"; }

# ---------- Checks ----------
need docker
need curl
need jq
need awk

log "Starting analysis. BASE=$BASE"
hr

# ---------- Warm-up ----------
log "Warm up gateway and service health endpoints"
for p in /health /auth/health /users/health /posts/health /comments/health; do
  code=$(curl -sS -o /dev/null -w '%{http_code}\n' "$BASE$p" || echo "ERR")
  log "  GET $p -> $code"
done
hr

# ---------- Baseline latency (no chaos) ----------
log "Baseline latency for /posts/health (ITER=${ITER})"
TTFB_FILE=$(mktemp)
TOTAL_FILE=$(mktemp)
for i in $(seq 1 "$ITER"); do
  line=$(req_timing "$BASE/posts/health")
  ttfb=$(awk '{for(i=1;i<=NF;i++) if($i ~ /^ttfb=/){split($i,a,"="); print a[2]}}' <<<"$line")
  total=$(awk '{for(i=1;i<=NF;i++) if($i ~ /^total=/){split($i,a,"="); print a[2]}}' <<<"$line")
  code=$(awk '{for(i=1;i<=NF;i++) if($i ~ /^code=/){split($i,a,"="); print a[2]}}' <<<"$line")
  echo "$ttfb" >> "$TTFB_FILE"
  echo "$total" >> "$TOTAL_FILE"
  log "  sample#$i ttfb=${ttfb}s total=${total}s code=${code}"
done
MEAN_TTFB=$(paste -d' ' <(yes ttfb | head -n "$ITER") "$TTFB_FILE" | avg_from_stream)
MEAN_TOTAL=$(paste -d' ' <(yes total | head -n "$ITER") "$TOTAL_FILE" | avg_from_stream)
log "Baseline mean TTFB=${MEAN_TTFB}s, mean total=${MEAN_TOTAL}s"
rm -f "$TTFB_FILE" "$TOTAL_FILE"
hr

# ---------- Chaos ON ----------
log "Enable chaos on post-service: fail_rate=$CHAOS_FAIL, delay=${CHAOS_DELAY_MS}ms @${CHAOS_DELAY_PCT}"
CHAOS_CFG=$(post_json "$BASE/posts/chaos/config" \
  "{\"enabled\":true,\"fail_rate\":$CHAOS_FAIL,\"delay_ms\":$CHAOS_DELAY_MS,\"delay_pct\":$CHAOS_DELAY_PCT}")
echo "$CHAOS_CFG" | tee -a "$LOG" | jq . >/dev/null 2>&1 || true
wait_http_ok "$BASE/posts/chaos/config" 10 || true

log "Latency under chaos for /posts/health (ITER=${ITER})"
TTFB_FILE=$(mktemp)
TOTAL_FILE=$(mktemp)
for i in $(seq 1 "$ITER"); do
  line=$(req_timing "$BASE/posts/health")
  ttfb=$(awk '{for(i=1;i<=NF;i++) if($i ~ /^ttfb=/){split($i,a,"="); print a[2]}}' <<<"$line")
  total=$(awk '{for(i=1;i<=NF;i++) if($i ~ /^total=/){split($i,a,"="); print a[2]}}' <<<"$line")
  code=$(awk '{for(i=1;i<=NF;i++) if($i ~ /^code=/){split($i,a,"="); print a[2]}}' <<<"$line")
  echo "$ttfb" >> "$TTFB_FILE"
  echo "$total" >> "$TOTAL_FILE"
  log "  sample#$i ttfb=${ttfb}s total=${total}s code=${code}"
done
MEAN_TTFB_C=$(paste -d' ' <(yes ttfb | head -n "$ITER") "$TTFB_FILE" | avg_from_stream)
MEAN_TOTAL_C=$(paste -d' ' <(yes total | head -n "$ITER") "$TOTAL_FILE" | avg_from_stream)
log "Chaos mean TTFB=${MEAN_TTFB_C}s, mean total=${MEAN_TOTAL_C}s"
rm -f "$TTFB_FILE" "$TOTAL_FILE"

log "Parallel snapshot under chaos: ${PARALLEL_N} requests"
CODES=$(seq 1 "$PARALLEL_N" | xargs -P 20 -I{} sh -lc \
  "curl -sS -o /dev/null -w '%{http_code}\n' '$BASE/posts/health'") || true
echo "$CODES" | code_dist | tee -a "$LOG"
hr

# ---------- Chaos OFF ----------
log "Disable chaos on post-service"
CHAOS_CFG=$(post_json "$BASE/posts/chaos/config" \
  '{"enabled":false,"fail_rate":0,"delay_ms":0,"delay_pct":0}')
echo "$CHAOS_CFG" | tee -a "$LOG" | jq . >/dev/null 2>&1 || true
wait_http_ok "$BASE/posts/health" 15 || true
hr

# ---------- Scale out ----------
log "Scale post-service to 2 replicas"
docker compose up -d --scale post-service=2 | tee -a "$LOG"
sleep 2
docker compose ps | tee -a "$LOG"

log "Parallel snapshot after scale-out: ${PARALLEL_N} requests"
CODES=$(seq 1 "$PARALLEL_N" | xargs -P 20 -I{} sh -lc \
  "curl -sS -o /dev/null -w '%{http_code}\n' '$BASE/posts/health'") || true
echo "$CODES" | code_dist | tee -a "$LOG"
hr

# ---------- Kill one replica ----------
log "Stop one post-service replica (simulate instance failure)"
ONE_POST=$(docker ps --format '{{.ID}} {{.Names}}' | grep post-service | head -n 1 | awk '{print $1}')
if [[ -n "${ONE_POST:-}" ]]; then
  docker stop "$ONE_POST" | tee -a "$LOG"
  sleep 2
  docker ps --format '{{.ID}} {{.Names}} {{.Status}}' | grep post-service | tee -a "$LOG"
else
  log "WARN: could not identify a post-service container to stop"
fi

log "Requests still succeed via LB? ${PARALLEL_N} requests"
CODES=$(seq 1 "$PARALLEL_N" | xargs -P 20 -I{} sh -lc \
  "curl -sS -o /dev/null -w '%{http_code}\n' '$BASE/posts/health'") || true
echo "$CODES" | code_dist | tee -a "$LOG"
hr

# ---------- Dependency outage ----------
log "Stop auth-service (simulate dependency outage) and observe health propagation"
docker compose stop auth-service | tee -a "$LOG"
sleep 2
log "Check /posts/health with auth down"
curl -sS "$BASE/posts/health" | tee -a "$LOG"
log "Restart auth-service"
docker compose start auth-service | tee -a "$LOG"
wait_http_ok "$BASE/auth/health" 30 || true
wait_http_ok "$BASE/posts/health" 30 || true
hr

# ---------- Cleanup scale (optional) ----------
log "Restore post-service to single replica"
docker compose up -d --scale post-service=1 | tee -a "$LOG"
sleep 2
docker compose ps | tee -a "$LOG"
hr

# ---------- Summary ----------
log "SUMMARY:"
log "  Baseline mean ttfb=${MEAN_TTFB}s total=${MEAN_TOTAL}s"
log "  Chaos   mean ttfb=${MEAN_TTFB_C}s total=${MEAN_TOTAL_C}s"
log "  See code distributions above for error-rate and resilience checks."
log "Finished. Log written to: ${LOG}"
