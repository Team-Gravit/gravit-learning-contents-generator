---
name: fetch-max-id
description: lesson/problem/option/answer는 prod·staging 통합 MAX, staging_label은 자체 MAX를 집계하여 ID Baseline으로 반환한다.
allowed-tools: Bash
---

## fetch-max-id

운영 데이터베이스에서 `lesson/problem/option/answer`는 **prod 테이블과 _staging 테이블의 통합 MAX**(GREATEST), **staging_label**은 자체 MAX ID를 조회하여 반환한다.

prod만 조회하면 아직 promote되지 않은 staging의 남은 배치가 baseline에 반영되지 않아 Phase 7 저장 시 PK 충돌이 난다. 통합 MAX를 쓰면 staging에 남은 데이터가 있어도, promote 후 정리돼도 항상 안전하다.

### 입력
없음

### 출력
- 표준 출력:
  ```
  last_lesson_id: {int}
  last_problem_id: {int}
  last_option_id: {int}
  last_answer_id: {int}
  last_label_id: {int}
  ```
- 테이블이 비어 있으면 해당 값은 0.

### 참조 파일
- `.claude/spec/generation/id-management.md`
- `.claude/spec/generation/learning-content-sql-schema.md`

### 절차

#### Phase 1. DATABASE_URL 로드
```
set -a && . ./.env && set +a
[ -z "$DATABASE_URL" ] && { echo "DATABASE_URL missing" >&2; exit 1; }
```

#### Phase 2. MAX ID 조회
**option**은 예약어이므로 쌍따옴표로 감싼다.

```
psql "$DATABASE_URL" -tAF'|' -v ON_ERROR_STOP=1 -c "
SELECT
  GREATEST(COALESCE((SELECT MAX(id) FROM lesson), 0),    COALESCE((SELECT MAX(id) FROM lesson_staging), 0)),
  GREATEST(COALESCE((SELECT MAX(id) FROM problem), 0),   COALESCE((SELECT MAX(id) FROM problem_staging), 0)),
  GREATEST(COALESCE((SELECT MAX(id) FROM \"option\"), 0), COALESCE((SELECT MAX(id) FROM option_staging), 0)),
  GREATEST(COALESCE((SELECT MAX(id) FROM answer), 0),    COALESCE((SELECT MAX(id) FROM answer_staging), 0)),
  COALESCE((SELECT MAX(id) FROM staging_label), 0);
"
```

#### Phase 3. 출력 포맷 변환
```
IFS='|' read -r L P O A LB <<< "$RESULT"
printf 'last_lesson_id: %d\nlast_problem_id: %d\nlast_option_id: %d\nlast_answer_id: %d\nlast_label_id: %d\n' "$L" "$P" "$O" "$A" "$LB"
```

### 실패 처리
- `.env` 또는 **DATABASE_URL** 누락 → 즉시 중단.
- psql 실패 → stderr와 종료 코드를 그대로 노출. 자체 재시도 없음.
