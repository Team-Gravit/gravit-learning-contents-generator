---
name: fetch-max-id
description: lesson/problem/option/answer의 MAX ID를 집계하여 ID Baseline으로 반환한다.
allowed-tools: Read, Glob, Bash
---

# fetch-max-id
가장 최근 파이프라인 사이클에서 발번된 lesson/problem/option/answer ID 중 최대값을 반환한다. 결과는 Phase 2에서 `pipeline-state`의 `ID Baseline`에 기록된다.

## 입력
없음

## 출력
- 표준 출력 형식 (호출자가 이 값을 파싱하여 pipeline-state에 기록):
  ```
  last_lesson_id: {int}
  last_problem_id: {int}
  last_option_id: {int}
  last_answer_id: {int}
  ```

## 참조 파일
- `.claude/spec/id-management.md` — baseline 기록 형식
- `.claude/spec/learning-content-sql-template.md` — 파싱 대상 INSERT 템플릿 구조

## 절차

### Phase 1. 최신 날짜 디렉토리 탐색
1. `pipeline-workspace/generation-output/` 하위의 직속 디렉토리 목록을 수집한다.
2. 이름이 `YYYY-MM-DD` 형식에 매칭되는 디렉토리만 남긴다.
3. 문자열 내림차순 정렬하여 가장 최신 날짜 `latest_date`를 선택한다.
4. 디렉토리가 없거나 형식에 맞는 것이 없으면 **Phase 5의 "비어있음 처리"로 이동**한다.

### Phase 2. lesson.sql 파일 수집
1. `pipeline-workspace/generation-output/{latest_date}/*/lesson.sql` 글롭으로 모든 유닛의 SQL 파일을 수집한다.
2. 수집된 파일이 0개면 **Phase 5의 "비어있음 처리"로 이동**한다.

### Phase 3. 파일별 테이블 ID 추출
각 sql 파일을 Read하여, 아래 테이블에 대해 INSERT 블록의 **마지막 VALUES row**에서 첫 번째 정수(= 해당 테이블의 id)만 추출한다.
- `lesson_staging`
- `problem_staging`
- `option_staging`
- `answer_staging`

### Phase 4. 파일 간 최대값 집계
Phase 3에서 얻은 파일별 값을 테이블별로 모아 max를 취한다. 값이 전혀 없는 테이블은 0.

### Phase 5. 결과 반환
- **정상:** 위 "출력" 형식으로 표준 출력.
- **비어있음 처리:** `generation-output`이 없거나 스캔 결과가 0건이면 모든 값을 0으로 반환한다. 호출자(Phase 2)가 첫 실행인지 판단한다.

## 실패 처리
- sql 파싱 결과가 비정상(음수, 형식 위반 등)이면 사용자에게 검토를 요청하고 승인한 값으로 확정한다.
