---
name: open-pr
description: |
  PR을 생성한다. PULL_REQUEST_TEMPLATE.md 규격에 맞춰 본문을 작성하고 gh pr create를 실행한다.
  Trigger: "PR 날려줘", "PR 만들어줘", "PR 생성해줘", "PR 올려줘"
  Do NOT use for: 커밋 생성(직접 git commit), 브랜치 생성, 코드 리뷰
  Boundary: PR 생성까지만 수행한다. 머지, 리뷰 요청, 라벨 설정은 범위 밖이다.
allowed-tools: Bash(git *), Bash(gh *), Read
---

# PR 생성

대상 브랜치: $ARGUMENTS (비어있으면 main)

## Phase 1: 현재 브랜치 및 변경 사항 파악

1. `git branch --show-current`로 현재 브랜치명을 확인하라
2. 브랜치명에서 이슈 번호를 추출하라 (형식: `{type}/{이슈번호}-{설명}`)
   - 예: `feat/123-bookmark` → 이슈 번호 `123`
   - 이슈 번호가 없으면 사용자에게 물어보라
3. `git log main..HEAD --oneline` (또는 $ARGUMENTS..HEAD)으로 이 브랜치의 커밋 목록을 확인하라
4. `git diff main...HEAD --stat`으로 변경된 파일 목록을 파악하라

> 다음 Phase 조건: 이슈 번호와 변경 사항이 파악되었을 때

> Skip 조건: 없음 (필수 Phase)

## Phase 2: PR 제목 및 본문 작성

1. `.github/PULL_REQUEST_TEMPLATE.md`를 Read로 읽어 템플릿 구조를 확인하라
2. `.claude/rules/git-convention.md`를 Read로 읽어 커밋 타입과 네이밍 규칙을 확인하라
3. 아래 템플릿에 맞춰 PR 본문을 작성하라:

```
### 1. 연관 이슈

---
 - close #{이슈번호}

<br>

### 2. 구현 사항

---
**{구현 사항 제목}**

{변경된 파일과 커밋을 바탕으로 구현 내용을 구체적으로 설명. 왜 변경했는지, 어떻게 동작하는지 포함}
```

   - 구현 사항이 여러 개면 `**구현 사항 1**`, `**구현 사항 2**` 형태로 분리하라
   - 커밋 메시지를 그대로 복사하지 말고, 변경 내용을 이해한 뒤 설명하라

4. PR 제목은 git-convention.md의 커밋 메시지 형식을 따라라: `{type}: {설명}(#{이슈번호})`

> 다음 Phase 조건: 제목과 본문이 완성되었을 때

> Skip 조건: 없음 (필수 Phase)

## Phase 3: PR 생성

1. 대상 브랜치를 결정하라:
   - $ARGUMENTS가 있으면 해당 브랜치로
   - 없으면 `main`으로
2. 현재 브랜치가 원격에 push되어 있는지 `git status`로 확인하라
   - push되지 않았으면 사용자에게 알리고 중단하라
3. 다음 명령으로 PR을 생성하라:
   ```bash
   gh pr create --title "{제목}" --body "{본문}" --base {대상 브랜치}
   ```
4. 생성된 PR URL을 사용자에게 보고하라

> Skip 조건: 없음 (필수 Phase)
