### 📌 목적

**Gravit** 서비스의 학습 콘텐츠 품질과 운영 효율성을 높이기 위해, CS **문제**(Problem), **정답**(Answer), **선지**(Option) 생성 파이프라인을 자동화하는 인프라를 구축한다.

**Claude Code**의 **Subagent**, **Skill**, **Hook** 등을 활용해, 이전까지 사람이 반복 수행하던 **문제 생성 → 검수 → DB 적재** 워크플로우를 1회의 스킬 호출(`/generate-learning-content`)로 끝까지 실행한다.

**파이프라인의 상태 추적**(pipeline-state), **정량 기반 검수 루브릭**, **피드백 루프**, **compaction 복구 프로토콜** 등을 도입해, Claude Code의 Subagent, Skill, Hook, Rule이 유기적으로 맞물려 돌아가는 **하네스 엔지니어링(Harness engineering) 기반 아키텍처**를 지향한다.

---

### 📌 설계 원칙

"LLM을 한 번 잘 호출한다"가 아니라, "LLM이 포함된 파이프라인이 수백 유닛에 걸쳐 일관된 품질로 돌아가게 만든다"를 목표로 **하네스 엔지니어링**을 지향했다. 

프롬프트에 의존하는 대신 **파이프라인의 뼈대(절차, 스펙, 상태, 검증)를 코드와 파일 바깥 인프라로 분리**하는 방향으로 설계했다.

- **Skill이 절차를 소유한다.** 
  - 8-phase 오케스트레이션은 `generate-learning-content` 스킬에 있고, phase별 runbook은 필요 시점에만 Read된다. 메인 세션의 컨텍스트는 얇게 유지된다.


- **Spec은 SoT 문서로 분리한다.**
  - 콘텐츠 규칙 · SQL 스키마 · 검수 루브릭 · writing-style 등 모든 규범은 `.claude/spec/` 하위 개별 문서에 있고, 스펙 한 곳을 고치면 generator · reviewer가 동일 기준으로 재동작한다.


- **서브에이전트는 context fork로 격리·병렬화한다.**
  - 유닛 간 교차 오염이 없고, reviewer는 read-only로 정답을 직접 풀어본 뒤 채점한다.


- **검수는 정량 루브릭 + 피드백 루프로 고정한다.**
  - R1~R6 정수 채점 → PASS/REJECT → 문제당 최대 3회 재생성 → 초과분 `manual-review` 태깅으로 사용자와 합의.


- **상태는 파일 하나에 지속(persist)한다.**
  - `pipeline-state-{YYYY-MM-DD}.md` 고정 스키마로 세션 compaction · 재시작에도 미완료 phase부터 재개 가능.


- **중간 산출물을 디스크로 고정한다.**
  - concept-note · lesson.sql · review.md 모두 날짜·유닛별 디렉토리에 남고, 서브에이전트 간에는 텍스트가 아니라 파일 경로가 오간다.


- **스키마 검증 후 staging에만 적재한다.**
  - `validate-lesson-{structure,sql}.py`로 구조·ID 연속성을 강제한 뒤 `_staging` 테이블로만 `psql --single-transaction` 적재. 운영 테이블에는 직접 쓰지 않는다.


---

### 📌 파이프라인 구조

```
[/generate-learning-content {unit_ids} 호출]
    │
    ├─ Phase 0. 복구 확인 (메인 세션)
    │   ├─ pipeline-state-{날짜}.md 없음 → Phase 1
    │   └─ 있음 → Checklist에서 미완료 가장 이른 phase를 resume_phase로 결정
    │       └─ resume_phase > 2 → fetch-max-id만 재호출해 ID Baseline 갱신
    │          (concept-note / existing-problems 캐시는 재사용)
    │
    ├─ Phase 1. 계획 수립 (메인 세션)
    │   ├─ 유닛 ID 파싱
    │   └─ pipeline-state-{날짜}.md 생성 (Meta + Checklist 초기화)
    │
    ├─ Phase 2. 데이터 수집 (메인 세션)
    │   ├─ /fetch-cs-note → concept-note.md
    │   ├─ /fetch-existing-learning-contents → existing-problems.sql
    │   ├─ fetch-max-id → ID Baseline 확정
    │   └─ pipeline-state 업데이트
    │
    ├─ Phase 3. 콘텐츠 생성 (서브에이전트 병렬, context: fork)
    │   ├─ [재실행 가드] 기존 lesson.sql 존재 시 [덮어쓰기 / 보존 후 skip] 확인
    │   ├─ [Unit A] learning-content-generator → lesson.sql (1 lesson, 6문제)
    │   ├─ [Unit B] learning-content-generator → lesson.sql
    │   └─ ...
    │
    ├─ Phase 4. 콘텐츠 검수 (서브에이전트 병렬, context: fork, read-only)
    │   ├─ [재실행 가드] 기존 review.md 존재 시 [덮어쓰기 / 보존 후 skip] 확인
    │   ├─ learning-content-reviewer → 각 문제 직접 풀이
    │   ├─ R1~R6 항목별 1~5점 채점 → PASS/REJECT 판정 → review.md
    │   ├─ 모두 PASS → ☞ Phase 7 (5·6 건너뜀)
    │   └─ 하나라도 REJECT → Phase 5
    │
    ├─ Phase 5. 피드백 루프 (문제당 최대 3회)
    │   ├─ REJECT 문제 + 감점항목 + 개선방향 → generator 재호출 → reviewer 재채점
    │   ├─ 3회 초과 시 lesson.sql에 -- manual-review 주석 태깅
    │   │                + pipeline-state의 Manual Review에 요약 기록
    │   ├─ Manual Review 항목 있음 → Phase 6
    │   └─ Manual Review 비어있음 → ☞ Phase 7 (6 건너뜀)
    │
    ├─ Phase 6. manual-review 해소 (사용자 대화)
    │   ├─ 태깅된 항목별 수정안 제시 → OK 응답 시 lesson.sql 반영
    │   └─ 모두 해소되면 Manual Review 비움
    │
    ├─ Phase 7. staging 적재
    │   ├─ .env의 DATABASE_URL 로드
    │   ├─ psql --single-transaction -f lesson.sql → _staging 테이블
    │   └─ pipeline-state 최종 상태: COMPLETED
    │
    └─ [Hook: notify-complete] Webhook 알림
```

---

### 📌 파일 디렉토리 구조

```
프로젝트 루트/
├── .claude/
│   ├── CLAUDE.md                              ← 항상 로드되는 최소 지침 (pipeline-state 경로, spec 인덱스)
│   ├── agents/
│   │   ├── learning-content-generator.md      ← 콘텐츠 생성 서브에이전트 (context: fork)
│   │   └── learning-content-reviewer.md       ← 콘텐츠 검수 서브에이전트 (context: fork, read-only)
│   ├── skills/
│   │   ├── generate-learning-content/
│   │   │   ├── SKILL.md                       ← 진입점 스킬 (Phase 0~7 오케스트레이션)
│   │   │   └── phases/                        ← phase별 절차 runbook
│   │   │       ├── phase-0-recovery.md
│   │   │       ├── phase-1-planning.md
│   │   │       ├── phase-2-fetch.md
│   │   │       ├── phase-3-generate.md
│   │   │       ├── phase-4-review.md
│   │   │       ├── phase-5-feedback-loop.md
│   │   │       ├── phase-6-manual-review.md
│   │   │       └── phase-7-staging-load.md
│   │   ├── fetch-cs-note/
│   │   │   └── SKILL.md                       ← 유닛 개념노트 조회
│   │   ├── fetch-existing-learning-contents/
│   │   │   └── SKILL.md                       ← 유닛의 기존 문제 SQL 수집 (중복 방지용)
│   │   └── fetch-max-id/
│   │       └── SKILL.md                       ← lesson/problem/option/answer MAX ID 조회
│   ├── hooks/
│   │   ├── notify-complete.sh                 ← Stop 이벤트: 완료 Webhook 알림
│   │   └── notify-permission.sh               ← Notification 이벤트: 권한 요청 알림
│   ├── scripts/
│   │   ├── validate-lesson-structure.py       ← 레슨 구조(문제 수·선지 수·정답 수) 검증
│   │   └── validate-lesson-sql.py             ← INSERT 쿼리 무결성 및 ID 연속성 검증
│   ├── spec/                                  ← SoT spec 문서 (skill/agent가 필요 시점에 Read)
│   │   ├── learning-content-rules.md          ← 콘텐츠 구성 규칙
│   │   ├── learning-content-writing-style.md  ← 한국어 표기·CS 용어·일관성 스타일 규칙
│   │   ├── learning-content-sql-schema.md     ← DB 테이블 스키마 (prod + _staging)
│   │   ├── learning-content-sql-template.md   ← INSERT 쿼리 템플릿
│   │   ├── problem-examples.md                ← generator few-shot 예시
│   │   ├── id-management.md                   ← ID 발번 규칙
│   │   ├── pipeline-state-template.md         ← pipeline-state 파일 스키마
│   │   ├── review-rubric.md                   ← 검수 루브릭 (R1~R6 채점 기준)
│   │   └── review-template.md                 ← 검수 출력 템플릿
│   └── settings.local.json
│
└── pipeline-workspace/
    ├── pipeline-state-{YYYY-MM-DD}.md         ← 파이프라인 상태 추적 파일
    ├── fetch-cache/{YYYY-MM-DD}/{unit_id}/
    │   ├── concept-note.md                    ← Phase 2: fetch-cs-note 산출물
    │   └── existing-problems.sql              ← Phase 2: fetch-existing-learning-contents 산출물
    ├── generation-output/{YYYY-MM-DD}/{unit_id}/
    │   └── lesson.sql                         ← Phase 3/5/6: generator + manual-review 최종 SQL
    ├── review-output/{YYYY-MM-DD}/{unit_id}/
    │   └── review.md                          ← Phase 4/5: reviewer 채점 결과
    └── problem-seed/                          ← 초기 시드 문제 SQL (유닛별 레퍼런스)
```