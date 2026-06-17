---
description: 학습 콘텐츠 생성 시 lesson/problem/option/answer ID 부여 규칙.
---

## ID 관리 규칙

### 원칙

Phase 2에서 **fetch-max-id** 스킬로 MAX ID를 확인하고 pipeline-state에 기록하라. 매 작업 시작 시 반드시 fetch하라. 캐시된 값을 재사용하지 마라.

- baseline은 **prod 테이블과 _staging 테이블의 통합 MAX**(GREATEST)다. prod만 보면 아직 promote되지 않은 staging의 남은 배치와 ID가 겹쳐 저장 시 PK 충돌이 난다.
- 파이프라인이 부여한 staging ID는 prod로 그대로 옮겨지지 않는다. promote API가 prod 시퀀스로 새 ID를 부여해 리매핑하므로, 여기서 지켜야 할 제약은 **staging 테이블 안에서의 PK 유일성**이다.

### pipeline-state 기록 형식

```markdown
## ID Baseline
- last_lesson_id: 82
- last_problem_id: 532
- last_option_id: 1466
- last_answer_id: 164
- last_label_id: 12
```

### 부여 규칙

- 신규 ID는 baseline + 1부터 순차 부여하라
- lesson → problem → option → answer 순서로 할당하라
- 서브에이전트는 메인 세션이 전달한 ID Baseline만 사용하라. 임의로 DB를 조회하지 마라

### Lesson 1개당 ID 소비량

| 테이블        | 소비 개수 | 근거                                       |
|---------------|-----------|--------------------------------------------|
| lesson        | 1         | lesson 본체                                |
| problem       | 6         | OBJECTIVE 4 + SUBJECTIVE 2                 |
| option        | 16        | OBJECTIVE 4개 × 선지 4개 (SUBJECTIVE 제외) |
| answer        | 2         | SUBJECTIVE 2개 × 1개씩 (OBJECTIVE 제외)    |
| staging_label | 1         | 유닛(=lesson) 1개당 라벨 1개               |

위 수량의 SoT는 `generation-contract.md` §0의 구성 규칙(OBJECTIVE 4 + SUBJECTIVE 2, 선지 4개)이다. 구성이 바뀌면 그 문서를 먼저 고치고 이 표를 맞춘다.

멀티 유닛 실행 시 skill은 이 수량을 기준으로 유닛 순서대로 ID 범위를 잘라 서브에이전트에 배정한다.
