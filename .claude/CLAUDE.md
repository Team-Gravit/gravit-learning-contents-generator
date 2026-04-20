# Gravit Learning Contents Generator

Gravit CS 학습 콘텐츠(lesson / problem / option / answer) 자동 생성 파이프라인.
`/generate-learning-content` 스킬 1회 호출로 생성 → 검수 → 피드백 루프 → 스테이징 빌드까지 실행된다.

파이프라인의 **오케스트레이션은 skill이 소유**한다. 이 파일은 항상 필요한 최소 정보만 둔다.

---

## Pipeline State

- **위치:** `pipeline-workspace/pipeline-state-{YYYY-MM-DD}.md`
- **스키마:** `.claude/spec/pipeline-state-template.md`

**복구 규칙 (compaction / 세션 재시작 시):** 오늘 날짜의 pipeline-state 파일이 있으면 먼저 Read하고, Checklist에서 미완료인 가장 이른 phase부터 재개한다. 파일이 없으면 skill을 새로 시작한다.

---

## Spec 인덱스

각 스펙은 SoT 문서로 `.claude/spec/` 하위에 있다. skill / agent / hook이 **필요 시점에 Read로 로드**한다.

- `.claude/spec/learning-content-rules.md` — 콘텐츠 구성 규칙
- `.claude/spec/learning-content-writing-style.md` — 한국어 표기·CS 용어·일관성 스타일 규칙
- `.claude/spec/learning-content-sql-schema.md` — DB 테이블 스키마 (prod + `_staging`)
- `.claude/spec/learning-content-sql-template.md` — INSERT 쿼리 템플릿
- `.claude/spec/problem-examples.md` — generator few-shot 예시
- `.claude/spec/id-management.md` — ID 발번 규칙
- `.claude/spec/pipeline-state-template.md` — pipeline-state 파일 스키마
- `.claude/spec/review-rubric.md` — R1~R6 검수 루브릭
- `.claude/spec/review-template.md` — 검수 출력 템플릿
