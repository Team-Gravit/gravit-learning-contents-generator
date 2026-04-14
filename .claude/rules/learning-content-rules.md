---
description: 학습 콘텐츠(lesson, 문제, 정답, 선지) 구성 및 생성 규칙.
---

# 학습 콘텐츠 구성 규칙

이 파일은 콘텐츠 **spec**이다. 각 섹션 말미의 `> 집행:` 태그는 규칙이 어디에서 강제·구현되는지 가리킨다. 규칙을 바꾸면 태그가 지시하는 구현체도 함께 갱신하라.

---

## 기본 단위

스킬 1회 호출당 lesson 1개를 생성하라. lesson 1개는 반드시 OBJECTIVE 4문제 + SUBJECTIVE 2문제 = 총 6문제로 구성하라.

> 초기 시드 데이터(`pipeline-workspace/problem-seed/`)는 유닛당 2~3개 레슨으로 구성되어 있다. 이는 초기 데이터 적재 시의 예외적 규약이므로 참고만 하라. 파이프라인 운영 기준은 1회 호출 = 1 lesson이다.

> **집행:** `hooks/learning-content-formatter.sh` — 문제 수·유형 비율 count 검증 (fail-closed).

---

## OBJECTIVE 문제 규칙

- 선지를 정확히 4개 생성하라
- 정답(`is_answer=true`) 선지는 반드시 1개만 포함하라
- 오답 선지는 명확한 오개념에 기반하여 그럴듯하게 작성하라. 너무 쉽게 소거되는 선지를 만들지 마라

> **집행:**
> - 선지 4개 / 정답 1개 → `hooks/learning-content-formatter.sh` (count 검증)
> - 오답의 "그럴듯함" → `agents/learning-content-generator.md` (judgment-required, 프롬프트 인라인 + `templates/problem-examples.md` few-shot)

---

## SUBJECTIVE 문제 규칙

- answer를 1개 생성하라
- content 필드에 허용 정답을 쉼표로 구분하여 나열하라 (예: `랜,lan,local area network`)
- 정답은 대소문자 구분 없이 매칭되므로, 주요 표현·한글·영문 약어·풀네임을 빠짐없이 포함하라

> **집행:**
> - answer 개수 = 1 → `hooks/learning-content-formatter.sh`
> - 허용 정답 나열의 완전성 → `agents/learning-content-generator.md` (judgment-required + 예시)

---

## 문제 생성 기준

- 개념노트의 핵심 개념을 6문제에 고르게 분배하라. 특정 개념에만 편중되지 않도록 하라
- 기존 문제 목록을 반드시 확인하라. 개념 범위의 중첩(동일 주제를 다루는 문제)은 일부 허용되지만, 발문·본문·선지 구성이 사실상 동일한 문제는 생성하지 마라
- 타겟층(CS 배경 취준생/학부생) 기준으로 개념 이해 + 약간의 응용이 필요한 난이도로 작성하라
- 발문(instruction)과 본문(content)이 자연스럽게 이어지도록 작성하라

> **집행:** 전부 `agents/learning-content-generator.md` (judgment-required). 중복 회피에 필요한 "기존 문제 목록"은 `skills/generate-learning-content`가 Phase 3 호출 시 서브에이전트에 인자로 전달한다.
