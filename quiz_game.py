"""파이썬 기초 퀴즈 게임.

터미널에서 동작하는 4지선다 퀴즈 게임이다.
`python quiz_game.py` 로 실행한다.
"""

TITLE = "파이썬 기초 퀴즈 게임"

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


def show_menu():
    """메뉴를 화면에 출력한다."""
    print()
    print("=" * 40)
    print(f"  {TITLE}")
    print("=" * 40)
    for number, name in MENU_ITEMS.items():
        print(f"  {number}. {name}")
    print("-" * 40)


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


def main():
    """프로그램의 시작점. 메뉴를 반복해서 보여준다."""
    print(f"{TITLE}에 오신 것을 환영합니다!")

    while True:
        show_menu()
        choice = read_menu_choice()

        if choice == 5:
            print("게임을 종료합니다. 수고하셨습니다!")
            break

        # 나머지 기능은 다음 단계에서 구현한다.
        print(f"[알림] '{MENU_ITEMS[choice]}' 기능은 아직 준비 중입니다.")


if __name__ == "__main__":
    main()
