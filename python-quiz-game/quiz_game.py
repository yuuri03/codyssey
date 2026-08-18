"""뮤지컬 퀴즈 게임.

터미널에서 동작하는 4지선다 퀴즈 게임이다.
`python quiz_game.py` 로 실행한다.
"""

import json
import os

TITLE = "뮤지컬 퀴즈 게임"

# 퀴즈 목록과 최고 점수를 저장할 파일.
# 어느 위치에서 실행하든 프로젝트 루트를 가리키도록
# 이 소스 파일이 있는 디렉터리를 기준으로 경로를 만든다.
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

# 저장하다가 멈춰도 직전 내용이 남도록 백업과 임시 파일을 함께 쓴다.
BACKUP_FILE = STATE_FILE + ".bak"
TEMP_FILE = STATE_FILE + ".tmp"

# 메뉴 번호 -> 화면에 보여줄 이름
MENU_ITEMS = {
    1: "퀴즈 풀기",
    2: "퀴즈 추가",
    3: "퀴즈 목록",
    4: "점수 확인",
    5: "종료",
}

# 모든 퀴즈는 4개의 선택지를 가진다.
CHOICE_COUNT = 4


class Quiz:
    """퀴즈 한 문제를 나타내는 클래스.

    속성:
        question (str): 문제 내용
        choices (list[str]): 선택지 4개
        answer (int): 정답 번호 (1~4)
    """

    def __init__(self, question, choices, answer):
        question = question.strip()
        choices = [choice.strip() for choice in choices]

        if not question:
            raise ValueError("문제 내용은 비어 있을 수 없습니다.")
        if len(choices) != CHOICE_COUNT:
            raise ValueError(f"선택지는 {CHOICE_COUNT}개여야 합니다. (입력: {len(choices)}개)")
        if any(not choice for choice in choices):
            raise ValueError("선택지는 비어 있을 수 없습니다.")
        # 같은 내용의 선택지가 둘 이상이면 정답이 하나로 정해지지 않는다.
        if len(set(choices)) != len(choices):
            raise ValueError("선택지는 서로 달라야 합니다.")
        if not isinstance(answer, int) or not 1 <= answer <= CHOICE_COUNT:
            raise ValueError(f"정답 번호는 1~{CHOICE_COUNT} 중 하나여야 합니다. (입력: {answer})")

        self.question = question
        self.choices = choices
        self.answer = answer

    def show(self, number=None):
        """문제와 선택지를 화면에 출력한다.

        number 를 주면 '3번 문제' 처럼 문제 번호를 함께 보여준다.
        """
        header = f"[{number}번 문제] " if number is not None else ""
        print(f"{header}{self.question}")
        for index, choice in enumerate(self.choices, start=1):
            print(f"   {index}) {choice}")

    def is_correct(self, choice):
        """입력한 번호가 정답이면 True 를 돌려준다."""
        return choice == self.answer

    def answer_text(self):
        """정답 선택지의 내용을 돌려준다."""
        return self.choices[self.answer - 1]

    def to_dict(self):
        """JSON 으로 저장할 수 있는 딕셔너리 형태로 바꾼다."""
        return {
            "question": self.question,
            "choices": list(self.choices),
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data):
        """저장 파일에서 읽은 딕셔너리로 Quiz 를 만든다.

        형식이 맞지 않으면 ValueError 를 일으킨다.
        값의 범위 검사는 __init__ 이 다시 한 번 수행한다.
        """
        if not isinstance(data, dict):
            raise ValueError("퀴즈 하나는 딕셔너리 형태여야 합니다.")

        for key in ("question", "choices", "answer"):
            if key not in data:
                raise ValueError(f"퀴즈에 '{key}' 항목이 없습니다.")

        question = data["question"]
        choices = data["choices"]
        answer = data["answer"]

        if not isinstance(question, str):
            raise ValueError("문제 내용은 문자열이어야 합니다.")
        if not isinstance(choices, list) or any(not isinstance(item, str) for item in choices):
            raise ValueError("선택지는 문자열 목록이어야 합니다.")
        # JSON 의 true/false 는 파이썬에서 int 로도 취급되므로 bool 을 먼저 걸러 낸다.
        if isinstance(answer, bool) or not isinstance(answer, int):
            raise ValueError("정답 번호는 정수여야 합니다.")

        return cls(question, choices, answer)

    def __str__(self):
        return f"{self.question} (정답: {self.answer}번 {self.answer_text()})"


# 기본으로 제공되는 뮤지컬 문제.
# (문제, 선택지 4개, 정답 번호) 형태로 적어 두고 Quiz 인스턴스로 만든다.
DEFAULT_QUIZ_DATA = [
    (
        "뮤지컬 「오페라의 유령」의 음악을 작곡한 인물은?",
        ["스티븐 손드하임", "앤드루 로이드 웨버", "클로드미셸 쇤베르크", "프랭크 와일드혼"],
        2,
    ),
    (
        "뮤지컬 「레미제라블」의 원작 소설을 쓴 작가는?",
        ["알렉상드르 뒤마", "에밀 졸라", "빅토르 위고", "오노레 드 발자크"],
        3,
    ),
    (
        "뮤지컬 「캣츠」에서 그리자벨라가 부르는 대표 넘버는?",
        ["Memory", "Tomorrow", "Defying Gravity", "One Day More"],
        1,
    ),
    (
        "미국 브로드웨이 뮤지컬에 수여하는 최고 권위의 상은?",
        ["그래미상", "에미상", "토니상", "골든글로브상"],
        3,
    ),
    (
        "뮤지컬 「해밀턴」의 극본·작사·작곡을 맡고 초연에서 주인공까지 연기한 인물은?",
        ["린마누엘 미란다", "조너선 라슨", "벤지 파섹", "팀 라이스"],
        1,
    ),
    (
        "뮤지컬 「위키드」가 새롭게 해석한 원작 이야기는?",
        ["이상한 나라의 앨리스", "피터 팬", "오즈의 마법사", "신데렐라"],
        3,
    ),
    (
        "이른바 '세계 4대 뮤지컬'에 포함되지 않는 작품은?",
        ["캣츠", "미스 사이공", "시카고", "레미제라블"],
        3,
    ),
    (
        "뮤지컬 「맘마미아!」의 넘버로 사용된 곡을 발표한 그룹은?",
        ["퀸", "비틀즈", "ABBA", "이글스"],
        3,
    ),
    (
        "영국 런던에서 뮤지컬 극장이 밀집해 있는 지역을 부르는 이름은?",
        ["웨스트엔드", "브로드웨이", "몽마르트르", "코번트 가든"],
        1,
    ),
    (
        "뮤지컬 「렌트」가 현대 뉴욕을 배경으로 각색한 오페라 작품은?",
        ["카르멘", "라 보엠", "라 트라비아타", "나비부인"],
        2,
    ),
]


def default_quizzes():
    """기본 퀴즈 데이터를 Quiz 인스턴스 목록으로 만들어 돌려준다."""
    return [Quiz(question, choices, answer) for question, choices, answer in DEFAULT_QUIZ_DATA]


def ask_int(prompt, low, high):
    """`low` 이상 `high` 이하의 정수를 입력받아 돌려준다.

    올바른 값을 입력할 때까지 반복해서 다시 물어본다.
    처리하는 잘못된 입력은 다음 세 가지다.
      - 빈 입력(그냥 Enter)
      - 숫자로 바꿀 수 없는 값 (예: abc)
      - 허용 범위를 벗어난 숫자 (예: 메뉴에서 9)
    입력값은 앞뒤 공백을 제거한 뒤 판단한다.
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


def ask_text(prompt):
    """비어 있지 않은 문자열을 입력받아 돌려준다."""
    while True:
        text = input(prompt).strip()
        if text == "":
            print("[안내] 내용을 입력해 주세요. 빈 값은 사용할 수 없습니다.")
            continue
        return text


def read_menu_choice():
    """메뉴 번호를 입력받아 돌려준다."""
    return ask_int("번호를 선택하세요: ", 1, len(MENU_ITEMS))


class QuizGame:
    """게임 전체를 관리하는 클래스.

    속성:
        quizzes (list[Quiz]): 현재 가지고 있는 퀴즈 목록
        best_score (int | None): 지금까지의 최고 점수(맞힌 문제 수).
            아직 한 번도 풀지 않았으면 None 이다.
    """

    def __init__(self):
        self.quizzes = default_quizzes()
        # 아직 한 번도 퀴즈를 풀지 않았으면 None 이다.
        # 0 은 '풀었지만 한 문제도 못 맞힌 기록' 이므로 둘을 구분한다.
        self.best_score = None

    def to_state(self):
        """저장 파일에 쓸 딕셔너리를 만든다."""
        return {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
        }

    def save(self):
        """현재 퀴즈 목록과 최고 점수를 state.json 에 저장한다.

        저장에 성공하면 True, 실패하면 False 를 돌려준다.
        저장에 실패해도 게임은 계속 진행할 수 있어야 하므로 예외를 밖으로 던지지 않는다.

        state.json 을 곧바로 열어서 쓰면, 쓰는 도중에 프로그램이 멈췄을 때
        반쯤 쓰인 파일만 남아 이전 내용까지 함께 사라진다.
        그래서 임시 파일에 먼저 다 쓴 뒤 이름을 바꿔 끼우고,
        직전 파일은 state.json.bak 으로 옮겨 한 세대 남겨 둔다.
        """
        try:
            with open(TEMP_FILE, "w", encoding="utf-8") as file:
                json.dump(self.to_state(), file, ensure_ascii=False, indent=2)
            if os.path.exists(STATE_FILE):
                os.replace(STATE_FILE, BACKUP_FILE)
            os.replace(TEMP_FILE, STATE_FILE)
        except (OSError, UnicodeEncodeError) as error:
            # OSError 는 디스크나 권한 문제, UnicodeEncodeError 는 입력받은 글자를
            # UTF-8 로 옮길 수 없는 경우다. 어느 쪽이든 게임은 계속할 수 있어야 한다.
            print(f"[안내] 저장에 실패했습니다. 변경 내용이 남지 않을 수 있습니다. ({error})")
            self.remove_temp_file()
            return False
        return True

    @staticmethod
    def remove_temp_file():
        """저장에 실패해 남은 임시 파일을 지운다.

        지우지 못해도 다음 저장 때 덮어쓰므로 오류를 밖으로 알리지 않는다.
        """
        try:
            os.remove(TEMP_FILE)
        except OSError:
            pass

    def load(self):
        """state.json 에서 퀴즈 목록과 최고 점수를 불러온다.

        본 파일을 읽지 못하면 백업 파일로 한 번 더 시도한다.
        둘 다 실패하면 안내 메시지를 출력하고 False 를 돌려주며,
        이때 퀴즈 목록은 __init__ 이 만들어 둔 기본 퀴즈가 그대로 유지된다.
        """
        if self.load_from(STATE_FILE):
            return True

        if os.path.exists(BACKUP_FILE):
            print("[안내] 백업 파일로 다시 시도합니다.")
            if self.load_from(BACKUP_FILE):
                # 살려 낸 내용을 본 파일 자리에 되돌려 놓는다.
                self.save()
                return True

        print("[안내] 기본 퀴즈로 시작합니다.")
        return False

    def load_from(self, path):
        """주어진 파일에서 퀴즈 목록과 최고 점수를 읽어 채운다.

        읽어서 채우는 데 성공하면 True, 실패하면 False 를 돌려준다.
        실패한 경우 퀴즈 목록과 최고 점수는 건드리지 않는다.
        """
        try:
            with open(path, "r", encoding="utf-8") as file:
                state = json.load(file)
        except FileNotFoundError:
            print("[안내] 저장된 데이터가 없습니다.")
            return False
        except (json.JSONDecodeError, UnicodeDecodeError):
            print("[안내] 저장 파일이 손상되어 읽을 수 없습니다.")
            return False
        except OSError as error:
            print(f"[안내] 저장 파일을 읽지 못했습니다. ({error})")
            return False

        if not isinstance(state, dict):
            print("[안내] 저장 파일의 형식이 올바르지 않습니다.")
            return False

        quizzes = self.read_quizzes(state.get("quizzes"))
        if not quizzes:
            print("[안내] 불러올 수 있는 퀴즈가 없습니다.")
            return False

        self.quizzes = quizzes
        self.best_score = self.read_best_score(state.get("best_score"))

        best_text = "없음" if self.best_score is None else f"{self.best_score}문제 정답"
        print(f"[알림] 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고 기록 {best_text})")
        return True

    @staticmethod
    def read_quizzes(raw_quizzes):
        """저장 파일에서 읽은 퀴즈 목록을 Quiz 목록으로 바꾼다.

        형식이 깨진 항목은 건너뛰고, 살아남은 퀴즈만 돌려준다.
        """
        if not isinstance(raw_quizzes, list):
            return []

        quizzes = []
        skipped = 0
        for raw_quiz in raw_quizzes:
            try:
                quizzes.append(Quiz.from_dict(raw_quiz))
            except ValueError:
                skipped += 1

        if skipped:
            print(f"[안내] 형식이 올바르지 않은 퀴즈 {skipped}개를 건너뛰었습니다.")
        return quizzes

    @staticmethod
    def read_best_score(raw_best_score):
        """저장 파일에서 읽은 최고 점수를 검사해 돌려준다.

        기록이 없거나 값이 이상하면 None 을 돌려준다.
        """
        if raw_best_score is None:
            return None
        if isinstance(raw_best_score, bool) or not isinstance(raw_best_score, int):
            print("[안내] 최고 점수 기록이 올바르지 않아 초기화합니다.")
            return None
        if raw_best_score < 0:
            print("[안내] 최고 점수 기록이 올바르지 않아 초기화합니다.")
            return None
        return raw_best_score

    def show_menu(self):
        """메뉴를 화면에 출력한다."""
        print()
        print("=" * 40)
        print(f"  {TITLE}")
        print("=" * 40)
        for number, name in MENU_ITEMS.items():
            print(f"  {number}. {name}")
        print("-" * 40)

    def play_quiz(self):
        """저장된 퀴즈를 차례대로 출제하고 채점한다.

        맞힌 문제 수를 돌려준다. 풀 퀴즈가 없으면 None 을 돌려준다.
        """
        if not self.quizzes:
            print()
            print("[안내] 등록된 퀴즈가 없습니다. 먼저 '2. 퀴즈 추가' 로 문제를 등록해 주세요.")
            return None

        total = len(self.quizzes)
        print()
        print(f"총 {total}문제를 풉니다. 1~{CHOICE_COUNT} 중에서 정답 번호를 입력하세요.")

        score = 0
        for number, quiz in enumerate(self.quizzes, start=1):
            print()
            quiz.show(number)
            choice = ask_int("정답 번호: ", 1, CHOICE_COUNT)

            if quiz.is_correct(choice):
                score += 1
                print("  -> 정답입니다!")
            else:
                print(f"  -> 오답입니다. 정답은 {quiz.answer}번 ({quiz.answer_text()}) 입니다.")

        is_best = self.best_score is None or score > self.best_score
        if is_best:
            self.best_score = score
            self.save()

        self.show_result(score, total, is_best)
        return score

    def show_result(self, score, total, is_best=False):
        """퀴즈를 모두 푼 뒤 결과를 보여준다."""
        percent = round(score / total * 100)
        print()
        print("=" * 40)
        print("  퀴즈 결과")
        print("=" * 40)
        print(f"  총 {total}문제 중 {score}문제를 맞혔습니다. (정답률 {percent}%)")

        if score == total:
            print("  만점입니다! 훌륭합니다.")
        elif percent >= 60:
            print("  잘하셨습니다. 조금만 더 하면 만점이에요.")
        else:
            print("  아쉽네요. 틀린 문제를 다시 확인해 보세요.")

        if is_best:
            print("  새로운 최고 점수입니다!")
        print("-" * 40)

    def add_quiz(self):
        """새로운 퀴즈를 입력받아 등록한다.

        등록에 성공하면 만들어진 Quiz 를, 실패하면 None 을 돌려준다.
        """
        print()
        print("새로운 퀴즈를 추가합니다.")

        question = ask_text("문제를 입력하세요: ")
        choices = [ask_text(f"선택지 {number}: ") for number in range(1, CHOICE_COUNT + 1)]
        answer = ask_int(f"정답 번호 (1~{CHOICE_COUNT}): ", 1, CHOICE_COUNT)

        # ask_text / ask_int 가 형식은 걸러 주지만, 중복 선택지처럼
        # Quiz 가 판단할 문제도 있으므로 생성 단계에서 한 번 더 확인한다.
        try:
            quiz = Quiz(question, choices, answer)
        except ValueError as error:
            print(f"[안내] 퀴즈를 추가하지 못했습니다. {error}")
            return None

        self.quizzes.append(quiz)
        self.save()
        print(f"[알림] 퀴즈가 추가되었습니다. (현재 총 {len(self.quizzes)}문제)")
        return quiz

    def show_quiz_list(self):
        """저장된 퀴즈 목록을 문제 번호와 함께 보여준다."""
        print()
        if not self.quizzes:
            print("[안내] 등록된 퀴즈가 없습니다. 먼저 '2. 퀴즈 추가' 로 문제를 등록해 주세요.")
            return

        print("=" * 40)
        print(f"  등록된 퀴즈 목록 (총 {len(self.quizzes)}문제)")
        print("=" * 40)
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"  [{number}] {quiz.question}")
        print("-" * 40)

    def show_best_score(self):
        """지금까지의 최고 점수를 보여준다."""
        print()
        print("=" * 40)
        print("  최고 점수")
        print("=" * 40)
        if self.best_score is None:
            print("  아직 퀴즈를 풀지 않았습니다. '1. 퀴즈 풀기' 로 도전해 보세요.")
        else:
            print(f"  최고 기록: {self.best_score}문제 정답")
        print("-" * 40)

    def run(self):
        """메뉴를 반복해서 보여주며 게임을 진행한다."""
        print(f"{TITLE}에 오신 것을 환영합니다!")

        while True:
            self.show_menu()
            choice = read_menu_choice()

            if choice == 1:
                self.play_quiz()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.show_quiz_list()
            elif choice == 4:
                self.show_best_score()
            elif choice == 5:
                self.save()
                print("게임을 종료합니다. 수고하셨습니다!")
                break


def main():
    """프로그램의 시작점.

    Ctrl+C(KeyboardInterrupt) 나 입력 스트림 종료(EOFError) 로 게임이 끊겨도
    파이썬 오류 메시지를 그대로 띄우지 않고, 지금까지의 내용을 저장한 뒤 종료한다.
    """
    game = QuizGame()
    game.load()

    try:
        game.run()
    except KeyboardInterrupt:
        finish_early(game, "Ctrl+C 가 입력되어")
    except EOFError:
        finish_early(game, "입력이 더 이상 들어오지 않아")


def finish_early(game, reason):
    """게임이 중간에 끊겼을 때 안내하고 안전하게 마무리한다."""
    print()
    print(f"[안내] {reason} 게임을 중단합니다.")
    if game.save():
        print("[알림] 지금까지의 퀴즈와 최고 점수를 저장했습니다.")
    print("게임을 종료합니다. 수고하셨습니다!")


if __name__ == "__main__":
    main()
