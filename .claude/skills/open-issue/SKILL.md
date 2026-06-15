---
name: open-issue
description: |
  이슈 템플릿(.github/ISSUE_TEMPLATE)에 맞춰 GitHub 이슈를 생성한다. 제목·본문은 간결하게 작성하고 gh issue create를 실행한다.
  Trigger: "이슈 만들어줘", "이슈 파줘", "이슈 생성해줘", "이슈 올려줘"
  Do NOT use for: PR 생성(open-pr), 브랜치 생성·전환, 커밋
  Boundary: 이슈 생성까지만 수행한다. 브랜치 생성·전환, PR, 라벨 신규 생성은 범위 밖이다.
allowed-tools: Bash(gh *), Read
---

# 이슈 생성

대상 내용: $ARGUMENTS

## Phase 1: 이슈 타입 결정

1. $ARGUMENTS(또는 대화 맥락)에서 이슈의 성격을 파악해 타입을 고른다. 타입은 `.github/ISSUE_TEMPLATE`의 5종 중 하나다.
   - `feat` — 새로운 기능
   - `fix` — 버그 수정
   - `docs` — 문서 변경
   - `hotfix` — 긴급 수정
   - `refactor` — 리팩토링
2. 타입이 모호하면 사용자에게 물어본다.

> 다음 Phase 조건: 타입이 정해졌을 때

> Skip 조건: 없음 (필수 Phase)

## Phase 2: 제목·본문 작성

1. `.github/ISSUE_TEMPLATE/{type}-issue-template.md`를 Read로 읽어 본문 구조(`1. Issue Description`, `2. Issue Task`)를 확인하라.
2. 제목은 `{type}: {간결한 한 줄}` 형식으로 작성하라. (예: `feat: 학습 컨텐츠 평가 스킬 추가`)
3. 본문은 템플릿 구조를 그대로 따르되 **최대한 간결하게** 채워라.
   - `1. Issue Description` — 1~2문장.
   - `2. Issue Task` — 핵심 작업 체크박스 1~3개.
   - 템플릿의 안내 문구(예: "이슈에 대한 설명을 작성해주세요.", "작업명")는 실제 내용으로 교체하라.

```
### 1.  Issue Description

---

{1~2문장 설명}

<br>

### 2. Issue Task

---

- [ ] {핵심 작업}
```

> 다음 Phase 조건: 제목과 본문이 완성되었을 때

> Skip 조건: 없음 (필수 Phase)

## Phase 3: 이슈 생성

1. assignee는 **항상 본인(`@me`)**으로 한다.
2. 라벨: 타입에 해당하는 라벨을 `--label`로 붙여라. 매핑은 아래와 같다(레포에 이미 존재하는 실제 라벨명).
   - `feat` → `🌼 Feat`
   - `fix` → `🔨 Fix`
   - `docs` → `📚 Docs`
   - `hotfix` → `🔥 HotFix`
   - `refactor` → `🧹Refactor`
   매핑된 라벨이 없으면 생략하라. 새 라벨을 만들지 마라.
3. 다음 명령으로 이슈를 생성하라:
   ```bash
   gh issue create --title "{제목}" --body "{본문}" --assignee @me [--label {라벨}]
   ```
4. 생성된 이슈 URL과 번호를 사용자에게 보고하라.
5. **브랜치 생성·전환은 하지 않는다.** 사용자가 수동으로 수행한다.

> Skip 조건: 없음 (필수 Phase)
