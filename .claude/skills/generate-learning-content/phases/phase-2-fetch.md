## Phase 2. 데이터 수집

### 목적
작업할 유닛의 개념노트와 기존 문제 목록을 수집하며 ID Baseline을 확정한다.

### 선행 조건
Phase 1에서 작성한 `pipeline-state` 파일이 존재하며, 파일 내의 `target_units`가 확정되어 있는 상태이다.

### 참조 파일
- `.claude/spec/id-management.md`

### 절차
1. `pipeline-state` 파일의 `Meta.target_units`의 각 유닛에 대해 **개념노트 캐시를 재사용하거나 새로 fetch**하며 아래 순서를 따른다.
   1. `pipeline-workspace/fetch-cache/{오늘 날짜}/{unit_id}/concept-note.md`가 이미 있으면 그대로 둔다. (cache hit, today)
   2. 캐시가 전혀 없으면 `fetch-cs-note`를 호출하여 `pipeline-workspace/fetch-cache/{오늘 날짜}/{unit_id}/concept-note.md`로 작성한다. (cache miss)
   - 수동 갱신이 필요할 때는 사용자가 해당 `{unit_id}/concept-note.md`(또는 `{날짜}/{unit_id}/` 전체)를 삭제하면 다음 실행에서 자동으로 새로 fetch된다.
2. `pipeline-state` 파일의 `Meta.target_units`의 각 유닛에 대해 `fetch-existing-learning-contents`를 호출하여, 그 결과를 `pipeline-workspace/fetch-cache/{오늘 날짜}/{unit_id}/existing-problems.sql`로 작성한다. (기존 문제 목록은 변경 가능성이 있으므로 캐시 재사용하지 않고 매번 새로 fetch)
3. `fetch-max-id`를 호출하여, `last_lesson_id`, `last_problem_id`, `last_option_id`, `last_answer_id`를 가져온다.
4. `pipeline-state`를 업데이트한다.
   - `current_phase` → 2
   - `ID Baseline` → 3단계에서 얻은 값으로 업데이트
   - `Checklist` 의 모든 유닛의 `phase_2` → ✅
5. `Log`에 다음과 같이 작성한다.
   - 유닛별 개념노트 캐시 상태: `{ISO8601} [phase_2] concept-note unit{unit_id} {cache hit today | cache hit {원본 날짜} | cache miss, fetched}`
   - 최종: `{ISO8601} [phase_2] baseline fetched ({last_lesson_id}/{last_problem_id}/{last_option_id}/{last_answer_id})`

### 출력
- `pipeline-workspace/fetch-cache/{오늘 날짜}/{unit_id}/concept-note.md` (유닛별)
- `pipeline-workspace/fetch-cache/{오늘 날짜}/{unit_id}/existing-problems.sql` (유닛별)

### 실패 처리
- fetch 스킬 실패 시, 최대 3회 재시도한다. 만약, 3회 모두 실패하면 아래 절차대로 수행한다.
  - `pipeline-state`의 `status` 필드를 `FAILED`로 업데이트한다.
  - `Log`에 다음과 같이 작성한다.
    - `- {ISO8601} [phase_2] {fetch-cs-note/fetch-existing-learning-contents} failed with unit{실패한 유닛의 아이디}`
  - 사용자에게 보고한다.
- 캐시 재사용은 실패 처리 대상이 아니다. 과거 캐시 파일 Read 실패 시에는 미발견으로 간주하고 `fetch-cs-note`를 호출한다.

### 다음 phase
- Phase 3
