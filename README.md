#### 📌목적

**Gravit** 서비스의 학습 컨텐츠 품질과 운영 효율성을 높이기 위해, CS **문제**(Problem), **정답**(Answer), **선지**(Option) 생성 파이프라인을 자동화하는 인프라를 구축한다.

**Claude Code**의 **Subagent**, **Skill**, **Hook** 등을 활용하여, 실제 사람이 수행했던 **문제 생성**, **검수**, **DB 저장** 워크플로우를 자동화한다.

#### 📌구성

**Agents**

- **`총괄(메인 세션)`**

  **역할**

    - 파이프라인의 상태를 추적, 관리한다. 에이전트들의 진행도, 재시도 횟수 등을 **`pipeline-state-{날짜}.md`**파일로 관리한다.
    - 문제 생성에 필요한 **개념노트**, **기존 문제**(중복 방지)를 가져와 **`문제 생성 에이전트`**에 분배한다.
    - **`문제 생성 에이전트`**가 만든 문제를 **`문제 검수 에이전트`**에게 전달하고, 그 결과를 통해 **재시도 여부(1문제당 최대 3회)를 결정**한다.
    - 최종 결과물을 모아 백오피스로 반환한다.
    - **compaction** 또는 세션 교체 시 **`pipeline-state-{날짜}.md`**를 읽어 중단된 단계부터 재개한다.

    ---

  **작업**

    - **`fetch-cs-note`** 스킬로 작업 유닛들의 **개념노트**를 가져온다.
    - **`fetch-existing-problems`** 스킬로 작업 유닛들의 **기존 문제 목록**을 가져온다.
    - 위 작업의 결과를 유닛별로 할당된 **`문제 생성 에이전트`**에게 분배한다.
    - 위 작업의 결과를 유닛별로 할당된 **`문제 검수 에이전트`** 에게 분배한다.
    - 검수 결과를 종합하여 수정이 필요한 부분에 대해 **재생성을 지시**한다.
    - 모든 작업 완료 시, **`build-staging-output`** 스킬로 작업물의 **JSON**과 **SQL 쿼리로 준비**한다.

    ---

  **pipeline-state(`pipeline-state-{YYYY-MM-DD}.md`)**

    ```markdown
    # Pipeline State
    
    ## Meta
    - file: pipeline-state-2026-04-14.md
    - target_units: [12 (스택과 큐), 15 (정렬), 23 (TCP/IP)]
    
    ## Plan
    - created_at: 2026-04-14T10:00:00+09:00
    - problems_per_unit: 6 (객관식 4, 주관식 2)
    - lessons_per_unit: 3
    - max_retry_per_problem: 3
    
    ## Checklist
    | unit_id | step         | status      | retry | assigned_to        | updated_at                |
    |---------|--------------|-------------|-------|--------------------|---------------------------|
    | 12      | fetch-note   | done        | -     | main               | 2026-04-14T10:01:12+09:00 |
    | 12      | generate     | done        | -     | gen:unit-12        | 2026-04-14T10:05:30+09:00 |
    | 12      | review       | done        | -     | rev:unit-12        | 2026-04-14T10:08:20+09:00 |
    | 12      | staging      | done        | -     | main               | 2026-04-14T10:09:00+09:00 |
    | 15      | generate     | done        | -     | gen:unit-15        | 2026-04-14T10:06:10+09:00 |
    | 15      | review       | rejected    | 1     | rev:unit-15        | 2026-04-14T10:09:40+09:00 |
    | 15      | regenerate   | done        | 2     | gen:unit-15        | 2026-04-14T10:12:30+09:00 |
    | 15      | re-review    | done        | 2     | rev:unit-15        | 2026-04-14T10:15:00+09:00 |
    | 23      | generate     | in-progress | -     | gen:unit-23        | 2026-04-14T10:05:00+09:00 |
    
    step: fetch-note / fetch-prob / generate / review / regenerate / re-review / staging
    status: pending / in-progress / done / rejected / failed / manual-review
    
    ## Log
    2026-04-14T10:01:12 | main        | fetch-note  | unit-12 | OK
    2026-04-14T10:05:30 | gen:unit-12 | generate    | unit-12 | OK | 6문제 생성
    2026-04-14T10:08:20 | rev:unit-12 | review      | unit-12 | OK | 6/6 PASS (avg 4.2)
    2026-04-14T10:09:40 | rev:unit-15 | review      | unit-15 | FAIL | 4/6 PASS, 2 REJECT (P-15-03: R1=2, P-15-05: R2=2)
    2026-04-14T10:12:30 | gen:unit-15 | regenerate  | unit-15 | OK | 2문제 재생성
    2026-04-14T10:15:00 | rev:unit-15 | re-review   | unit-15 | OK | 2/2 PASS (avg 4.0)
    
    Log 컬럼: timestamp | agent | action | unit_id | result(OK/FAIL) | memo(10단어 이내)
    ```


- **`문제 생성 에이전트`**

  **역할**

    <aside>

  여러 유닛의 문제를 생성할 경우, **`총괄`**이 유닛별로 **독립된 문제 생성 에이전트를 병렬로 호출**한다.

    </aside>

  **`총괄`**로부터 개념 노트, 기존 문제 목록을 전달받아 **문제를 생성**한다.
    
  ---

  **작업**

    - 전달받은 데이터 기반으로 문제를 생성
    - 각 문제에 대해 **발문**(instruction), **본문**(content), **정답**(Answer), **해설**(explanation), **선지**(Option)를 **SQL**에 맞춰 출력
    - 부분 재생성 요청 시 해당 문제만 새로 생성하여 동일 형식으로 반환

    ---

  **문제 생성 기준**

    - 핵심 개념 목록이 커버하는 범위의 문제
    - 기존 문제 목록과 최대한 겹치지 않는 6개의 문제(객관식 4문제, 주관식 2문제, 문제의 중복 일부 허용)

- **`문제 검수 에이전트`**

  **역할**

    <aside>

  여러 유닛의 문제를 검수할 경우, **`총괄`**이 유닛별로 **독립된 문제 검수 에이전트를 병렬로 호출**한다.

    </aside>

  **`총괄`**로부터 **`문제 생성 에이전트`**의 출력을 전달받아 **문제를 검수**한다.
    
  ---

  **작업**

    - 각 문제를 직접 풀어본다.(정답을 참조하지 않고, 발문과 본문으로만 풀이한다.)
    - 풀이 결과와 제시된 정답을 대조하여 정답 정확성을 검증한다.
    - **`검수 루브릭`**에 따라 항목별 1~5점 채점 후 **PASS**/**REJECT**을 결정한다.

    ---

  **검수 루브릭**

  | 항목 | 코드 | 적용 대상 | 설명 |
      | --- | --- | --- | --- |
  | **정답 정확성** | R1 | 객관식/주관식 | 리뷰어가 직접 풀어본 결과와 제시된 정답 일치 여부 |
  | **선지 변별력** | R2 | 객관식만 | 오답 선지의 그럴듯함 + 정답 선지의 유일성 |
  | **난이도 적절성** | R3 | 객관식/주관식 | 타겟층(CS 배경 취준생/학부생) 수준 적합도 |
  | **발문-본문 정합성** | R4 | 객관식/주관식 | 발문이 묻는 바와 본문 맥락의 자연스러움 |
  | **해설 충실도** | R5 | 객관식/주관식 | 정답 근거 + 오답 이유 설명의 학습 효과 |
    
  ---

  **채점 기준**

    ```
    R1. 정답 정확성
      5: 풀이 결과와 제시된 정답 완전 일치, 해설 논리도 정확
      4: 정답 일치, 해설에 사소한 표현 부정확 (오개념 아님)
      3: 정답 일치, 해설 논리에 빈약한 부분 존재
      2: 정답이 모호하거나 특정 해석에서만 성립
      1: 정답이 명백히 오류
    
    R2. 선지 변별력 (객관식만)
      5: 오답 선지 모두 그럴듯하되 명확한 오개념 기반, 정답이 유일
      4: 대부분 적절, 1개가 너무 쉽게 소거됨
      3: 2개 이상이 명백히 틀려 소거법으로 쉽게 풀림
      2: 복수정답 가능 선지 존재
      1: 선지 구성 무의미 또는 정답 선지 오류
    
    R3. 난이도 적절성
      5: 개념 이해 + 약간의 응용 필요, 타겟층에 최적
      4: 적절하나 약간 쉽거나 어려움
      3: 단순 암기로 풀리거나 상위 10%만 풀 수 있는 수준
      2: 지나치게 쉬움(정의만) 또는 지나치게 어려움(대학원 수준)
      1: 타겟층과 완전 불일치
    
    R4. 발문-본문 정합성
      5: 발문과 본문이 완벽히 일치, 자연스러운 문장
      4: 정합하나 사소한 어색함 (조사, 어미 등)
      3: 이해 가능하나 연결이 느슨
      2: 발문이 모호하여 의도 파악 어려움
      1: 발문과 본문이 논리적으로 불일치
    
    R5. 해설 충실도
      5: 왜 정답인지/왜 오답인지 핵심 개념으로 설명, 학습 효과 높음
      4: 정답 근거 충실, 오답 해설 다소 부족
      3: 해설이 피상적 ("~이므로 정답이다" 수준)
      2: 핵심 개념 언급 없이 결론만 제시
      1: 해설 누락 또는 오개념 포함
    ```
    
  ---

  **판정 기준과 REJECT 시 반환 형식**

    ```
    **PASS 조건** (모두 충족):
      - R1 ≥ 4
      - 전 항목 평균 ≥ 3.5
      - 어떤 항목도 2 이하가 아닐 것
      - 주관식: R2 제외, 나머지 4개 항목으로 판정
    
    **REJECT 조건** (하나라도 해당 시):
      - R1 ≤ 2 → 즉시 REJECT
      - 어떤 항목이든 1점 → 즉시 REJECT
      - 전 항목 평균 < 3.5
      
    **REJECT 시 반환 형식**
    - problem_id: 문제 임시 ID
    - verdict: REJECT
    - scores: { R1~R5 점수 }
    - avg: 평균
    - reject_reasons: 감점 항목별 구체적 사유
    - improvement_direction: 개선 방향 (generator가 참조)
    ```


**Skills**

- **`fetch-cs-note`**

  유닛의 식별자를 받아 유닛의 개념노트를 가져온다.

- **`fetch-existing-problems`**

  특정 유닛의 문제 목록을 조회한다. 유닛의 식별자로 하위 레슨을 조회한 뒤, 레슨별 문제를 가져온다.

- **`build-staging-output`**

  검수를 통과한 문제 SQL를 백오피스가 소비할 수 있는 형태로 가공한다. 백오피스 UI용 JSON과 최종 승인 시 실행할 SQL 쿼리문을 종합한다.


**Hooks**

- **`problem-formatter`**(command)

  JSON 키 배치, SQL 컬럼 구성 등, 서비스 도메인과의 구조적 유효성 검증

- **`sql-validator`**(command)

  INSERT 쿼리의 문법, 무결성 검증

- **`typo-checker`**(prompt)

  CS 도메인 맥락을 고려한 오탈자/문법 검출

- **`notify-complete`**(command)

  작업 완료시 Webhook 알림


#### 📌파이프라인 구조

```
[/generate-problems {unit_ids} 호출]
    │
    ├─ Phase 0. 복구 확인
    │   └─ pipeline-state-{날짜}.md 존재 시 → 중단 지점부터 재개
    │
    ├─ Phase 1. 계획 수립 (메인 세션)
    │   ├─ 유닛 ID 파싱, 하위 Lesson 조회
    │   └─ pipeline-state-{날짜}.md 생성 (Plan + Checklist 초기화)
    │
    ├─ Phase 2. 데이터 수집 (메인 세션)
    │   ├─ /fetch-cs-note → 개념노트 확보
    │   ├─ /fetch-existing-problems → 기존 문제 목록 확보
    │   └─ pipeline-state 업데이트
    │
    ├─ Phase 3. 문제 생성 (서브에이전트 병렬, context: fork)
    │   ├─ [Unit A] problem-generator → 6문제 생성
    │   ├─ [Unit B] problem-generator → 6문제 생성
    │   └─ [Unit C] problem-generator → 6문제 생성
    │   └─ [Hook: problem-formatter] 구조 검증
    │   └─ [Hook: typo-checker] 오탈자 검출
    │   └─ pipeline-state 업데이트
    │
    ├─ Phase 4. 문제 검수 (서브에이전트 병렬, context: fork, read-only)
    │   ├─ 각 문제를 직접 풀어 정답 검증
    │   ├─ 검수 루브릭(R1~R5) 항목별 1~5점 채점
    │   ├─ PASS/REJECT 판정
    │   └─ pipeline-state 업데이트
    │
    ├─ Phase 5. 피드백 루프 (1문제당 최대 3회)
    │   ├─ REJECT 문제 + 감점항목 + 개선방향 → problem-generator 재호출
    │   ├─ 재생성 → Phase 4 재검수 반복
    │   ├─ 3회 초과 시 manual-review 표기
    │   └─ pipeline-state 업데이트
    │
    ├─ Phase 6. 최종 빌드
    │   ├─ /build-staging-output → JSON + INSERT 쿼리 생성
    │   ├─ {날짜}-update-unit-{id}.json
    │   ├─ {날짜}-update-unit-{id}.sql
    │   └─ pipeline-state 최종 상태: COMPLETED
    │
    └─ [Hook: notify-complete] Webhook 알림
```

#### 📌파일 디렉토리 구조

```
프로젝트 루트/
├── .claude/
│   ├── CLAUDE.md                            ← compaction 보존 지침, pipeline-state 경로 명시
│   ├── agents/
│   │   ├── problem-generator.md             ← 문제 생성 서브에이전트 (context: fork)
│   │   └── problem-reviewer.md              ← 문제 검수 서브에이전트 (context: fork, read-only)
│   ├── review-rubric.md                     ← 검수 루브릭 (R1~R5 채점 기준)
│   └── settings.local.json
│
├── .claude/skills/
│   ├── generate-problems/
│   │   ├── SKILL.md                         ← 진입점 스킬 (Phase 0~6 오케스트레이션)
│   │   └── templates/
│   │       ├── output-template.md           ← JSON + SQL 출력 형식 정의
│   │       └── problem-examples.md          ← 문제 생성 기준 및 예시
│   ├── fetch-cs-note/
│   │   └── SKILL.md
│   ├── fetch-existing-problems/
│   │   └── SKILL.md
│   └── build-staging-output/
│       └── SKILL.md
│
├── .claude/hooks/
│   ├── problem-formatter.sh                 ← PreToolUse: JSON/SQL 구조 검증
│   ├── sql-validator.sh                     ← PreToolUse: INSERT 쿼리 무결성
│   ├── typo-checker (prompt)                ← PostToolUse: CS 도메인 오탈자 검출
│   └── notify-complete.sh                   ← Stop: Webhook 알림
│
└── pipeline-workspace/
    ├── pipeline-state-{YYYY-MM-DD}.md       ← 체크리스트 + 요약 로그 (통합)
    └── output/
        ├── {날짜}-update-unit-{id}.json      ← 백오피스 UI용 JSON
        └── {날짜}-update-unit-{id}.sql       ← 최종 승인용 INSERT 쿼리
```