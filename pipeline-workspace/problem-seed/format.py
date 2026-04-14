"""
problem-seed SQL 파일 포맷터

수행 작업:
  1. 멀티라인 VALUES 행 → 한 줄로
  2. Lesson 구분자 → -- Lesson N (id = X) 한 줄로
     - data-structure 형식: -- =+\n-- Lesson N\n-- =+
     - algorithm 형식:      -- =+\n-- Lesson {id}: {title}\n-- =+
     - operating-system 형식: -- ===== Lesson N: title =====
  3. 1번 라인 ↔ 2번 라인 교체 (Unit이 먼저인 경우에만)
  4. Lesson 주석과 INSERT 사이 빈 줄 제거
  [database 전처리]
  5. 헤더 형식 변환: -- Unit N: title / -- ===...=== → 표준 헤더
  6. Lesson 구분자: -- Lesson N: title (ID: X) → -- Lesson N (id = X)
  7. INSERT INTO lesson 컬럼 순서 정규화: (id, title, unit_id) → (id, unit_id, title)
  8. -- 문제 XXX 주석 제거
  9. VALUES가 단독 줄인 option/problem 블록 → 표준 형식
  10. 개별 INSERT INTO lesson → 하나로 통합 (파일 상단)
  11. INSERT INTO option 내 rows를 problem_id별로 묶고 그룹 사이 빈 줄 추가
  [operating-system 전처리]
  12. VALUES 단독 줄 + 들여쓰기 없는 행 + -- 문제 주석 → 표준 형식 (빈 줄 그룹 보존)

사용법:
  python3 format.py                    # 모든 디렉토리 처리
  python3 format.py data-structure     # 특정 디렉토리만
  python3 format.py algorithm
  python3 format.py database
  python3 format.py operating-system
"""

import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DIRS = {
    'data-structure':   os.path.join(BASE, 'data-structure'),
    'algorithm':        os.path.join(BASE, 'algorithm'),
    'network':          os.path.join(BASE, 'network'),
    'database':         os.path.join(BASE, 'database'),
    'operating-system': os.path.join(BASE, 'operating-system'),
}


def collapse_multiline_values(content):
    """멀티라인 VALUES 행 → 한 줄"""
    lines = content.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        is_new_row = line.startswith('VALUES (') or line.startswith('       (')
        if is_new_row:
            accumulated = line.rstrip()
            while i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.startswith('        ') and not next_line.startswith('       ('):
                    accumulated += ' ' + next_line.strip()
                    i += 1
                else:
                    break
            result.append(accumulated)
        else:
            result.append(line)
        i += 1
    return '\n'.join(result)


def simplify_lesson_separators(content):
    """Lesson 구분자 → -- Lesson N (id = X)"""
    # 레슨 ID 목록 추출
    cutoff = content.index('INSERT INTO problem') if 'INSERT INTO problem' in content else len(content)
    lesson_section = content[:cutoff]
    ids = re.findall(r'VALUES\s*\((\d+),\s*\d+,\s*\'[^\']+\'\)', lesson_section)
    ids += re.findall(r'\n\s+\((\d+),\s*\d+,\s*\'[^\']+\'\)', lesson_section)
    lesson_ids = sorted(set(ids), key=lambda x: int(x))

    # data-structure 형식: 3줄 구분자
    matches_ds = list(re.finditer(r'-- =+\n-- Lesson (\d+)\n-- =+', content))
    if matches_ds:
        idx_map = {m.start(): (pos + 1, lesson_ids[pos]) for pos, m in enumerate(matches_ds) if pos < len(lesson_ids)}
        def rep_ds(m):
            pos, lid = idx_map.get(m.start(), (m.group(1), m.group(1)))
            return f'-- Lesson {pos} (id = {lid})'
        content = re.sub(r'-- =+\n-- Lesson (\d+)\n-- =+', rep_ds, content)

    # algorithm 형식: 3줄 구분자 + title
    matches_al = list(re.finditer(r'-- =+\n-- Lesson (\d+): [^\n]+\n-- =+', content))
    if matches_al:
        idx_map = {m.start(): (pos + 1, m.group(1)) for pos, m in enumerate(matches_al)}
        def rep_al(m):
            pos, lid = idx_map.get(m.start(), (1, m.group(1)))
            return f'-- Lesson {pos} (id = {lid})'
        content = re.sub(r'-- =+\n-- Lesson (\d+): [^\n]+\n-- =+', rep_al, content)

    # operating-system 형식: -- ===== Lesson N: title =====
    matches_os = list(re.finditer(r'-- =+ Lesson (\d+): [^\n]+ =+', content))
    if matches_os:
        idx_map = {m.start(): (pos + 1, lesson_ids[pos]) for pos, m in enumerate(matches_os) if pos < len(lesson_ids)}
        def rep_os(m):
            pos, lid = idx_map.get(m.start(), (int(m.group(1)), m.group(1)))
            return f'-- Lesson {pos} (id = {lid})'
        content = re.sub(r'-- =+ Lesson (\d+): [^\n]+ =+', rep_os, content)

    return content


def swap_lines_1_2(content):
    """1번 라인 ↔ 2번 라인 교체 (Unit이 먼저인 경우에만)"""
    lines = content.split('\n')
    if len(lines) >= 2 and lines[0].startswith('-- Unit:') and lines[1].startswith('-- Chapter:'):
        lines[0], lines[1] = lines[1], lines[0]
    return '\n'.join(lines)


def remove_blank_after_lesson(content):
    """Lesson 주석과 INSERT 사이 빈 줄 제거"""
    return re.sub(r'(-- Lesson \d+ \(id = \d+\))\n\n(INSERT)', r'\1\n\2', content)


def consolidate_lesson_inserts(content):
    """개별 INSERT INTO lesson → 하나로 통합하여 파일 상단에 배치"""
    pattern = re.compile(
        r'INSERT INTO lesson \(id, unit_id, title\)\nVALUES \((\d+), (\d+), \'([^\']*)\'\);\n?'
    )
    matches = list(pattern.finditer(content))

    if len(matches) <= 1:
        return content

    rows = [(int(m.group(1)), int(m.group(2)), m.group(3)) for m in matches]
    content = pattern.sub('', content)

    row_strs = [f"({r[0]}, {r[1]}, '{r[2]}')" for r in rows]
    values_part = 'VALUES ' + row_strs[0]
    for rs in row_strs[1:]:
        values_part += f',\n       {rs}'
    consolidated = f'-- Lesson 생성\nINSERT INTO lesson (id, unit_id, title)\n{values_part};'

    lines = content.split('\n')
    pos = 2
    while pos < len(lines) and lines[pos] == '':
        pos += 1
    lines.insert(pos, '')
    lines.insert(pos, consolidated)

    return '\n'.join(lines)


def group_options_by_problem(content):
    """INSERT INTO option 내 rows를 problem_id별로 묶고 그룹 사이에 빈 줄 추가"""
    lines = content.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('INSERT INTO option'):
            result.append(line)
            i += 1

            raw_rows = []
            while i < len(lines):
                l = lines[i]
                if l.startswith('VALUES (') or l.startswith('       ('):
                    row = l.strip()
                    if row.startswith('VALUES '):
                        row = row[7:]
                    row = re.sub(r'[,;]$', '', row)
                    raw_rows.append(row)
                    i += 1
                elif l == '':
                    i += 1
                else:
                    break

            groups = []
            current_group = []
            current_prob = None
            for row in raw_rows:
                m = re.match(r'\((\d+),\s*(\d+),', row)
                prob_id = m.group(2) if m else current_prob
                if prob_id != current_prob:
                    if current_group:
                        groups.append(current_group)
                    current_group = [row]
                    current_prob = prob_id
                else:
                    current_group.append(row)
            if current_group:
                groups.append(current_group)

            total_rows = sum(len(g) for g in groups)
            row_counter = 0
            is_first_overall = True

            for gi, group in enumerate(groups):
                for row in group:
                    row_counter += 1
                    is_last = (row_counter == total_rows)
                    suffix = ';' if is_last else ','
                    prefix = 'VALUES ' if is_first_overall else '       '
                    result.append(f'{prefix}{row}{suffix}')
                    is_first_overall = False
                if gi < len(groups) - 1:
                    result.append('')
        else:
            result.append(line)
            i += 1

    return '\n'.join(result)


def preprocess_database(content):
    """database 디렉토리 전용 전처리"""

    # 1. 헤더: -- Unit 42: title\n-- ===...=== → 표준 헤더
    content = re.sub(
        r'-- Unit (\d+): ([^\n]+)\n-- =+',
        lambda m: f'-- Unit: {m.group(2)} (Unit ID: {m.group(1)})\n-- Chapter: 데이터베이스 (Chapter ID: 4)',
        content
    )

    # 2. Lesson 구분자: -- Lesson N: title (ID: X) → -- Lesson N (id = X)
    content = re.sub(
        r'-- Lesson (\d+): [^\n]+\(ID: (\d+)\)',
        lambda m: f'-- Lesson {m.group(1)} (id = {m.group(2)})',
        content
    )

    # 3. INSERT INTO lesson 컬럼 순서 정규화
    content = content.replace(
        'INSERT INTO lesson (id, title, unit_id)',
        'INSERT INTO lesson (id, unit_id, title)'
    )
    content = re.sub(
        r"VALUES \((\d+), '([^']+)', (\d+)\);",
        lambda m: f"VALUES ({m.group(1)}, {m.group(3)}, '{m.group(2)}');",
        content
    )

    # 4. -- 문제 XXX 주석 제거
    content = re.sub(r'-- 문제 \d+\n', '', content)

    # 5. VALUES가 단독 줄인 블록(problem/option) → 표준 형식
    lines = content.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        is_insert = line.startswith('INSERT INTO option') or line.startswith('INSERT INTO problem')
        next_is_values_only = (i + 1 < len(lines) and lines[i + 1].strip() == 'VALUES')

        if is_insert and next_is_values_only:
            result.append(line)
            i += 2

            rows = []
            while i < len(lines):
                row_line = lines[i]
                if not row_line.strip() or row_line.strip().startswith('--'):
                    i += 1
                    continue
                row = row_line.strip()
                while not (row.endswith('),') or row.endswith(');')):
                    i += 1
                    if i < len(lines):
                        row += ' ' + lines[i].strip()
                    else:
                        break
                rows.append(row)
                is_last = row.endswith(');')
                i += 1
                if is_last:
                    break

            for j, row in enumerate(rows):
                prefix = 'VALUES ' if j == 0 else '       '
                result.append(prefix + row)
        else:
            result.append(line)
            i += 1

    content = '\n'.join(result)

    # 6. 개별 INSERT INTO lesson → 하나로 통합
    content = consolidate_lesson_inserts(content)

    # 7. option rows를 problem_id별로 그룹화
    content = group_options_by_problem(content)

    return content


def preprocess_operating_system(content):
    """operating-system 디렉토리 전용 전처리

    처리 대상:
      - VALUES 단독 줄 + 들여쓰기 없는 행 + -- 문제 주석 혼재 블록
      - 기존 그룹 사이 빈 줄은 그대로 유지
    """
    lines = content.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        is_insert = line.startswith('INSERT INTO option') or line.startswith('INSERT INTO problem')
        next_is_values_only = (i + 1 < len(lines) and lines[i + 1].strip() == 'VALUES')

        if is_insert and next_is_values_only:
            result.append(line)
            i += 2  # INSERT 줄 추가, VALUES 단독 줄 스킵

            # 행/빈줄 수집 (-- 주석만 제거, 빈 줄은 보존)
            items = []  # ('row', str) or ('blank', '')
            while i < len(lines):
                l = lines[i]
                stripped = l.strip()

                if stripped.startswith('--'):
                    i += 1
                    continue

                if stripped == '':
                    items.append(('blank', ''))
                    i += 1
                    continue

                # 행 수집 (멀티라인 처리)
                row = stripped
                while not (row.endswith('),') or row.endswith(');')):
                    i += 1
                    if i < len(lines):
                        row += ' ' + lines[i].strip()
                    else:
                        break
                items.append(('row', row))
                is_last = row.endswith(');')
                i += 1
                if is_last:
                    break

            # 선행/후행 빈 줄 제거
            while items and items[0][0] == 'blank':
                items.pop(0)
            while items and items[-1][0] == 'blank':
                items.pop()

            # 총 data 행 수
            total_rows = sum(1 for kind, _ in items if kind == 'row')
            row_counter = 0
            is_first_overall = True

            for kind, data in items:
                if kind == 'blank':
                    result.append('')
                else:
                    row_counter += 1
                    is_last = (row_counter == total_rows)
                    # 끝 , ; 제거 후 새 suffix
                    row = re.sub(r'[,;]$', '', data)
                    suffix = ';' if is_last else ','
                    prefix = 'VALUES ' if is_first_overall else '       '
                    result.append(f'{prefix}{row}{suffix}')
                    is_first_overall = False
        else:
            result.append(line)
            i += 1

    content = '\n'.join(result)

    # 연속 빈 줄 2개 이상 → 1개로
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content


def format_file(filepath, dir_key=''):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if dir_key == 'database':
        content = preprocess_database(content)
    elif dir_key == 'operating-system':
        content = preprocess_operating_system(content)

    content = collapse_multiline_values(content)
    content = simplify_lesson_separators(content)
    content = swap_lines_1_2(content)
    content = remove_blank_after_lesson(content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  formatted: {os.path.basename(filepath)}")


def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(DIRS.keys())
    for key in targets:
        d = DIRS.get(key)
        if not d or not os.path.isdir(d):
            print(f"[skip] {key} 디렉토리 없음")
            continue
        print(f"[{key}]")
        for fname in sorted(os.listdir(d)):
            if fname.endswith('.sql'):
                format_file(os.path.join(d, fname), dir_key=key)


if __name__ == '__main__':
    main()
