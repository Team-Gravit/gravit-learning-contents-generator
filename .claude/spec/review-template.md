# 검수 출력 템플릿

채점 기준은 `.claude/spec/review-rubric.md` 참조.

---

## 레슨 단위

| 항목 | 값 |
|---|---|
| R6 | `<1~5 정수>` |
| verdict | `PASS` \| `REJECT` |
| reject_reason | `<사유 문자열>` \| `null` |
| improvement_direction | `<방향 문자열>` \| `null` |

---

## 문제 단위

문제마다 아래 블록을 반복한다.

| 항목 | 값 |
|---|---|
| problem_ref | `p1` ~ `p6` |
| problem_type | `OBJECTIVE` \| `SUBJECTIVE` |
| avg | `<소수점 둘째 자리>` |
| verdict | `PASS` \| `REJECT` |

### 점수

| R1 | R2 (객관식만) | R3 | R4 | R5 |
|---|---|---|---|---|
| `<1~5>` | `<1~5>` \| `-` | `<1~5>` | `<1~5>` | `<1~5>` |

### reject_reasons

항목별 사유를 기록한다. PASS이면 생략(null).

| 키 | 사유 |
|---|---|
| `<R코드 또는 avg>` | `<사유 문자열>` |

### improvement_direction

항목별 개선 방향을 기록한다. PASS이면 생략(null).

| 키 | 방향 |
|---|---|
| `<R코드>` | `<방향 문자열>` |

---

## 규칙

- `reject_reasons`·`improvement_direction`은 **항목별 구조화 객체**. generator 재호출 시 프롬프트에 항목별로 삽입 가능해야 한다.
- 평균 기준 미달 같은 합산 사유는 `avg` 키에 담는다.
- PASS 문제는 `reject_reasons`·`improvement_direction`을 null로 둔다.