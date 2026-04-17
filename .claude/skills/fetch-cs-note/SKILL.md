---
name: fetch-cs-note
description: 지정된 유닛의 개념노트를 Gravit API에서 markdown으로 조회하여 표준 출력으로 반환한다.
allowed-tools: Bash
---

# fetch-cs-note
Gravit API(`{GRAVIT_API_BASE_URL}/cs-notes/{unit_id}`)에서 해당 유닛의 개념노트를 markdown으로 조회하여 반환한다. 호출자(Phase 2)가 반환된 내용을 `pipeline-workspace/fetch-cache/{오늘 날짜}/{unit_id}/concept-note.md`로 저장한다.

## 입력
- `unit_id` (int, 필수) — 조회 대상 유닛 ID.

## 출력
- 표준 출력: API가 반환한 markdown 본문.

## 절차

### Phase 1. API 호출
다음 명령을 실행하고 응답 본문을 그대로 표준 출력으로 내보낸다.

```
curl -fsS -X GET "${GRAVIT_API_BASE_URL}/cs-notes/{unit_id}" \
  -H 'accept: text/markdown'
```

- `-f`: HTTP 비-2xx 응답 시 비정상 종료(호출자가 실패를 감지할 수 있게)
- `-s`: 진행률 등 부가 출력 억제
- `-S`: `-s`와 함께 사용 시에도 에러 메시지는 stderr로 출력

## 실패 처리
- `.env` 또는 `GRAVIT_API_BASE_URL` 누락 시 즉시 중단, 호출자에게 보고.
- curl 실패(비-2xx, 네트워크 오류 등) 시 호출자에게 에러 메시지와 종료 코드를 그대로 노출한다. 자체 재시도는 하지 않는다(호출자 Phase 2가 최대 3회 재시도).