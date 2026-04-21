## pipeline-state 파일 스키마

`pipeline-workspace/pipeline-state-{YYYY-MM-DD}.md`는 아래 고정 구조를 따른다.

### 템플릿

````markdown
---
date: YYYY-MM-DD
status: IN_PROGRESS | COMPLETED | FAILED
current_phase: 0
---

## Meta
- target_units: [unit_id, ...]
- max_retry_per_problem: 3

## ID Baseline
- last_lesson_id: {n}
- last_problem_id: {n}
- last_option_id: {n}
- last_answer_id: {n}

## Checklist
| unit_id | phase_2 | phase_3 | phase_4 | phase_5 | phase_6 | phase_7 |
|---------|---------|---------|---------|---------|---------|---------|
| {id}    | ⏳      | ⏳      | ⏳       | ⏳      | ⏳      | ⏳      |

## Manual Review
- {unit_id}/{problem_ref}: 재시도 3회 초과 — {마지막 감점 요약}

## Log
- {ISO8601} [phase_{n}] {event}
````

---

### 상태 기호
- ✅ 완료
- ⏳ 진행 중 / 예정
- ❌ 실패
- ⏭ 건너뜀 (manual-review 등)

### 복구 판단
- `status: COMPLETED`이면 같은 날짜로 재시작하지 말고 사용자에게 확인을 구한다.
