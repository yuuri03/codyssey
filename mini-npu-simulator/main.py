"""Mini NPU 시뮬레이터.

입력 패턴과 필터를 같은 자리끼리 곱해 모두 더하는 MAC 연산으로
십자가(Cross)와 X 중 어느 쪽에 가까운지 판별한다.
`python main.py` 로 실행한다.
"""

import json
import os
import time

TITLE = "Mini NPU 시뮬레이터"

# 필터와 패턴이 들어 있는 데이터 파일.
# 어느 위치에서 실행하든 프로젝트 루트를 가리키도록
# 이 소스 파일이 있는 디렉터리를 기준으로 경로를 만든다.
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

MENU_ITEMS = {
    1: "사용자 입력 (3x3)",
    2: "data.json 분석",
}

# 프로그램 안에서 쓰는 표준 라벨. 파일에 적힌 '+' 나 'cross' 는 모두 이 두 가지로 바꾼다.
CROSS = "Cross"
X = "X"
UNDECIDED = "UNDECIDED"

# 두 점수의 차이가 이 값보다 작으면 동점으로 본다.
# 0.1 처럼 2진수로 딱 떨어지지 않는 값을 여러 번 더하면 마지막 자리가 어긋나는데,
# 그 정도 오차로 승패를 가르지 않기 위한 기준이다.
EPSILON = 1e-9

# 성능 측정 반복 횟수. 과제 기준은 10회이며,
# 보너스 비교표는 3x3 처럼 작은 크기에서 시간이 너무 짧아 잡음이 커서 더 많이 반복한다.
REPEAT = 10
BONUS_REPEAT = 1000

# 위 측정을 몇 번 되풀이해 가장 빠른 회차를 쓸지. 측정값이 튀는 것을 줄이기 위한 값이다.
ROUNDS = 5

# 성능 분석에 사용할 크기.
PERF_SIZES = (3, 5, 13, 25)

# 사용자 입력 모드에서 다루는 크기.
USER_MODE_SIZE = 3

# 파일에 적힐 수 있는 표기 -> 표준 라벨
LABEL_NAMES = {
    "+": CROSS,
    "cross": CROSS,
    "plus": CROSS,
    "x": X,
    "×": X,
}


def normalize_label(raw):
    """'+' 나 'cross' 처럼 제각각인 표기를 표준 라벨로 바꾼다.

    아는 표기가 아니면 None 을 돌려주고, 부르는 쪽에서 해당 항목만 실패로 처리한다.
    """
    if raw is None:
        return None
    return LABEL_NAMES.get(str(raw).strip().lower())


class Matrix:
    """n x n 크기의 정사각 숫자표.

    속성:
        n (int): 한 변의 길이
        rows (list[list[float]]): 실제 값이 담긴 2차원 배열
    """

    def __init__(self, n, fill=0.0):
        if n <= 0:
            raise ValueError("크기는 1 이상이어야 합니다.")
        self.n = n
        self.rows = [[float(fill)] * n for _ in range(n)]

    @classmethod
    def from_rows(cls, rows):
        """2차원 배열을 검사하면서 Matrix 를 만든다.

        행과 열의 개수가 다르거나 숫자가 아닌 값이 있으면 ValueError 를 일으킨다.
        """
        if not isinstance(rows, list) or not rows:
            raise ValueError("2차원 배열이 아닙니다.")

        n = len(rows)
        matrix = cls(n)
        for r, row in enumerate(rows):
            if not isinstance(row, list):
                raise ValueError(f"{r + 1}번째 행이 배열이 아닙니다.")
            if len(row) != n:
                raise ValueError(f"정사각형이 아닙니다. (행 {n}개, {r + 1}번째 행의 열 {len(row)}개)")
            for c, value in enumerate(row):
                # JSON 의 true/false 는 파이썬에서 int 로도 취급되므로 bool 을 먼저 걸러 낸다.
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise ValueError(f"숫자가 아닌 값이 있습니다. ({r}, {c}) = {value!r}")
                matrix.rows[r][c] = float(value)
        return matrix

    def get(self, r, c):
        """(r, c) 자리의 값을 읽는다."""
        return self.rows[r][c]

    def set(self, r, c, value):
        """(r, c) 자리에 값을 넣는다."""
        self.rows[r][c] = float(value)

    def to_flat(self):
        """2차원 배열을 길이 N*N 인 1차원 배열로 펼친다."""
        flat = []
        for row in self.rows:
            flat.extend(row)
        return flat


def make_cross(n):
    """n x n 십자가 패턴을 만든다. 가운데 행과 가운데 열을 1로 채운다."""
    matrix = Matrix(n)
    mid = n // 2
    for i in range(n):
        matrix.set(i, mid, 1.0)
        matrix.set(mid, i, 1.0)
    return matrix


def make_x(n):
    """n x n X 패턴을 만든다. 두 대각선을 1로 채운다."""
    matrix = Matrix(n)
    for i in range(n):
        matrix.set(i, i, 1.0)
        matrix.set(i, n - 1 - i, 1.0)
    return matrix


def mac(pattern, filt):
    """같은 자리끼리 곱해서 전부 더한 값을 돌려준다.

    곱셈은 정확히 N*N 번 일어난다.
    크기가 다르면 ValueError 를 일으킨다.
    """
    if pattern.n != filt.n:
        raise ValueError(f"크기가 다릅니다. (패턴 {pattern.n}x{pattern.n}, 필터 {filt.n}x{filt.n})")

    total = 0.0
    for r in range(pattern.n):
        # 안쪽 반복문에서 매번 행을 찾지 않도록 미리 꺼내 둔다.
        pattern_row = pattern.rows[r]
        filter_row = filt.rows[r]
        for c in range(pattern.n):
            total += pattern_row[c] * filter_row[c]
    return total


def mac_flat(flat_pattern, flat_filter):
    """1차원으로 펼친 배열끼리 MAC 연산을 한다."""
    if len(flat_pattern) != len(flat_filter):
        raise ValueError("두 배열의 길이가 다릅니다.")

    total = 0.0
    for i in range(len(flat_pattern)):
        total += flat_pattern[i] * flat_filter[i]
    return total


def measure_mac(pattern, filt, repeat=REPEAT, rounds=ROUNDS):
    """MAC 연산을 repeat 번 반복하고 (점수, 1회 평균 시간(ms)) 을 돌려준다.

    입력, 출력, 파일 읽기는 측정 구간에 넣지 않는다.
    같은 측정을 rounds 번 되풀이해 그중 가장 빠른 값을 돌려준다.
    다른 프로그램이 CPU 를 가져가면 측정값이 크게 늘어나는데,
    그렇게 방해받은 회차를 빼고 보려는 것이다.
    """
    score = 0.0
    best = None
    for _ in range(rounds):
        start = time.perf_counter()
        for _ in range(repeat):
            score = mac(pattern, filt)
        average = (time.perf_counter() - start) / repeat * 1000
        if best is None or average < best:
            best = average
    return score, best


def measure_mac_flat(flat_pattern, flat_filter, repeat=REPEAT, rounds=ROUNDS):
    """1차원 배열 버전의 (점수, 1회 평균 시간(ms)) 을 돌려준다."""
    score = 0.0
    best = None
    for _ in range(rounds):
        start = time.perf_counter()
        for _ in range(repeat):
            score = mac_flat(flat_pattern, flat_filter)
        average = (time.perf_counter() - start) / repeat * 1000
        if best is None or average < best:
            best = average
    return score, best


def decide(score_a, score_b, label_a, label_b):
    """두 점수를 비교해 이긴 쪽 라벨을 돌려준다.

    차이가 EPSILON 보다 작으면 동점으로 보고 UNDECIDED 를 돌려준다.
    """
    if abs(score_a - score_b) < EPSILON:
        return UNDECIDED
    return label_a if score_a > score_b else label_b


def show_section(number, name):
    """구분선과 함께 단계 제목을 출력한다."""
    print()
    print("=" * 40)
    print(f"  [{number}] {name}")
    print("=" * 40)


def show_perf_table(rows):
    """크기별 측정 결과를 표로 출력한다.

    rows 는 (크기 이름, 평균 시간(ms), 연산 횟수) 목록이다.
    '연산당' 은 평균 시간을 연산 횟수로 나눈 값이다.
    크기가 달라져도 이 값이 일정하면 전체 시간이 N*N 에 비례한다는 뜻이 된다.
    """
    print(f"  {'크기':<8}{'평균 시간(ms)':<14}{'연산 횟수':<10}{'연산당(ns)'}")
    print("-" * 52)
    for name, avg_ms, count in rows:
        per_op = avg_ms * 1000000 / count
        print(f"  {name:<10}{avg_ms:<18.4f}{count:<14}{per_op:.1f}")
    print("-" * 52)


def measure_sizes(sizes=PERF_SIZES):
    """크기별로 십자가 패턴과 십자가 필터의 MAC 시간을 잰다."""
    rows = []
    for n in sizes:
        pattern = make_cross(n)
        filt = make_cross(n)
        _, avg_ms = measure_mac(pattern, filt)
        rows.append((f"{n}x{n}", avg_ms, n * n))
    return rows


def show_flat_comparison(sizes=PERF_SIZES):
    """2차원 배열과 1차원 배열의 접근 속도를 비교해 출력한다."""
    print()
    print(f"  2차원 배열과 1차원 배열 비교 (평균/{BONUS_REPEAT}회)")
    print(f"  {'크기':<8}{'2차원(ms)':<16}{'1차원(ms)':<16}{'속도비'}")
    print("-" * 52)
    for n in sizes:
        pattern = make_cross(n)
        filt = make_cross(n)
        flat_pattern = pattern.to_flat()
        flat_filter = filt.to_flat()

        _, avg_2d = measure_mac(pattern, filt, BONUS_REPEAT)
        _, avg_1d = measure_mac_flat(flat_pattern, flat_filter, BONUS_REPEAT)
        ratio = avg_2d / avg_1d if avg_1d > 0 else 0

        print(f"  {f'{n}x{n}':<10}{avg_2d:<18.4f}{avg_1d:<18.4f}{ratio:.2f}배")
    print("-" * 52)


def ask_int(prompt, low, high):
    """`low` 이상 `high` 이하의 정수를 입력받아 돌려준다.

    올바른 값을 입력할 때까지 반복해서 다시 물어본다.
    """
    while True:
        answer = input(prompt).strip()

        if answer == "":
            print("[안내] 입력이 비어 있습니다. 다시 입력해 주세요.")
            continue

        try:
            number = int(answer)
        except ValueError:
            print(f"[안내] 숫자만 입력할 수 있습니다. ('{answer}' 은(는) 숫자가 아닙니다)")
            continue

        if number < low or number > high:
            print(f"[안내] {low}~{high} 사이의 숫자를 입력해 주세요.")
            continue

        return number


def ask_matrix(name, n):
    """n 줄을 공백으로 구분해 입력받아 Matrix 로 만든다.

    한 줄이라도 형식이 어긋나면 안내 후 그 표를 처음부터 다시 입력받는다.
    """
    while True:
        print(f"{name} ({n}줄, 한 줄에 {n}개씩 공백으로 구분)")

        rows = []
        for _ in range(n):
            values = input().split()

            if len(values) != n:
                print(f"[안내] 한 줄에 {n}개의 숫자를 공백으로 구분해 입력해야 합니다. (입력: {len(values)}개)")
                break

            try:
                rows.append([float(value) for value in values])
            except ValueError:
                print("[안내] 숫자만 입력할 수 있습니다.")
                break
        else:
            # 모든 줄을 정상적으로 받은 경우에만 여기까지 온다.
            return Matrix.from_rows(rows)

        print(f"[안내] {name} 을(를) 처음부터 다시 입력합니다.")
        print()


def run_user_mode():
    """3x3 필터 두 개와 패턴을 직접 입력받아 판정한다."""
    n = USER_MODE_SIZE

    show_section(1, "필터 입력")
    filter_a = ask_matrix("필터 A", n)
    print(f"[알림] 필터 A 를 저장했습니다. ({n}x{n})")
    print()
    filter_b = ask_matrix("필터 B", n)
    print(f"[알림] 필터 B 를 저장했습니다. ({n}x{n})")

    show_section(2, "패턴 입력")
    pattern = ask_matrix("패턴", n)
    print(f"[알림] 패턴을 저장했습니다. ({n}x{n})")

    show_section(3, "MAC 결과")
    score_a, time_a = measure_mac(pattern, filter_a)
    score_b, time_b = measure_mac(pattern, filter_b)

    print(f"  A 점수: {score_a}")
    print(f"  B 점수: {score_b}")
    print(f"  연산 시간(평균/{REPEAT}회): {(time_a + time_b) / 2:.4f} ms")

    result = decide(score_a, score_b, "A", "B")
    if result == UNDECIDED:
        print(f"  판정: 판정 불가 (두 점수의 차이가 {EPSILON:g} 보다 작음)")
    else:
        print(f"  판정: {result}")

    show_section(4, f"성능 분석 (평균/{REPEAT}회)")
    show_perf_table(measure_sizes((n,)))


def parse_size(key):
    """'size_13' 이나 'size_13_1' 에서 크기 13을 뽑는다.

    규칙에 맞지 않으면 None 을 돌려준다.
    """
    parts = str(key).split("_")
    if len(parts) < 2 or parts[0] != "size" or not parts[1].isdigit():
        return None
    return int(parts[1])


def load_filters(raw_filters, notes):
    """filters 항목을 {크기: {표준 라벨: Matrix}} 형태로 바꾼다.

    문제가 있는 항목은 건너뛰고 그 사유를 notes 에 담는다.
    """
    filters = {}

    if not isinstance(raw_filters, dict):
        notes.append("filters 항목이 없거나 형식이 올바르지 않습니다.")
        return filters

    for size_key, group in raw_filters.items():
        n = parse_size(size_key)
        if n is None:
            notes.append(f"{size_key}: 필터 키는 size_N 형태여야 합니다.")
            continue
        if not isinstance(group, dict):
            notes.append(f"{size_key}: 필터 형식이 올바르지 않습니다.")
            continue

        found = {}
        for label_key, rows in group.items():
            label = normalize_label(label_key)
            if label is None:
                notes.append(f"{size_key}: 알 수 없는 라벨 '{label_key}' 은(는) 건너뜁니다.")
                continue

            try:
                matrix = Matrix.from_rows(rows)
            except ValueError as error:
                notes.append(f"{size_key}/{label}: {error}")
                continue

            if matrix.n != n:
                notes.append(f"{size_key}/{label}: 키는 {n}인데 실제 크기는 {matrix.n}입니다.")
                continue

            found[label] = matrix

        missing = [label for label in (CROSS, X) if label not in found]
        if missing:
            notes.append(f"{size_key}: {', '.join(missing)} 필터가 없어 이 크기는 판정할 수 없습니다.")
            continue

        filters[n] = found
        print(f"  {size_key:<8} 필터를 불러왔습니다. ({CROSS}, {X})")

    return filters


def evaluate_pattern(case_id, entry, filters):
    """패턴 한 건을 판정한다.

    (통과 여부, 화면에 출력할 줄 목록, 실패 사유) 를 돌려준다.
    통과했으면 실패 사유는 None 이다.
    """
    lines = []

    n = parse_size(case_id)
    if n is None:
        return False, lines, "패턴 키는 size_N_번호 형태여야 합니다."
    if not isinstance(entry, dict):
        return False, lines, "패턴 항목의 형식이 올바르지 않습니다."
    if "input" not in entry:
        return False, lines, "'input' 항목이 없습니다."

    expected = normalize_label(entry.get("expected"))
    if expected is None:
        return False, lines, f"expected 값 {entry.get('expected')!r} 을(를) 표준 라벨로 바꿀 수 없습니다."

    if n not in filters:
        return False, lines, f"size_{n} 필터가 없어 판정할 수 없습니다."

    try:
        pattern = Matrix.from_rows(entry["input"])
    except ValueError as error:
        return False, lines, str(error)

    if pattern.n != n:
        return False, lines, f"키는 {n}x{n}인데 input 은 {pattern.n}x{pattern.n}입니다."

    try:
        score_cross = mac(pattern, filters[n][CROSS])
        score_x = mac(pattern, filters[n][X])
    except ValueError as error:
        return False, lines, str(error)

    lines.append(f"  {CROSS} 점수: {score_cross}")
    lines.append(f"  {X} 점수: {score_x}")

    result = decide(score_cross, score_x, CROSS, X)
    if result == UNDECIDED:
        lines.append(f"  판정: {UNDECIDED} | expected: {expected} | FAIL")
        return False, lines, f"두 점수의 차이가 {EPSILON:g} 보다 작아 동점으로 처리했습니다."

    passed = result == expected
    lines.append(f"  판정: {result} | expected: {expected} | {'PASS' if passed else 'FAIL'}")
    if passed:
        return True, lines, None
    return False, lines, f"판정은 {result}인데 expected 는 {expected}입니다."


def read_data(path):
    """데이터 파일을 읽어 딕셔너리로 돌려준다.

    읽지 못하면 안내 메시지를 출력하고 None 을 돌려준다.
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"[안내] 데이터 파일을 찾을 수 없습니다. ({path})")
        return None
    except (json.JSONDecodeError, UnicodeDecodeError):
        print("[안내] 데이터 파일이 손상되어 읽을 수 없습니다.")
        return None
    except OSError as error:
        print(f"[안내] 데이터 파일을 읽지 못했습니다. ({error})")
        return None

    if not isinstance(data, dict):
        print("[안내] 데이터 파일의 형식이 올바르지 않습니다.")
        return None
    return data


def run_data_mode(path=DATA_FILE):
    """data.json 의 필터와 패턴을 불러와 한꺼번에 판정한다."""
    data = read_data(path)
    if data is None:
        return

    show_section(1, "필터 불러오기")
    notes = []
    filters = load_filters(data.get("filters"), notes)
    for note in notes:
        print(f"[안내] {note}")
    if not filters:
        print("[안내] 사용할 수 있는 필터가 없습니다.")

    show_section(2, "패턴 분석")
    raw_patterns = data.get("patterns")
    total = 0
    passed = 0
    failures = []

    if not isinstance(raw_patterns, dict):
        print("[안내] patterns 항목이 없거나 형식이 올바르지 않습니다.")
    else:
        for case_id, entry in raw_patterns.items():
            total += 1
            print(f"[{case_id}]")

            ok, lines, reason = evaluate_pattern(case_id, entry, filters)
            for line in lines:
                print(line)
            if ok:
                passed += 1
            else:
                if not lines:
                    print("  판정: FAIL")
                print(f"  사유: {reason}")
                failures.append((case_id, reason))

    show_section(3, f"성능 분석 (평균/{REPEAT}회)")
    show_perf_table(measure_sizes())
    show_flat_comparison()

    show_section(4, "결과 요약")
    print(f"  총 테스트: {total}개")
    print(f"  통과: {passed}개")
    print(f"  실패: {len(failures)}개")
    if failures:
        print()
        print("  실패한 케이스")
        for case_id, reason in failures:
            print(f"  - {case_id}: {reason}")


def show_menu():
    """모드 선택 메뉴를 출력한다."""
    print("=" * 40)
    print(f"  {TITLE}")
    print("=" * 40)
    for number, name in MENU_ITEMS.items():
        print(f"  {number}. {name}")
    print("-" * 40)


def main():
    """프로그램의 시작점.

    Ctrl+C(KeyboardInterrupt) 나 입력 스트림 종료(EOFError) 로 중간에 끊겨도
    파이썬 오류 메시지를 그대로 띄우지 않고 안내 후 종료한다.
    """
    try:
        show_menu()
        choice = ask_int("번호를 선택하세요: ", 1, len(MENU_ITEMS))

        if choice == 1:
            run_user_mode()
        else:
            run_data_mode()
    except KeyboardInterrupt:
        finish_early("Ctrl+C 가 입력되어")
    except EOFError:
        finish_early("입력이 더 이상 들어오지 않아")


def finish_early(reason):
    """실행이 중간에 끊겼을 때 안내하고 마무리한다."""
    print()
    print(f"[안내] {reason} 실행을 중단합니다.")


if __name__ == "__main__":
    main()
