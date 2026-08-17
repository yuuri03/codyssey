# Codyssey

Codyssey 입학연수 '개발 입문' 과정에서 한 미션들을 모아둔 저장소예요.
미션마다 폴더를 하나씩 두고, 폴더 안에 소스랑 그 미션의 README 를 같이 넣었어요.

## 미션 목록

| 폴더 | 미션 | 내용 |
|---|---|---|
| [python-quiz-game](python-quiz-game) | 뮤지컬 퀴즈 게임 | 터미널에서 돌아가는 4지선다 퀴즈 게임이에요. 클래스랑 JSON 파일 저장을 다뤄요. |
| [mini-npu-simulator](mini-npu-simulator) | Mini NPU 시뮬레이터 | MAC 연산으로 십자가랑 X 패턴을 판별해요. 부동소수점 비교랑 시간 복잡도를 다뤄요. |

## 폴더 구조

```
codyssey/
├── python-quiz-game/
│   ├── quiz_game.py
│   └── README.md
├── mini-npu-simulator/
│   ├── main.py
│   ├── data.json
│   └── README.md
├── .gitignore
└── README.md
```

## 실행 방법

미션 폴더로 들어가서 실행하면 돼요. 자세한 설명은 각 폴더의 README 에 있어요.

```bash
cd python-quiz-game
python quiz_game.py
```

```bash
cd mini-npu-simulator
python main.py
```

## 공통 사항

- 개발 언어는 파이썬이에요. 3.13 에서 만들고 확인했어요.
- 터미널에서 실행하는 콘솔 프로그램이에요.
- 외부 라이브러리는 안 쓰고 표준 라이브러리만 써요.
- 기능 하나를 끝낼 때마다 커밋하고, 브랜치를 나눠 작업한 뒤 main 에 병합해요.
