## Phase 0. 복구 확인

### 목적
오늘 중단된 파이프라인이 있으면 그 지점부터 재개하고, 없으면 새로 시작한다.

### 선행 조건
없음

### 참조 파일
- `.claude/spec/id-management.md`

### 절차
1. `pipeline-workspace/pipeline-state-{오늘 날짜}.md` 파일이 존재하는지 확인하고, 존재하지 않는다면 즉시 Phase 1로 이동한다.
2. `pipeline-workspace/pipeline-state-{오늘 날짜}.md` 파일이 존재하면 아래 절차를 따른다.
3. `pipeline-workspace/pipeline-state-{오늘 날짜}.md` 파일을 읽고, `Checklist`에서 ⏳ 또는 ❌ 로 표기된 가장 이른 Phase 번호를 찾아 이를 `resume_phase`로 기록한다.
4. `resume_phase`가 2보다 큰 경우, Phase 전체를 되감지 않고 **ID Baseline만 갱신**한다. DB가 외부에서 바뀌었을 수 있어 캐시된 baseline은 신뢰할 수 없다.
   - `fetch-max-id`를 호출하여 `last_lesson_id`, `last_problem_id`, `last_option_id`, `last_answer_id`를 재조회한다.
   - `pipeline-state`의 `ID Baseline`을 갱신한다.
   - `Log`에 `- {ISO8601} [phase_0] id baseline refreshed on resume` 와 같이 작성한다.
   - 아래 파일은 재사용한다.
     - `pipeline-workspace/fetch-cache/{오늘 날짜}/{unit_id}/concept-note.md`
     - `pipeline-workspace/fetch-cache/{오늘 날짜}/{unit_id}/existing-problems.md`
5. `resume_phase`로 설정된 Phase로 이동한다.

### 출력
없음

### 실패 처리
없음

### 다음 phase
- `pipeline-workspace/pipeline-state-{오늘 날짜}.md` 파일이 있는 경우 → Phase `resume_phase`로 이동한다.
- `pipeline-workspace/pipeline-state-{오늘 날짜}.md` 파일이 없는 경우 → Phase 1로 이동한다.