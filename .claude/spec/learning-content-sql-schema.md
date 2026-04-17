---
description: Gravit 서비스의 학습 콘텐츠 관련 테이블 스키마. prod 테이블과 staging 테이블(파이프라인 출력 대상).
---

# 학습 콘텐츠 SQL 스키마

## prod 테이블

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

---

## staging 테이블

파이프라인 출력은 `_staging` 테이블에 적재된다(Phase 7). 각 테이블은 prod 테이블과 **같은 컬럼 구조**에 `label VARCHAR NOT NULL` 컬럼이 추가된다. 백오피스에서 staging 테이블을 조회·검수한 후 prod 테이블로 승격한다.

`label` 값은 배치 식별자로, 파이프라인 실행일 기반 고정 포맷 `YYYY-MM-DD-update` (예: `2026-04-16-update`).

**lesson_staging**

| 컬럼    | 타입    | 설명       |
|---------|---------|------------|
| id      | INT PK  | 레슨 식별자 |
| unit_id | INT FK  | 유닛 식별자 |
| title   | VARCHAR | 레슨 제목   |
| label   | VARCHAR | 배치 식별자 (`YYYY-MM-DD-update`) |

**problem_staging**

| 컬럼         | 타입                           | 설명           |
|--------------|--------------------------------|----------------|
| id           | INT PK                         | 문제 식별자     |
| lesson_id    | INT FK                         | 레슨 식별자     |
| instruction  | VARCHAR                        | 발문           |
| content      | VARCHAR                        | 본문           |
| problem_type | ENUM('OBJECTIVE','SUBJECTIVE') | 문제 유형      |
| label        | VARCHAR                        | 배치 식별자     |

**option_staging** — OBJECTIVE 전용

| 컬럼        | 타입    | 설명                      |
|-------------|---------|---------------------------|
| id          | INT PK  | 선지 식별자                |
| problem_id  | INT FK  | 문제 식별자                |
| content     | VARCHAR | 선지 내용                  |
| explanation | VARCHAR | 해설                      |
| is_answer   | BOOLEAN | 정답 여부 (정답 선지 1개)  |
| label       | VARCHAR | 배치 식별자                |

**answer_staging** — SUBJECTIVE 전용

| 컬럼        | 타입    | 설명                                                |
|-------------|---------|-----------------------------------------------------|
| id          | INT PK  | 정답 식별자                                          |
| problem_id  | INT FK  | 문제 식별자                                          |
| content     | VARCHAR | 허용 정답                                            |
| explanation | VARCHAR | 해설                                                |
| label       | VARCHAR | 배치 식별자                                          |
