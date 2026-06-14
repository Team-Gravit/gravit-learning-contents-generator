---
description: Gravit 서비스의 학습 콘텐츠 관련 테이블 스키마. prod 테이블과 staging 테이블(파이프라인 출력 대상).
---

## 학습 콘텐츠 SQL 스키마

> **길이 한도 주의.** 아래 `VARCHAR(n)` 컬럼은 운영 DB가 실제로 강제하는 한도다(문자 수 기준). 한도를 넘기면 `validate-lesson-sql.py`는 통과하더라도 **Phase 7 적재 시 `value too long for type character varying(n)`으로 실패**한다. 본문(`problem.content`)·정답 해설(`answer.explanation`)만 `TEXT`(무제한)이고, 제목·발문·선지 내용·선지 해설·정답 내용은 모두 **255자**, `label`은 **32자**다. 생성 시 특히 **선지 해설(option.explanation)**이 한도를 넘기기 쉬우니 255자 안쪽으로 쓴다.

### prod 테이블

**lesson**

| 컬럼    | 타입         | 설명       |
|---------|--------------|------------|
| id      | INT PK       | 레슨 식별자 |
| unit_id | INT FK       | 유닛 식별자 |
| title   | VARCHAR(255) | 레슨 제목   |

**problem**

| 컬럼         | 타입                           | 설명           |
|--------------|--------------------------------|----------------|
| id           | INT PK                         | 문제 식별자     |
| lesson_id    | INT FK                         | 레슨 식별자     |
| instruction  | VARCHAR(255)                   | 발문           |
| content      | TEXT                           | 본문 (무제한)   |
| problem_type | ENUM('OBJECTIVE','SUBJECTIVE') | 문제 유형      |

**option** — OBJECTIVE 전용

| 컬럼        | 타입         | 설명                      |
|-------------|--------------|---------------------------|
| id          | INT PK       | 선지 식별자                |
| problem_id  | INT FK       | 문제 식별자                |
| content     | VARCHAR(255) | 선지 내용                  |
| explanation | VARCHAR(255) | 해설                      |
| is_answer   | BOOLEAN      | 정답 여부 (정답 선지 1개)  |

**answer** — SUBJECTIVE 전용

| 컬럼        | 타입         | 설명                                                |
|-------------|--------------|-----------------------------------------------------|
| id          | INT PK       | 정답 식별자                                          |
| problem_id  | INT FK       | 문제 식별자                                          |
| content     | VARCHAR(255) | 허용 정답 (쉼표로 구분)                              |
| explanation | TEXT         | 해설 (무제한)                                        |

---

### staging 테이블

각 staging 테이블은 prod 테이블과 **같은 컬럼 구조·길이 한도**에 **label VARCHAR(32) NOT NULL** 컬럼이 추가된다.

**label** 값 포맷: **YYYY-MM-DD-{4자 16진수 랜덤}** (예: **2026-04-25-a3f9**). **label** 컬럼은 **staging_label.label**을 외래키로 참조한다.

**staging_label**

| 컬럼        | 타입                                  | 설명                                              |
|-------------|---------------------------------------|---------------------------------------------------|
| id          | BIGINT PK                             | 라벨 식별자 (외부 발번 — **fetch-max-id** baseline 기반) |
| label       | VARCHAR(32) UNIQUE NOT NULL           | 라벨 값 (**YYYY-MM-DD-{4자}**)                      |
| unit_id     | BIGINT NOT NULL                       | 유닛 식별자                                       |
| description | VARCHAR(255) NOT NULL                 | **Unit {unit_id} - 신규 lesson 1건**                |
| status      | VARCHAR(20) NOT NULL DEFAULT 'PENDING' | **PENDING** / **COMPLETED** (CHECK 제약). **DB DEFAULT — 파이프라인은 INSERT하지 않음** |
| created_at  | TIMESTAMP NOT NULL DEFAULT NOW()      | 생성 시각. **DB DEFAULT — 파이프라인은 INSERT하지 않음** |

> 파이프라인은 `staging_label`에 **(id, label, unit_id, description)** 4개 컬럼만 INSERT한다. `status`·`created_at`은 DB DEFAULT가 채우므로 **직접 INSERT 금지**.

**lesson_staging**

| 컬럼    | 타입         | 설명       |
|---------|--------------|------------|
| id      | INT PK       | 레슨 식별자 |
| unit_id | INT FK       | 유닛 식별자 |
| title   | VARCHAR(255) | 레슨 제목   |
| label   | VARCHAR(32)  | 배치 식별자 (FK → **staging_label.label**) |

**problem_staging**

| 컬럼         | 타입                           | 설명           |
|--------------|--------------------------------|----------------|
| id           | INT PK                         | 문제 식별자     |
| lesson_id    | INT FK                         | 레슨 식별자     |
| instruction  | VARCHAR(255)                   | 발문           |
| content      | TEXT                           | 본문 (무제한)   |
| problem_type | ENUM('OBJECTIVE','SUBJECTIVE') | 문제 유형      |
| label        | VARCHAR(32)                    | 배치 식별자 (FK → **staging_label.label**) |

**option_staging** — OBJECTIVE 전용

| 컬럼        | 타입         | 설명                      |
|-------------|--------------|---------------------------|
| id          | INT PK       | 선지 식별자                |
| problem_id  | INT FK       | 문제 식별자                |
| content     | VARCHAR(255) | 선지 내용                  |
| explanation | VARCHAR(255) | 해설                      |
| is_answer   | BOOLEAN      | 정답 여부 (정답 선지 1개)  |
| label       | VARCHAR(32)  | 배치 식별자 (FK → **staging_label.label**) |

**answer_staging** — SUBJECTIVE 전용

| 컬럼        | 타입         | 설명                                                |
|-------------|--------------|-----------------------------------------------------|
| id          | INT PK       | 정답 식별자                                          |
| problem_id  | INT FK       | 문제 식별자                                          |
| content     | VARCHAR(255) | 허용 정답                                            |
| explanation | TEXT         | 해설 (무제한)                                        |
| label       | VARCHAR(32)  | 배치 식별자 (FK → **staging_label.label**)            |
