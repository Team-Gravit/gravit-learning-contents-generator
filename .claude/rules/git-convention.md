---
description: 커밋, 브랜치, PR 등 Git 작업 시 적용되는 규칙
paths:
  - ".github/**"
---

# Git Convention

## 커밋 메시지

형식: `{type}: 커밋 내용(#{이슈번호})`

| type | 용도 |
|---|---|
| feat | 새로운 기능 |
| hotfix | 긴급 수정 |
| fix | 버그 수정 |
| docs | 문서 변경 |
| test | 테스트 추가/수정 |
| cicd | CI/CD 설정 변경 |
| refactor | 리팩토링 |

예시: `feat: 북마크 기능 구현(#123)`

## 브랜치 전략

- `main` → 각자 개발 브랜치
- main에 직접 커밋하지 마라
- 개발 브랜치 네이밍: `{type}/#{이슈번호}-{간단한설명}` (예: `feat/#123-bookmark`)
