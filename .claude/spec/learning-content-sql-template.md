---
description: 학습 콘텐츠 INSERT SQL 쿼리 작성 템플릿 및 순서. 파이프라인은 `_staging` 테이블에 적재한다.
---

# 학습 콘텐츠 SQL INSERT 템플릿

## 쿼리 작성 순서

`lesson_staging` → `problem_staging` → `option_staging` (OBJECTIVE) → `answer_staging` (SUBJECTIVE) 순서로 작성하라. 같은 lesson의 option은 하나의 INSERT VALUES 블록으로 묶어라.

`{label}`은 pipeline-state 헤더 `date` 값 기반 `YYYY-MM-DD-update` 고정 포맷이다 (예: `2026-04-16-update`).

## 템플릿

```sql
-- Lesson 생성
INSERT INTO lesson_staging (id, unit_id, title, label)
VALUES ({lesson_id}, {unit_id}, '{lesson_title}', '{label}');

-- 문제 생성
INSERT INTO problem_staging (id, lesson_id, instruction, content, problem_type, label)
VALUES
  ({problem_id}, {lesson_id}, '{instruction}', '{content}', 'OBJECTIVE', '{label}'),
  ({problem_id}, {lesson_id}, '{instruction}', '{content}', 'OBJECTIVE', '{label}'),
  ({problem_id}, {lesson_id}, '{instruction}', '{content}', 'OBJECTIVE', '{label}'),
  ({problem_id}, {lesson_id}, '{instruction}', '{content}', 'OBJECTIVE', '{label}'),
  ({problem_id}, {lesson_id}, '{instruction}', '{content}', 'SUBJECTIVE', '{label}'),
  ({problem_id}, {lesson_id}, '{instruction}', '{content}', 'SUBJECTIVE', '{label}');

-- 선지 생성 (OBJECTIVE 문제만, lesson 단위로 하나의 블록으로 묶어라)
INSERT INTO option_staging (id, problem_id, content, explanation, is_answer, label)
VALUES
  ({option_id}, {problem_id}, '{content}', '{explanation}', false, '{label}'),
  ({option_id}, {problem_id}, '{content}', '{explanation}', false, '{label}'),
  ({option_id}, {problem_id}, '{content}', '{explanation}', false, '{label}'),
  ({option_id}, {problem_id}, '{content}', '{explanation}', true, '{label}'),
  -- 나머지 OBJECTIVE 문제 선지 ...
  ;

-- 정답 생성 (SUBJECTIVE 문제만)
INSERT INTO answer_staging (id, problem_id, content, explanation, label)
VALUES
  ({answer_id}, {problem_id}, '{정답1,정답2,정답3}', '{explanation}', '{label}'),
  ({answer_id}, {problem_id}, '{정답1,정답2,정답3}', '{explanation}', '{label}');
```