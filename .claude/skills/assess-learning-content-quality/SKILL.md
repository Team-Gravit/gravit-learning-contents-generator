---
name: assess-learning-content-quality
description: 한 번의 파이프라인 실행에서 생성된 레슨들을 종합 채점하고, 감점을 스펙 파일에 귀인해 개선안을 넘버링으로 제안한다. 사용자가 번호로 고른 제안만 스펙에 반영한다. /assess-learning-content-quality 호출 시 트리거.
allowed-tools: Read, Write, Edit, Glob, Bash
---

## assess-learning-content-quality

생성된 학습 콘텐츠의 품질을 사후 회고하고, **반복되는 약점을 생성기 스펙에 반영해 다음 생성부터** 품질을 끌어올리는 메타 개선 도구다. 개별 레슨의 문제를 재생성하는 **Phase 5(콘텐츠 교정)** 와 달리, 이 스킬은 **스펙 파일(생성기의 규칙)** 을 고친다.

### 참조 파일
- `.claude/spec/review/deduction-attribution.md` — 종합 점수 산식·감점 신호·귀인 맵·체계적 판정·제안 작성 규칙 (이 스킬의 채점/귀인 SoT)
- `.claude/spec/review/review-rubric.md` — R1~R6 의미 (필요 시)

귀인이 가리키는 생성 스펙(제안·적용 시 Read):
- `.claude/spec/generation/learning-content-rules.md`
- `.claude/spec/generation/learning-content-writing-style.md`
- `.claude/spec/generation/problem-good-patterns.md`
- `.claude/spec/generation/problem-antipatterns.md`

### 절차

1. **대상 실행 확정.**
   - 인자로 `pipeline-state-{date}-{seq}` 파일(또는 date·seq)을 받으면 그것을 대상으로 한다.
   - 인자가 없으면 `pipeline-workspace/pipeline-state-*.md`를 훑어 후보(최근 **COMPLETED** 우선)를 사용자에게 제시하고 하나를 고르게 한다.
   - 대상 pipeline-state에서 **Meta.target_units**와 각 유닛의 `review.md` 경로(`pipeline-workspace/review-output/{date}/{unit_id}/review.md`)를 수집한다.
   - `review.md`가 없는 유닛은 "검수 전"으로 분류해 대상에서 제외하고 사용자에게 알린다.

2. **채점·집계.** `deduction-attribution.md`의 **종합 점수 산식**에 따라 각 유닛의 `review.md`(R1~R6)를 레슨 종합 점수로 환산한다.
   - 레슨별 종합 점수
   - 실행 평균 · 최저 레슨
   - 감점 신호 분포 (어느 R항목/AP/S가 몇 번)

3. **귀인·약점 추출.** `deduction-attribution.md`의 **감점 신호·귀인 맵·체계적 판정**을 적용한다.
   - 감점 신호를 수집한다 (R항목 ≤ 3 또는 reject_reasons 등장, AP·S 코드 포함).
   - 각 신호를 책임 스펙 파일로 귀인한다.
   - **체계적**(레슨 내 ≥ 3문제 또는 실행 내 ≥ 50% 레슨)인 신호만 스펙 제안 대상으로 추린다.
   - 나머지(일회성)는 **"Phase 5 재시도 권장"** 목록으로 따로 둔다.

4. **보고 + 제안 출력.** 사용자에게 대화로 출력한다. **파일로 저장하지 않는다.**
   - (A) **스코어보드**: 레슨별 종합 점수 + 실행 요약 + 감점 분포.
   - (B) **일회성 약점**: "Phase 5 재시도 권장" 목록 (스펙 변경 아님).
   - (C) **넘버링된 스펙 제안**: 체계적 약점 하나당 1개. 각 제안은 `deduction-attribution.md`의 **제안 작성 규칙**(대상 파일·근거·변경 전/후·기대효과)을 따르고 1번부터 번호를 매긴다.
   - 사용자에게 **어느 번호를 반영할지** 묻고 응답을 기다린다. **이 단계에서 파일을 건드리지 않는다.**

5. **선택 적용.** 사용자가 번호를 지정하면(예: **"1, 3번"**) 그 제안에 한해서만 대상 스펙 파일을 **Edit**으로 반영한다.
   - 반영 후 무엇을·어디에 바꿨는지 요약한다(파일·섹션·요지).
   - 커밋/푸시는 하지 않는다(사용자 몫).
   - 사용자가 아무것도 고르지 않으면 적용 없이 종료한다.

### 출력
- 대화창 출력만 (스코어보드·제안). 파일 산출물 없음.
- 사용자가 고른 제안에 한해 `.claude/spec/generation/*` 스펙 파일 수정.

### 실패 처리
- 대상 pipeline-state를 못 찾거나 `review.md`가 하나도 없으면, 사용자에게 알리고 종료한다.
- `review.md` 파싱 실패(형식 불일치) 시 해당 유닛만 건너뛰고 나머지로 진행하며, 건너뛴 유닛을 보고한다.
