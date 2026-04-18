#!/usr/bin/env python3
# lesson.sql 구조 카운트 검증.
#   - problem_staging: OBJECTIVE 4 + SUBJECTIVE 2
#   - option_staging:  각 OBJECTIVE problem_id당 선지 4 / is_answer=true 1
#   - answer_staging:  각 SUBJECTIVE problem_id당 answer 1
#
# 사용법: validate-lesson-structure.py <lesson.sql>
# exit: 0 통과 / 1 검증 실패 / 2 인자·파일 오류
#
# SQL 무결성(순서/FK/블록/ID 연속성)은 validate-lesson-sql.py에서 별도 검증.

import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

# ------------------------------------------------------------
# SQL 파싱 (validate-lesson-sql.py에 동일 코드. 수정 시 양쪽 동기화 필수.)
# ------------------------------------------------------------

_INSERT_HEAD = re.compile(
    r"INSERT\s+INTO\s+(\w+)\s*\([^)]*\)\s*VALUES\s*",
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class _ParsedLesson:
    insert_order: list[str] = field(default_factory=list)
    table_block_counts: dict[str, int] = field(default_factory=dict)
    lesson_rows: list[list[str]] = field(default_factory=list)
    problem_rows: list[list[str]] = field(default_factory=list)
    option_rows: list[list[str]] = field(default_factory=list)
    answer_rows: list[list[str]] = field(default_factory=list)


def _parse_inserts(sql: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    pos = 0
    while pos < len(sql):
        m = _INSERT_HEAD.search(sql, pos)
        if not m:
            break
        table = m.group(1).lower()
        i = m.end()
        body_start = i
        in_str = False
        while i < len(sql):
            ch = sql[i]
            if ch == "'":
                if in_str and i + 1 < len(sql) and sql[i + 1] == "'":
                    i += 2
                    continue
                in_str = not in_str
            elif ch == ";" and not in_str:
                break
            i += 1
        out.append((table, sql[body_start:i]))
        pos = i + 1
    return out


def _iter_outside_strings(body: str):
    # 문자열 리터럴(이스케이프 '' 포함) 바깥의 (index, char)만 생성.
    i, in_str = 0, False
    while i < len(body):
        ch = body[i]
        if ch == "'":
            if in_str and i + 1 < len(body) and body[i + 1] == "'":
                i += 2
                continue
            in_str = not in_str
            i += 1
            continue
        if not in_str:
            yield i, ch
        i += 1


def _split_value_tuples(body: str) -> list[str]:
    tuples, depth, start = [], 0, None
    for i, ch in _iter_outside_strings(body):
        if ch == "(":
            if depth == 0:
                start = i + 1
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and start is not None:
                tuples.append(body[start:i])
                start = None
    return tuples


def _split_fields(row: str) -> list[str]:
    if not row:
        return []
    fields_: list[str] = []
    last = 0
    for i, ch in _iter_outside_strings(row):
        if ch == ",":
            fields_.append(row[last:i].strip())
            last = i + 1
    if last < len(row):
        fields_.append(row[last:].strip())
    return fields_


def _unquote(value: str) -> str:
    v = value.strip()
    if len(v) >= 2 and v[0] == "'" and v[-1] == "'":
        return v[1:-1]
    return v


def _to_int(value: str) -> int | None:
    try:
        return int(value.strip())
    except ValueError:
        return None


def _parse_lesson_sql(path: str | Path) -> _ParsedLesson:
    sql = Path(path).read_text(encoding="utf-8")
    parsed = _ParsedLesson()
    rows_by_table = {
        "lesson_staging": parsed.lesson_rows,
        "problem_staging": parsed.problem_rows,
        "option_staging": parsed.option_rows,
        "answer_staging": parsed.answer_rows,
    }
    for table, body in _parse_inserts(sql):
        parsed.insert_order.append(table)
        parsed.table_block_counts[table] = parsed.table_block_counts.get(table, 0) + 1
        target = rows_by_table.get(table)
        if target is None:
            continue
        for tup in _split_value_tuples(body):
            target.append(_split_fields(tup))
    return parsed


# ------------------------------------------------------------
# 구조 검증
# ------------------------------------------------------------


def collect_problems(parsed: _ParsedLesson, errors: list[str]) -> list[tuple[int | None, str]]:
    out: list[tuple[int | None, str]] = []
    for row in parsed.problem_rows:
        if len(row) < 5:
            errors.append("problem_staging row 필드 부족 (<5)")
            continue
        out.append((_to_int(row[0]), _unquote(row[4])))
    return out


def check_type_counts(problems: list[tuple[int | None, str]], errors: list[str]) -> None:
    counts = Counter(t for _, t in problems)
    if counts.get("OBJECTIVE", 0) != 4:
        errors.append(f"OBJECTIVE 문제 개수: expected 4, got {counts.get('OBJECTIVE', 0)}")
    if counts.get("SUBJECTIVE", 0) != 2:
        errors.append(f"SUBJECTIVE 문제 개수: expected 2, got {counts.get('SUBJECTIVE', 0)}")


def collect_options_by_obj(
    parsed: _ParsedLesson, obj_ids: set[int], errors: list[str]
) -> dict[int, list[str]]:
    opt_by_pid: dict[int, list[str]] = {}
    for row in parsed.option_rows:
        if len(row) < 6:
            errors.append("option_staging row 필드 부족 (<6)")
            continue
        pid = _to_int(row[1])
        if pid is not None and pid in obj_ids:
            opt_by_pid.setdefault(pid, []).append(row[4].lower().strip())
    return opt_by_pid


def check_option_counts(
    obj_ids: set[int], opt_by_pid: dict[int, list[str]], errors: list[str]
) -> None:
    for pid in sorted(obj_ids):
        opts = opt_by_pid.get(pid, [])
        if len(opts) != 4:
            errors.append(f"OBJECTIVE problem_id={pid} 선지 개수: expected 4, got {len(opts)}")
        true_count = sum(1 for a in opts if a == "true")
        if true_count != 1:
            errors.append(
                f"OBJECTIVE problem_id={pid} is_answer=true 개수: expected 1, got {true_count}"
            )


def check_answer_counts(
    parsed: _ParsedLesson, subj_ids: set[int], errors: list[str]
) -> None:
    ans_by_pid: Counter[int] = Counter()
    for row in parsed.answer_rows:
        if len(row) < 5:
            errors.append("answer_staging row 필드 부족 (<5)")
            continue
        pid = _to_int(row[1])
        if pid is not None and pid in subj_ids:
            ans_by_pid[pid] += 1
    for pid in sorted(subj_ids):
        c = ans_by_pid.get(pid, 0)
        if c != 1:
            errors.append(f"SUBJECTIVE problem_id={pid} answer 개수: expected 1, got {c}")


def run_checks(parsed: _ParsedLesson) -> list[str]:
    errors: list[str] = []
    problems = collect_problems(parsed, errors)
    check_type_counts(problems, errors)
    obj_ids = {pid for pid, t in problems if t == "OBJECTIVE" and pid is not None}
    subj_ids = {pid for pid, t in problems if t == "SUBJECTIVE" and pid is not None}
    opt_by_pid = collect_options_by_obj(parsed, obj_ids, errors)
    check_option_counts(obj_ids, opt_by_pid, errors)
    check_answer_counts(parsed, subj_ids, errors)
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <lesson.sql>", file=sys.stderr)
        return 2
    try:
        parsed = _parse_lesson_sql(sys.argv[1])
    except OSError as e:
        print(f"cannot read {sys.argv[1]}: {e}", file=sys.stderr)
        return 2

    errors = run_checks(parsed)
    if errors:
        print("[FAIL] validate-lesson-structure", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("[OK] validate-lesson-structure")
    return 0


if __name__ == "__main__":
    sys.exit(main())