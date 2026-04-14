---
description: Gravit 서비스의 학습 콘텐츠 관련 테이블 스키마.
---

# 학습 콘텐츠 SQL 스키마

**lesson**

| 컬럼    | 타입    | 설명       |
|---------|---------|------------|
| id      | INT PK  | 레슨 식별자 |
| unit_id | INT FK  | 유닛 식별자 |
| title   | VARCHAR | 레슨 제목   |

**problem**

| 컬럼         | 타입                           | 설명           |
|--------------|--------------------------------|----------------|
| id           | INT PK                         | 문제 식별자     |
| lesson_id    | INT FK                         | 레슨 식별자     |
| instruction  | VARCHAR                        | 발문           |
| content      | VARCHAR                        | 본문           |
| problem_type | ENUM('OBJECTIVE','SUBJECTIVE') | 문제 유형      |

**option** — OBJECTIVE 전용

| 컬럼        | 타입    | 설명                      |
|-------------|---------|---------------------------|
| id          | INT PK  | 선지 식별자                |
| problem_id  | INT FK  | 문제 식별자                |
| content     | VARCHAR | 선지 내용                  |
| explanation | VARCHAR | 해설                      |
| is_answer   | BOOLEAN | 정답 여부 (정답 선지 1개)  |

**answer** — SUBJECTIVE 전용

| 컬럼        | 타입    | 설명                                                |
|-------------|---------|-----------------------------------------------------|
| id          | INT PK  | 정답 식별자                                          |
| problem_id  | INT FK  | 문제 식별자                                          |
| content     | VARCHAR | 허용 정답 (쉼표 구분: `랜,lan,local area network`)   |
| explanation | VARCHAR | 해설                                                |
