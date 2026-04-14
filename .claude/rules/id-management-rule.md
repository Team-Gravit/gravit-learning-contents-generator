---
description: 학습 콘텐츠 생성 시 lesson/problem/option/answer ID 부여 규칙.
---

# ID 관리 규칙

## 원칙

Phase 2에서 `fetch-existing-learning-contents` 스킬로 현재 DB의 MAX ID를 확인하고 pipeline-state에 기록하라. ID는 별도 파일로 추적하지 않고 매 작업 시작 시 반드시 fetch하라. 파이프라인 외부에서 DB가 변경될 수 있으므로 캐시된 값을 재사용하지 마라.

## pipeline-state 기록 형식

```markdown
## ID Baseline
- last_lesson_id: 82
- last_problem_id: 532
- last_option_id: 1466
- last_answer_id: 164
```

## 부여 규칙

- 신규 ID는 baseline + 1부터 순차 부여하라
- lesson → problem → option → answer 순서로 할당하라
- 서브에이전트는 메인 세션이 전달한 ID Baseline만 사용하라. 임의로 DB를 조회하지 마라

> **집행:**
> - 캐시 금지 / 매 Phase 2 재조회 → `skills/generate-learning-content` (skill 코드가 강제)
> - ID 연속성(gap 없음) → `hooks/sql-validator.sh`
> - 서브에이전트 DB 직접 조회 금지 → `agents/learning-content-generator.md`의 `allowed_tools`에서 조회 skill 제외 (권한으로 강제)
