#!/usr/bin/env bash
# 한 번의 generate-learning-content 실행이 쓴 토큰을 Claude Code 트랜스크립트에서 집계해
# pipeline-state의 "## Token Usage" 블록으로 출력한다.
#
# 사용:  token-report.sh <marker_file> <units>
#   marker_file : Phase 1에서 touch한 실행 시작 마커(이 시점 이후 종료된 서브에이전트만 집계).
#                 비었거나 없으면 세션 전체를 집계.
#   units       : 유닛 수(per_unit 산출용).
#
# 의존: $CLAUDE_CODE_SESSION_ID 환경변수, jq, macOS stat/find.
# 트랜스크립트 내부 포맷에 의존하므로(Claude Code 구현 세부), 읽기 실패 시
# "total_tokens: unavailable"을 출력하고 0으로 종료한다(파이프라인 중단 금지).
set -uo pipefail

marker="${1:-}"
units="${2:-0}"
now="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

emit_fail() {
  printf '## Token Usage\n- units: %s\n- total_tokens: unavailable (%s)\n- measured_at: %s\n' "$units" "$1" "$now"
  exit 0
}

command -v jq >/dev/null 2>&1 || emit_fail "jq 없음"
sid="${CLAUDE_CODE_SESSION_ID:-}"
[ -n "$sid" ] || emit_fail "세션 ID 없음"
D="$HOME/.claude/projects/$(pwd | sed 's#/#-#g')"
main="$D/$sid.jsonl"
subdir="$D/$sid/subagents"
[ -f "$main" ] || emit_fail "메인 트랜스크립트 없음"

# 실행 시작 epoch (마커 mtime). 마커 없으면 0 = 세션 전체.
since=0
[ -n "$marker" ] && [ -f "$marker" ] && since="$(stat -f %m "$marker" 2>/dev/null || echo 0)"

# 이 실행의 서브에이전트 파일(마커 이후 종료분)
subfiles=()
if [ -d "$subdir" ]; then
  if [ -n "$marker" ] && [ -f "$marker" ]; then
    while IFS= read -r f; do [ -n "$f" ] && subfiles+=("$f"); done \
      < <(find "$subdir" -name '*.jsonl' -newer "$marker" 2>/dev/null)
  else
    while IFS= read -r f; do [ -n "$f" ] && subfiles+=("$f"); done \
      < <(find "$subdir" -name '*.jsonl' 2>/dev/null)
  fi
fi

# usage 합산. 줄 단위 fromjson?로 진행(쓰는 중인 파일의 잘린 마지막 줄도 안전).
# main은 since로 시각 필터, 서브에이전트는 파일 단위로 이미 골랐으므로 since=0.
sum_usage() { # $1=since_epoch ; stdin=jsonl
  jq -rR --argjson since "$1" '
    fromjson?
    | select(.message.usage)
    | select($since==0 or (((.timestamp|sub("\\.[0-9]+Z$";"Z")|fromdateiso8601?)//0) >= $since))
    | .message.usage
    | [.input_tokens//0, .output_tokens//0, .cache_read_input_tokens//0, .cache_creation_input_tokens//0]
    | @tsv' 2>/dev/null \
  | awk -F'\t' '{i+=$1;o+=$2;r+=$3;c+=$4} END{printf "%d %d %d %d", i+0,o+0,r+0,c+0}'
}

read -r MI MO MR MC < <(sum_usage "$since" < "$main")
if [ "${#subfiles[@]}" -gt 0 ]; then
  read -r SI SO SR SC < <(cat "${subfiles[@]}" 2>/dev/null | sum_usage 0)
else
  SI=0; SO=0; SR=0; SC=0
fi

IN=$((MI+SI)); OUT=$((MO+SO)); CR=$((MR+SR)); CC=$((MC+SC))
TOTAL=$((IN+OUT+CR+CC))
FRESH=$((IN+CC))
PERUNIT=0
[ "$units" -gt 0 ] 2>/dev/null && PERUNIT=$((TOTAL/units))

printf '## Token Usage\n- units: %s\n- total_tokens: %s\n- per_unit: %s\n- breakdown: in=%s out=%s cache_read=%s cache_create=%s fresh=%s\n- scope: subagents(this run) + main-loop(this run window)\n- measured_at: %s\n' \
  "$units" "$TOTAL" "$PERUNIT" "$IN" "$OUT" "$CR" "$CC" "$FRESH" "$now"
