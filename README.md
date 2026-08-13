# Codyssey

Codyssey 입학연수 '개발 입문' 과정에서 진행한 미션을 모아 둔 저장소입니다.
미션마다 폴더를 하나씩 두고, 각 폴더 안에 소스와 그 미션의 README 를 함께 둡니다.

## 미션 목록

| 폴더 | 미션 | 내용 |
| --- | --- | --- |
| [python-quiz-game](python-quiz-game) | 뮤지컬 퀴즈 게임 | 터미널에서 동작하는 4지선다 퀴즈 게임. 클래스와 JSON 파일 기반 데이터 영속성을 다룹니다. |
| [mini-npu-simulator](mini-npu-simulator) | Mini NPU 시뮬레이터 | MAC 연산으로 십자가와 X 패턴을 판별하는 프로그램. 부동소수점 비교와 시간 복잡도를 다룹니다. |

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

미션 폴더로 이동해 실행합니다. 자세한 설명은 각 폴더의 README 에 있습니다.

```bash
cd python-quiz-game
python quiz_game.py
```

```bash
cd mini-npu-simulator
python main.py
```

## 공통 사항

- 개발 언어: Python (개발·검증 환경 3.13)
- 실행 방식: 터미널(콘솔)
- 외부 라이브러리를 쓰지 않고 표준 라이브러리만 사용합니다.
