---
description: 검수 결과(review.md)를 레슨 종합 점수로 환산하는 산식과, 감점을 책임 스펙 파일로 귀인하는 맵, 체계적/일회성 판정 기준. assess-learning-content-quality 스킬이 읽는다.
---

## 감점 귀인 & 종합 점수

`assess-learning-content-quality` 스킬이 한 번의 파이프라인 실행(**pipeline-state 1개**)의 모든 `review.md`를 읽어, 레슨에 종합 점수를 매기고 감점을 스펙 파일에 귀인할 때 따르는 기준이다. 채점을 새로 하지 않고 **기존 `review.md`의 R1~R6를 집계**한다.

---

### 1. 종합 점수 산식

입력: 각 `review.md`의 문제별 R1~R5(1~5 정수)와 레슨 R6(1~5 정수). 의미는 `review-rubric.md`를 따른다.

- 문제 점수 = (적용 R항목 평균 ÷ 5) × 100
  - 객관식 적용 항목: R1·R2·R3·R4·R5
  - 주관식 적용 항목: R1·R3·R4·R5 (R2 제외)
- 6문제 평균 = 여섯 문제 점수의 산술평균
- **레슨 종합 점수 = 0.85 × (6문제 평균) + 0.15 × (R6 ÷ 5 × 100)**
- 실행 종합 = 레슨 종합 점수들의 평균. 분포와 최저 레슨도 함께 보고한다.

가중치(0.85 / 0.15)는 기본값이며 조정 가능하다.

---

### 2. 감점 신호

- **감점 신호** = 어떤 R항목 점수가 **≤ 3**이거나, 그 항목이 `review.md`의 **reject_reasons**에 등장한 경우.
- 4점은 경미한 흠으로 보고 신호에서 제외한다(만점 5 기준).
- `review.md`가 AP 코드(예: **AP-01**)를 사유에 적었으면 그 코드도 신호로 함께 수집한다. (`review-rubric.md` R4 프로토콜에 따라 reject 사유에 AP 코드가 실릴 수 있다.)
- 표기·용어 지적은 R항목에 없으므로, **reject_reasons / improvement_direction의 자유 서술**에서 표기·용어 언급을 별도 신호(**S**)로 수집한다.

---

### 3. 귀인 맵

감점 신호를 1차 책임 규칙과 책임 스펙 파일로 잇는다.

| 감점 신호 | 1차 책임 규칙 | 책임 스펙 파일 | 비고 |
|---|---|---|---|
| R1 정답 정확성 | INV-3 | (체계적이면) rules / 주관식은 antipatterns AP-08 | 대개 생성 슬립 — 1순위는 Phase 5 재시도 |
| R2 선지 변별력 | INV-4 / AP-02·AP-07·AP-03 | rules · antipatterns · good-patterns | 객관식만 |
| R3 난이도 적절성 | 문제 생성 기준 | rules | |
| R4 본문기능성·발문 | INV-1·INV-2·INV-6 / AP-01·AP-04·AP-06 | rules · antipatterns · good-patterns | |
| R5 해설 충실도 | EXP-1~EXP-4 / AP-05 | rules · antipatterns · good-patterns | |
| R6 난이도 균형 | 문제 생성 기준(다양성·정답위치 분산·난이도 분포) | rules | 레슨 단위 |
| S 표기·용어 | S1~S6 | writing-style | R항목 외, 자유서술에서만 수집 |

파일 경로:
- rules → `.claude/spec/generation/learning-content-rules.md`
- writing-style → `.claude/spec/generation/learning-content-writing-style.md`
- good-patterns → `.claude/spec/generation/problem-good-patterns.md`
- antipatterns → `.claude/spec/generation/problem-antipatterns.md`

한 신호가 여러 파일을 가리키면, 어느 파일을 고칠지는 제안 단계에서 패턴의 성격으로 좁힌다.

- "오답이 터무니없어 소거된다" → antipatterns(AP-02) 보강
- "정답만 길어 새어 나간다" → antipatterns(AP-07) 보강
- "규칙은 있는데 예시가 없어 못 따라 한다" → good-patterns에 해당 유형 예시 추가
- "규칙 자체가 약하거나 모호하다" → rules의 해당 INV/EXP 강화

---

### 4. 체계적 vs 일회성

같은 신호가 아래 중 **하나라도** 충족하면 **체계적**(스펙 제안 대상):

- **레슨 내**: 한 레슨의 6문제 중 **≥ 3문제**에서 같은 신호.
- **실행 내**: 실행의 레슨 중 **≥ 50%**에서 같은 신호.

둘 다 못 미치면 **일회성**이다. 스펙을 바꾸지 않고 **"Phase 5 재시도 권장"** 목록으로만 보고한다. 한 번 삐끗한 감점에 스펙을 바꾸면 규칙이 그 사례에 과적합된다.

---

### 5. 제안 작성 규칙

체계적 약점 하나당 제안 하나. 각 제안은 다음을 담는다.

- **대상 스펙 파일** (귀인 맵 기준)
- **근거**: 어느 레슨/문제의 어느 신호에서 몇 번 나왔는지 집계
- **변경 전 → 변경 후**: 반영할 구체 텍스트
- **기대 효과**

제안은 **1번부터 넘버링**한다. 적용은 사용자가 지정한 번호에 한한다. 새 안티패턴을 추가할 때는 `problem-antipatterns.md`의 기존 **AP-NN** 번호를 이어서 발번한다.
