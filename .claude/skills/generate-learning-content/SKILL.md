---
name: generate-learning-content
description: Gravit CS 학습 콘텐츠 생성 파이프라인 진입점. 유닛 ID를 받아 1 lesson(OBJECTIVE 4 + SUBJECTIVE 2) 생성·검수·staging 적재까지 수행. /generate-learning-content 호출 시 트리거.
allowed-tools: Read, Write, Edit, Glob, Bash, Task, Skill
---

# generate-learning-content

Gravit CS 학습 콘텐츠 1 lesson(OBJECTIVE 4 + SUBJECTIVE 2 = 6문제) 생성 파이프라인의 진입점 스킬. Phase 0부터 순차 실행한다.

## 진입 지시

1. **항상 Phase 0부터 시작한다.** `phases/phase-0-recovery.md`를 Read하고 그 파일의 절차를 따른다.
2. Phase 0이 결정한 `resume_phase`에 해당하는 phase 파일을 Read한다.
3. 각 phase 파일은 자기 phase의 입력·절차·출력·실패 처리·다음 phase를 **자체 선언**한다. 필요한 spec·template은 해당 phase 파일이 명시한다.
4. Phase 간 이동은 항상 현재 phase 파일의 "다음 phase" 섹션을 따른다.

## Phase 인덱스

| Phase | 파일 | 한 줄 요약 |
|---|---|---|
| 0 | `phases/phase-0-recovery.md` | 오늘 날짜의 pipeline-state 존재 여부 확인, 재개 지점 결정. 복구 시 ID Baseline만 재조회 |
| 1 | `phases/phase-1-planning.md` | 유닛 파싱, pipeline-state 초기화 |
| 2 | `phases/phase-2-fetch.md` | 개념노트·기존 문제 수집, ID Baseline 확정 (캐시 금지) |
| 3 | `phases/phase-3-generate.md` | 유닛별 generator 서브에이전트 병렬 호출 → 1 lesson씩 생성 |
| 4 | `phases/phase-4-review.md` | reviewer 서브에이전트로 R1~R6 채점 및 PASS/REJECT 판정 |
| 5 | `phases/phase-5-feedback-loop.md` | REJECT 재생성 루프 (문제당 최대 3회), 초과 시 manual-review |
| 6 | `phases/phase-6-manual-review.md` | manual-review 태깅 항목을 사용자와 대화로 해소 |
| 7 | `phases/phase-7-staging-load.md` | 유닛별 lesson.sql을 `_staging` 테이블에 psql로 적재 |

**분기 요약**
- Phase 4: 전부 PASS → **Phase 7** (5·6 건너뜀) / 하나라도 REJECT → Phase 5
- Phase 5: Manual Review에 항목 있음 → Phase 6 / 비어 있음 → **Phase 7** (6 건너뜀)
- Phase 6: 해소 완료 → Phase 7

## 디렉토리

- `phases/` — phase별 절차 문서 (이 파일의 "진입 지시" 참고)

> generator few-shot 예시(`problem-examples.md`)를 포함한 모든 SoT 문서는 `.claude/spec/` 아래에 있다. `learning-content-generator` 에이전트가 직접 Read한다.