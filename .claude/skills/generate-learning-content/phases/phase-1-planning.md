## Phase 1. 계획 수립

### 목적
작업할 유닛을 확정하고, `pipeline-state` 파일을 초기화한다.

### 선행 조건
Phase 0에서 당일 `pipeline-state`이 존재하지 않음을 판정받았으며, 사용자로부터 유닛 아이디를 전달받았다.

### 참조 파일
- `.claude/spec/pipeline-state-template.md`

### 절차
1. 스킬 호출 인자를 통해 작업할 유닛의 아이디를 확정한다. 인자가 없는 경우 사용자에게 요청한다.
2. `.claude/spec/pipeline-state-template.md` 탬플릿을 복사하여, `pipeline-workspace/pipeline-state-{오늘 날짜}.md`를 추가한다.
3. 추가한 `pipeline-state` 파일을 초기화한다.
   - `date` → {오늘 날짜}
   - `status` → IN_PROGRESS
   - `current_phase` → 1
   - `target_units` → Phase 1에서 전달 받은 유닛의 아이디
   - `ID Baseline` → Phase 2에서 확정
   - `Checklist` → 유닛 1개당 1행, 모든 컬럼 ⏳로 초기화
4. `Log` 에 다음과 같이 작성한다.
   - `- {ISO8601} [phase_1] initialized for units {작업할 유닛의 아이디들}`

### 출력
- `pipeline-workspace/pipeline-state-{오늘 날짜}.md` 생성

### 실패 처리
- 작업할 유닛의 아이디를 전달받지 못한 경우, 사용자에게 요청한 후 재개한다.

### 다음 phase
- Phase 2