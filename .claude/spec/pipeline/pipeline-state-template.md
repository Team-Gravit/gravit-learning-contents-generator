---
description: pipeline-state 파일의 고정 스키마(메타·ID Baseline·Checklist·로그)와 상태 기호·복구 판단 기준.
---

## pipeline-state 파일 스키마

`pipeline-workspace/pipeline-state-{YYYY-MM-DD}-{seq}.md`는 아래 고정 구조를 따른다 (**seq**는 같은 날 1부터 증가).

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
- labels:
  - {unit_id}: {YYYY-MM-DD}-{4자}
  - ...

## ID Baseline
- last_lesson_id: {n}
- last_problem_id: {n}
- last_option_id: {n}
- last_answer_id: {n}
- last_label_id: {n}

## Checklist
| unit_id | phase_2 | phase_3 | phase_4 | phase_5 | phase_6 | phase_7 |
|---------|---------|---------|---------|---------|---------|---------|
| {id}    | ⏳      | ⏳      | ⏳       | ⏳      | ⏳      | ⏳      |

## Manual Review
- {unit_id}/{problem_ref}: 재시도 3회 초과 — {마지막 감점 요약}

## Observations
| phase | unit | scope | signal | n | note |
|---|---|---|---|---|---|
| {n} | {unit_id} | {pN/lesson/-} | {signal} | {count} | {1줄 요약} |

## Log
- {ISO8601} [phase_{n}] {event}
````

---

### Observations 어휘

`## Observations`는 실행 중 발생한 **마찰 신호**(반복 감점·검증기 오류·사람 교정)를 한 행에 하나씩 구조화해 쌓는다. `assess-learning-content-quality`가 이 표를 읽어 회고에 활용한다. 사람용 타임라인인 `## Log`와 역할이 다르다(Log는 그대로 유지).

- **phase**: 신호가 관측된 phase 번호(2~7).
- **unit**: unit_id.
- **scope**: `pN`(problem_ref, p1~p6) · `lesson`(레슨 단위) · `-`(유닛·구조 단위).
- **signal**: 아래 통제 어휘 중 하나.
- **n**: 같은 항목에서 그 신호가 반복된 횟수(재시도 등). 1 이상의 정수.
- **note**: 한 줄 요약. 자유 서술은 이 칸에만 둔다.

**signal 통제 어휘**

| signal | 의미 | 출처 |
|---|---|---|
| `R1`~`R6` | 루브릭 항목 감점 | review.md |
| `AP-NN` | 안티패턴 코드 | review.md reject 사유 |
| `S1`~`S6` | 표기·용어 | review.md 자유서술 |
| `VALIDATOR:varchar` | varchar(255) 길이 초과 | 생성기 검증 FAIL |
| `VALIDATOR:structure` | 개수·타입·FK·INSERT 순서·블록·label 불일치 | 생성기 검증 FAIL |
| `VALIDATOR:idrange` | ID 연속성·중복 | 생성기 검증 FAIL |
| `VALIDATOR:quote` | 작은따옴표 짝·이스케이프 | 생성기 검증 FAIL |
| `HUMAN` | 사람이 직접 교정 | Phase 6 |

각 phase가 무엇을 기록하는지는 해당 phase 파일이 정의한다.

### 상태 기호
- ✅ 완료
- ⏳ 진행 중 / 예정
- ❌ 실패
- ⏭ 건너뜀 (전부 PASS로 Phase 5·6 생략, Manual Review 없이 Phase 6 생략 등)

### 복구 판단
- **status: COMPLETED**이면 같은 날짜로 재시작하지 말고 사용자에게 확인을 구한다.
- **current_phase**는 사람이 읽는 진행 표시용이다. 복구의 권위 있는 신호는 **Checklist**(가장 이른 ⏳/❌ phase)이며, current_phase로 재개 지점을 정하지 않는다.
