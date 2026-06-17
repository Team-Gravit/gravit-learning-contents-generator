---
name: fetch-existing-learning-contents
description: 지정된 유닛의 기존 학습 콘텐츠 SQL을 generation-output에서 수집하여 표준 출력으로 반환한다.
allowed-tools: Read, Glob
---

## fetch-existing-learning-contents

### 입력
- **unit_id** (int, 필수) — 정수 그대로 전달된다 (예: **1**, **11**).

### 출력
- 표준 출력: 매칭된 파일마다 아래 블록을 이어 붙인다.
  ```
  === source: {프로젝트 루트 기준 상대경로} ===
  {파일 내용}
  ```
- 매칭 파일이 0건이면 **NO_EXISTING_CONTENT** 한 줄만 출력한다.

### 절차

#### Phase 1. 파일 탐색
아래 글롭으로 파일 경로를 수집한다.

- `pipeline-workspace/generation-output/*/{unit_id}/*.sql`
  - **unit_id**는 zero-pad 없이 정수로 그대로 치환한다.
  - **unit_id = 1**일 때 최종 글롭: `pipeline-workspace/generation-output/*/1/*.sql`

`pipeline-workspace/problem-seed/`는 수집 대상이 아니다. 시드 문제는 서비스에서 더 이상 쓰이지 않아 중복 회피 맥락에 포함하지 않는다 (파일은 그대로 보관).

#### Phase 2. 내용 연결
수집된 각 파일을 읽어 "출력" 형식대로 연결해 표준 출력으로 내보낸다. 0건이면 **NO_EXISTING_CONTENT**.

### 실패 처리
- Read 실패 파일은 호출자에게 그대로 노출한다. 자체 재시도 없음.
