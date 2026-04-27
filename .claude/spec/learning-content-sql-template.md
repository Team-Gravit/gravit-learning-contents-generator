---
description: 학습 콘텐츠 INSERT SQL 쿼리 작성 템플릿 및 순서. 파이프라인은 `_staging` 테이블에 적재한다.
---

# 학습 콘텐츠 SQL INSERT 템플릿

## 쿼리 작성 순서

`staging_label` → `lesson_staging` → `problem_staging` → `option_staging` (OBJECTIVE) → `answer_staging` (SUBJECTIVE) 순서로 작성하라.

`{label}`은 호출자가 인자로 전달한 값을 그대로 사용하라. 임의로 생성하지 마라.

## 템플릿

```sql
-- 라벨 메타 등록 (FK 부모, 반드시 첫 INSERT)
INSERT INTO staging_label (id, label, unit_id, description)
VALUES ({label_id}, '{label}', {unit_id}, 'Unit {unit_id} - 신규 lesson 1건');

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
