---
description: 학습 콘텐츠 INSERT SQL 쿼리 작성 템플릿 및 순서.
---

# 학습 콘텐츠 SQL INSERT 템플릿

## 쿼리 작성 순서

lesson → problem → option (OBJECTIVE) → answer (SUBJECTIVE) 순서로 작성하라. 같은 lesson의 option은 하나의 INSERT VALUES 블록으로 묶어라.

## 템플릿

```sql
-- Lesson 생성
INSERT INTO lesson (id, unit_id, title)
VALUES ({lesson_id}, {unit_id}, '{lesson_title}');

-- 문제 생성
INSERT INTO problem (id, lesson_id, instruction, content, problem_type)
VALUES
  ({problem_id}, {lesson_id}, '{instruction}', '{content}', 'OBJECTIVE'),
  ({problem_id}, {lesson_id}, '{instruction}', '{content}', 'OBJECTIVE'),
  ({problem_id}, {lesson_id}, '{instruction}', '{content}', 'OBJECTIVE'),
  ({problem_id}, {lesson_id}, '{instruction}', '{content}', 'OBJECTIVE'),
  ({problem_id}, {lesson_id}, '{instruction}', '{content}', 'SUBJECTIVE'),
  ({problem_id}, {lesson_id}, '{instruction}', '{content}', 'SUBJECTIVE');

-- 선지 생성 (OBJECTIVE 문제만, lesson 단위로 하나의 블록으로 묶어라)
INSERT INTO option (id, problem_id, content, explanation, is_answer)
VALUES
  ({option_id}, {problem_id}, '{content}', '{explanation}', false),
  ({option_id}, {problem_id}, '{content}', '{explanation}', false),
  ({option_id}, {problem_id}, '{content}', '{explanation}', false),
  ({option_id}, {problem_id}, '{content}', '{explanation}', true),
  -- 나머지 OBJECTIVE 문제 선지 ...
  ;

-- 정답 생성 (SUBJECTIVE 문제만)
INSERT INTO answer (id, problem_id, content, explanation)
VALUES
  ({answer_id}, {problem_id}, '{정답1,정답2,정답3}', '{explanation}'),
  ({answer_id}, {problem_id}, '{정답1,정답2,정답3}', '{explanation}');
```
