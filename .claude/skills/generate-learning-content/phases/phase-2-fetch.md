## Phase 2. 데이터 수집

### 목적
작업할 유닛의 개념노트와 기존 문제 목록을 수집하며 ID Baseline을 확정한다.

수집한 파일은 파일로 저장하여 이후 Phase에서 각 서브에이전트가 인덱스를 통해 참조하도록 한다.

### 선행 조건
Phase 1에서 작성한 `pipeline-state` 파일이 존재하며, 파일 내의 `target_units`가 확정되어 있는 상태이다.

### 참조 파일
- `.claude/spec/id-management.md` — ID Baseline 캐시 금지 / 매 Phase 2 재조회.

### 절차
1. `pipeline-state` 파일의 `Meta.target_units`의 각 유닛에 대해 `fetch-cs-note`를 호출하여, 그 결과를 `pipeline-workspace/fetch-cache/{오늘 날짜}/{unit_id}/concept-note.md`로 작성한다.
2. `pipeline-state` 파일의 `Meta.target_units`의 각 유닛에 대해 `fetch-existing-learning-contents`를 호출하여, 그 결과를 `pipeline-workspace/fetch-cache/{오늘 날짜}/{unit_id}/existing-problems.md`로 작성한다.
3. `fetch-max-id`를 호출하여, `last_lesson_id`, `last_problem_id`, `last_option_id`, `last_answer_id`를 가져온다.
4. `pipeline-state`를 업데이트한다.
   - `current_phase` → 2
   - `ID Baseline` → 3단계에서 얻은 값으로 업데이트
   - `Checklist` 의 모든 유닛의 `phase_2` → ✅
5. `Log`에 다음과 같이 작성한다.
   - `{ISO8601} [phase_2] baseline fetched ({last_lesson_id}/{last_problem_id}/{last_option_id}/{last_answer_id})`

### 출력
- `pipeline-workspace/fetch-cache/{오늘 날짜}/{unit_id}/concept-note.md` (유닛별)
- `pipeline-workspace/fetch-cache/{오늘 날짜}/{unit_id}/existing-problems.md` (유닛별)

### 실패 처리
- fetch 스킬 실패 시, 최대 3회 재시도한다. 만약, 3회 모두 실패하면 아래 절차대로 수행한다.
  - `pipeline-state`의 `status` 필드를 `FAILED`로 업데이트한다.
  - `Log`에 다음과 같이 작성한다.
    - `- {ISO8601} [phase_2] {fetch-cs-note/fetch-existing-learning-contents} failed with unit{실패한 유닛의 아이디}`
  - 사용자에게 보고한다.

### 다음 phase
- Phase 3
