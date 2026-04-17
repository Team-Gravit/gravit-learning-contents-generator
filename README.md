### 📌 목적

**Gravit** 서비스의 학습 컨텐츠 품질과 운영 효율성을 높이기 위해, CS **문제**(Problem), **정답**(Answer), **선지**(Option) 생성 파이프라인을 자동화하는 인프라를 구축한다.

**Claude Code**의 **Subagent**, **Skill**, **Hook** 등을 활용하여, 실제 사람이 수행했던 **문제 생성**, **검수**, **DB 저장** 워크플로우를 자동화한다.

**파이프라인의 상태 추적**(pipeline-state), **정량 기반 검수 루브릭**, **피드백 루프**, **compaction 복구 프로토콜** 등을 도입하여, Claude Code의 Subagent, Skill, Hook, Rule이 유기적으로 연결되는 **하네스 엔지니어링 기반 아키텍처를 지향**한다.

---

### 📌 Agent 구성

**👩🏻‍💻 총괄(메인 세션)**

**역할**
- 파이프라인의 상태를 추적, 관리한다. 에이전트들의 진행도, 재시도 횟수 등을 `pipeline-state-{날짜}.md`파일로 관리한다.
- 콘텐츠 생성에 필요한 **개념노트**, **기존 문제**(중복 방지)를 가져와 `콘텐츠 생성 에이전트`에 분배한다.
- `콘텐츠 생성 에이전트`가 만든 콘텐츠를 `콘텐츠 검수 에이전트`에게 전달하고, 그 결과를 통해 **재시도 여부(1문제당 최대 3회)를 결정**한다.
- 재시도 3회 초과분(`manual-review`)은 **사용자와 대화로 해소**한다.
- 최종 산출물(`lesson.sql`)을 운영 DB의 `_staging` 테이블에 적재한다.
- **compaction** 또는 세션 교체 시 `pipeline-state-{날짜}.md`를 읽어 중단된 단계부터 재개한다. 재개 시 `fetch-max-id`로 ID Baseline만 재조회하고 fetch-cache는 재사용한다.

---

**작업**

- `fetch-cs-note` 스킬로 작업 유닛들의 **개념노트**를 가져온다.
- `fetch-existing-learning-contents` 스킬로 작업 유닛들의 **기존 문제 목록**을 가져온다.
- 위 작업의 결과를 유닛별로 할당된 `콘텐츠 생성 에이전트`에게 분배한다.
- 생성 결과물을 유닛별로 할당된 `콘텐츠 검수 에이전트`에게 분배한다.
- 검수 결과를 종합하여 수정이 필요한 부분에 대해 **재생성을 지시**한다.
- 미해소 항목은 사용자와 대화로 수정안을 합의한 뒤 `lesson.sql`에 반영한다.
- 모든 작업 완료 시, `.env`의 `DATABASE_URL`로 `psql` 실행하여 `_staging` 테이블에 적재한다.

---

**pipeline-state (`pipeline-state-{YYYY-MM-DD}.md`)**

상태 파일의 고정 스키마는 `.claude/spec/pipeline-state-template.md`를 참조한다. Phase 1에서 skill이 템플릿을 복사해 초기화하고, 이후 phase에서 in-place로 갱신한다.

필드 요약:
- `Meta` — target_units, max_retry_per_problem
- `ID Baseline` — lesson/problem/option/answer의 MAX ID (Phase 2마다 재조회, 캐시 금지)
- `Checklist` — 유닛 × phase 격자 (✅/⏳/❌/⏭)
- `Manual Review` — 재시도 3회 초과 문제
- `Log` — 타임스탬프 기반 이력

<br>

**🧑🏻‍💻 콘텐츠 생성 에이전트**

**역할**

> 여러 유닛의 콘텐츠를 생성할 경우, `총괄`이 유닛별로 **독립된 콘텐츠 생성 에이전트를 병렬로 호출**한다.

`총괄`로부터 개념 노트, 기존 문제 목록을 전달받아 **학습 콘텐츠를 생성**한다.

---

**작업**

- 전달받은 데이터 기반으로 학습 콘텐츠(문제, 정답, 선지)를 생성
- 각 문제에 대해 **발문**(instruction), **본문**(content), **정답**(Answer), **해설**(explanation), **선지**(Option)를 **SQL**에 맞춰 출력
- 스킬 호출 1회 = lesson 1개 = OBJECTIVE 4문제 + SUBJECTIVE 2문제
- 부분 재생성 요청 시 해당 문제만 새로 생성하여 동일 형식으로 반환

---

**콘텐츠 생성 기준**

- 핵심 개념 목록이 커버하는 범위의 문제
- 기존 문제 목록과 최대한 겹치지 않는 6개의 문제(객관식 4문제, 주관식 2문제, 문제의 중복 일부 허용)

<br>

**🧑🏻‍💻 콘텐츠 검수 에이전트**

**역할**

> 여러 유닛의 콘텐츠를 검수할 경우, `총괄`이 유닛별로 **독립된 콘텐츠 검수 에이전트를 병렬로 호출**한다.

`총괄`로부터 `콘텐츠 생성 에이전트`의 출력을 전달받아 **학습 콘텐츠를 검수**한다.

---

**작업**

- 각 문제를 직접 풀어본다.(정답을 참조하지 않고, 발문과 본문으로만 풀이한다.)
- 풀이 결과와 제시된 정답을 대조하여 정답 정확성을 검증한다.
- `검수 루브릭`에 따라 항목별 1~5점 채점 후 **PASS**/**REJECT**을 결정한다.

---

**검수 루브릭 (요약)**

| 항목 | 코드 | 적용 대상 |
| --- | --- | --- |
| 정답 정확성 | R1 | 문제(객/주) |
| 선지 변별력 | R2 | 문제(객) |
| 난이도 적절성 | R3 | 문제(객/주) |
| 발문-본문 정합성 | R4 | 문제(객/주) |
| 해설 충실도 | R5 | 문제(객/주) |
| 난이도 균형 | R6 | 레슨 |

**판정 요약**

- 문제: PASS = R1 ≥ 4 AND 적용 항목 평균 ≥ 3.5 AND 최솟값 ≥ 3. 하나라도 어기면 REJECT.
- 레슨: PASS = R6 ≥ 3. REJECT 시 기존 문제 보존 + 난이도만 조정.
- 문제·레슨 모두 재시도 최대 3회, 초과 시 `manual-review` 태깅.

채점 척도(정수 1~5), 각 항목 세부 기준, 출력 스키마, R1 판정 프로토콜은 [`.claude/spec/review-rubric.md`](.claude/spec/review-rubric.md) 참조.

---

### 📌 Skill 구성

**⚒️ generate-learning-content**

Phase 0~7의 절차 지향 오케스트레이션을 통해 복구 → 계획 → 데이터 수집 → 생성 → 검수 → 피드백 루프 → manual-review → staging 적재까지 파이프라인 전체를 실행하는 진입점 스킬이다.

<br>

**⚒️ fetch-cs-note**

유닛의 식별자를 받아 유닛의 개념노트를 가져온다.

<br>

**⚒️ fetch-existing-learning-contents**

특정 유닛의 학습 컨텐츠 목록을 조회한다. 유닛의 식별자로 하위 레슨을 조회한 뒤, 레슨별 학습 컨텐츠를 가져온다.

<br>

**⚒️ fetch-max-id**

lesson / problem / option / answer 테이블의 MAX ID를 조회한다. Phase 2에서 ID Baseline 확정 시, Phase 0 복구 시에 호출된다.

---

### 📌 Hook 구성

**🔗 learning-content-formatter**

SQL 컬럼 구성, 문제 수/선지 수/정답 개수 등 구조적 유효성 검증 (fail-closed)

<br>

**🔗 sql-validator**

INSERT 쿼리의 문법, 무결성 검증

<br>

**🔗 typo-checker**

CS 도메인 맥락을 고려한 오탈자/문법 검출

<br>

**🔗 notify-complete**

작업 완료시 Webhook 알림

> 현재 4개 훅은 스텁 상태다. 상위 3개(formatter / validator / typo-checker)는 모델 판단이 필요한 단계라 skill 절차 또는 reviewer 에이전트로 흡수할지 논의 중이다. `notify-complete`만은 Stop 이벤트 훅으로 유지.

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
    │   ├─ /fetch-existing-learning-contents → existing-problems.md
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
│   │   │   └── SKILL.md
│   │   └── fetch-existing-learning-contents/
│   │       └── SKILL.md
│   ├── hooks/
│   │   ├── learning-content-formatter.sh      ← PreToolUse: JSON/SQL 구조·count 검증
│   │   ├── sql-validator.sh                   ← PreToolUse: INSERT 쿼리 무결성
│   │   ├── typo-checker                       ← PostToolUse: CS 도메인 오탈자 검출
│   │   └── notify-complete.sh                 ← Stop: Webhook 알림
│   ├── spec/                                  ← SoT spec 문서 (skill/agent가 필요 시점에 Read)
│   │   ├── learning-content-rules.md          ← 콘텐츠 구성 규칙
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
    │   └── existing-problems.md               ← Phase 2: fetch-existing-learning-contents 산출물
    ├── generation-output/{YYYY-MM-DD}/{unit_id}/
    │   └── lesson.sql                         ← Phase 3/5/6: generator + manual-review 최종 SQL
    └── review-output/{YYYY-MM-DD}/{unit_id}/
        └── review.md                          ← Phase 4/5: reviewer 채점 결과
```