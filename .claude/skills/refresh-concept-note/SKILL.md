---
name: refresh-concept-note
description: 지정된 유닛의 개념노트를 Gravit API에서 받아 pipeline-workspace/concept-notes/에 저장하고, 신규·변경·동일·실패 유닛을 요약해 반환한다.
allowed-tools: Bash
---

## refresh-concept-note

개념노트는 거의 바뀌지 않는다. 그래서 유닛마다 `pipeline-workspace/concept-notes/{unit_id}.md` 한 장만 저장해 두고 계속 쓰며, 최신화가 필요할 때만 이 스킬로 다시 받는다.

받은 본문은 파일에 바로 쓰고 표준 출력으로 내보내지 않는다. 본문이 모델 컨텍스트를 거치지 않게 하기 위해서다.

### 입력
- **unit_ids** (필수) — 아래 둘 중 하나.
  - 유닛 ID 목록: 공백으로 구분한 정수 (예: **12 13**)
  - **all**: `pipeline-workspace/concept-notes/`에 저장된 모든 유닛

### 출력
- `pipeline-workspace/concept-notes/{unit_id}.md`
  - 받기에 성공한 유닛은 파일 수정일이 실행 시각으로 바뀐다. 파일 수정일이 곧 마지막 최신화일이다.
- 표준 출력: 결과별 유닛 ID 목록.
  ```
  new: {처음 저장한 유닛}
  changed: {내용이 바뀐 유닛}
  unchanged: {내용이 같은 유닛}
  failed: {받기에 실패한 유닛}
  ```

### 절차
Phase 1~4의 명령은 변수를 이어 쓰므로 하나로 이어 붙여 한 번의 Bash 호출로 실행한다.

#### Phase 1. GRAVIT_API_BASE_URL 로드
```
set -a && . ./.env && set +a
[ -z "$GRAVIT_API_BASE_URL" ] && { echo "GRAVIT_API_BASE_URL missing" >&2; exit 1; }
```

#### Phase 2. 대상 유닛 확정
`{unit_ids}`는 입력값 그대로 치환한다. **all**이면 저장된 파일 이름에서 유닛 ID를 모은다.
```
dir=pipeline-workspace/concept-notes
mkdir -p "$dir"
set -- {unit_ids}
[ "$1" = all ] && set -- $(ls "$dir" | sed -n 's/^\([0-9][0-9]*\)\.md$/\1/p' | sort -n)
```

#### Phase 3. 받아서 비교 후 저장
받은 내용을 임시 파일에 쓰고 저장된 파일과 비교한다.
- 저장된 파일이 없음 → 저장 (**new**)
- 내용이 다름 → 교체 (**changed**)
- 내용이 같음 → 임시 파일은 지우고, 저장된 파일의 수정일만 갱신 (**unchanged**)

```
new=; changed=; unchanged=; failed=
for u in "$@"; do
  tmp="$dir/.$u.tmp"
  if ! curl -fsS "${GRAVIT_API_BASE_URL}/cs-notes/$u" -H 'accept: text/markdown' -o "$tmp" || [ ! -s "$tmp" ]; then
    rm -f "$tmp"; failed="$failed $u"; continue
  fi
  if [ ! -f "$dir/$u.md" ]; then mv "$tmp" "$dir/$u.md"; new="$new $u"
  elif cmp -s "$tmp" "$dir/$u.md"; then rm "$tmp"; touch "$dir/$u.md"; unchanged="$unchanged $u"
  else mv "$tmp" "$dir/$u.md"; changed="$changed $u"
  fi
done
```

#### Phase 4. 결과 출력
```
printf 'new:%s\nchanged:%s\nunchanged:%s\nfailed:%s\n' "$new" "$changed" "$unchanged" "$failed"
[ -z "$failed" ]
```

### 실패 처리
- `.env` 또는 **GRAVIT_API_BASE_URL** 누락 → 즉시 중단.
- curl 실패 또는 빈 응답 → 그 유닛의 저장된 파일은 건드리지 않고 **failed**에 넣은 뒤 다음 유닛을 계속한다. curl의 stderr는 그대로 노출한다.
- **failed**가 하나라도 있으면 종료 코드 1로 끝난다. 자체 재시도 없음.
