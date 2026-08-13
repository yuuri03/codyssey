"""뮤지컬 퀴즈 게임.

터미널에서 동작하는 4지선다 퀴즈 게임이다.
`python quiz_game.py` 로 실행한다.
"""

TITLE = "뮤지컬 퀴즈 게임"

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
        best_score (int): 지금까지의 최고 점수(맞힌 문제 수)
    """

    def __init__(self):
        self.quizzes = default_quizzes()
        self.best_score = 0

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

        self.show_result(score, total)
        return score

    def show_result(self, score, total):
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
        print("-" * 40)

    def add_quiz(self):
        """새로운 퀴즈를 등록한다."""
        print("[알림] 퀴즈 추가 기능은 아직 준비 중입니다.")

    def show_quiz_list(self):
        """저장된 퀴즈 목록을 보여준다."""
        print("[알림] 퀴즈 목록 기능은 아직 준비 중입니다.")

    def show_best_score(self):
        """최고 점수를 보여준다."""
        print("[알림] 점수 확인 기능은 아직 준비 중입니다.")

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
                print("게임을 종료합니다. 수고하셨습니다!")
                break


def main():
    """프로그램의 시작점."""
    game = QuizGame()
    game.run()


if __name__ == "__main__":
    main()
