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


def show_menu():
    """메뉴를 화면에 출력한다."""
    print()
    print("=" * 40)
    print(f"  {TITLE}")
    print("=" * 40)
    for number, name in MENU_ITEMS.items():
        print(f"  {number}. {name}")
    print("-" * 40)


def read_menu_choice():
    """메뉴 번호를 입력받아 돌려준다.

    올바른 번호를 입력할 때까지 계속 다시 물어본다.
    """
    while True:
        raw = input("번호를 선택하세요: ")
        choice = raw.strip()

        if choice == "":
            print("[안내] 입력이 비어 있습니다. 번호를 입력해 주세요.")
            continue

        if not choice.isdigit():
            print("[안내] 숫자만 입력할 수 있습니다. 다시 입력해 주세요.")
            continue

        number = int(choice)
        if number not in MENU_ITEMS:
            print(f"[안내] 1~{len(MENU_ITEMS)} 사이의 번호를 입력해 주세요.")
            continue

        return number


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
