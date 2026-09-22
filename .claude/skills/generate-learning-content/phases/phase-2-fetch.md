## Phase 2. 데이터 수집

### 목적
작업할 유닛의 개념노트를 준비하고 기존 문제 목록을 수집하며 ID Baseline을 확정한다.

### 선행 조건
Phase 1에서 작성한 **pipeline-state** 파일이 존재하며, 파일 내의 **target_units**가 확정되어 있는 상태이다.

### 참조 파일
- `.claude/spec/generation/id-management.md`

### 절차
1. **pipeline-state** 파일의 **Meta.target_units**의 각 유닛에 대해 개념노트를 준비한다. 개념노트는 `pipeline-workspace/concept-notes/{unit_id}.md`에 유닛마다 한 장씩 저장되어 있다.
   - 저장된 노트가 없는 유닛은 묻지 않고 **refresh-concept-note**를 호출해 받아온다.
   - 저장된 노트가 있던 유닛이 하나라도 있으면, 유닛별 마지막 최신화일(`date -r {파일} +%F`)을 보여주고 아래 중 선택을 받는다. (예: `개념노트를 최신화할까요? 12: 2026-09-10, 13: 2026-09-10`)
     - **아니요, 저장된 노트 사용** → 그대로 사용한다.
     - **이번 대상 유닛만 최신화** → 저장된 노트가 있던 대상 유닛으로 **refresh-concept-note**를 호출한다.
     - **전체 최신화** → **refresh-concept-note**를 **all**로 호출한다.
2. **Meta.target_units**의 각 유닛에 대해 **fetch-existing-learning-contents**를 호출하여 결과를 `pipeline-workspace/fetch-cache/{오늘 날짜}/{unit_id}/existing-problems.sql`로 작성한다 (캐시 재사용 안 함).
3. **fetch-max-id**를 호출하여 **last_lesson_id**, **last_problem_id**, **last_option_id**, **last_answer_id**, **last_label_id**를 가져온다.
4. **pipeline-state**를 업데이트한다.
   - **current_phase** → 2
   - **ID Baseline** → 단계 3 결과
   - **Checklist**의 모든 유닛의 **phase_2** → ✅
5. **Log**에 다음과 같이 작성한다.
   - `{ISO8601} [phase_2] concept notes new [{new 유닛}], changed [{changed 유닛}], unchanged {unchanged 개수}` — **refresh-concept-note**를 호출한 경우만 작성한다. 여러 번 호출했으면 결과를 합친다.
   - `{ISO8601} [phase_2] baseline fetched ({last_lesson_id}/{last_problem_id}/{last_option_id}/{last_answer_id}/{last_label_id})`

### 출력
- `pipeline-workspace/concept-notes/{unit_id}.md` (없던 유닛, 또는 최신화를 고른 경우에만 갱신)
- `pipeline-workspace/fetch-cache/{오늘 날짜}/{unit_id}/existing-problems.sql` (유닛별)

### 실패 처리
- **refresh-concept-note** 또는 **fetch-existing-learning-contents** 실패 시, 최대 3회 재시도한다. **refresh-concept-note**는 **failed**에 나온 유닛만 다시 호출한다. 만약, 3회 모두 실패하면 아래 절차대로 수행한다.
  - **pipeline-state**의 **status** 필드를 **FAILED**로 업데이트한다.
  - **Log**에 다음과 같이 작성한다.
    - `- {ISO8601} [phase_2] {refresh-concept-note/fetch-existing-learning-contents} failed with unit{실패한 유닛의 아이디}`
  - 사용자에게 보고한다.

### 다음 phase
- Phase 3
