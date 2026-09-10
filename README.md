# Codyssey

Codyssey 입학연수 '개발 입문' 과정에서 한 미션들을 모아둔 저장소예요.
미션마다 폴더를 하나씩 두고, 폴더 안에 소스랑 그 미션의 README 를 같이 넣었어요.

## 미션 목록

| 폴더 | 미션 | 내용 |
|---|---|---|
| [python-quiz-game](python-quiz-game) | 뮤지컬 퀴즈 게임 | 터미널에서 돌아가는 4지선다 퀴즈 게임이에요. 클래스랑 JSON 파일 저장을 다뤄요. |
| [mini-npu-simulator](mini-npu-simulator) | Mini NPU 시뮬레이터 | MAC 연산으로 십자가랑 X 패턴을 판별해요. 부동소수점 비교랑 시간 복잡도를 다뤄요. |
| [portfolio-website](portfolio-website) | 나를 소개하는 웹페이지 | 라이브러리 없이 HTML·CSS·JavaScript 로 만든 반응형 포트폴리오예요. DOM 조작이랑 이벤트, GitHub API 연동을 다뤄요. |

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
├── portfolio-website/
│   ├── index.html
│   ├── css/
│   ├── js/
│   ├── images/
│   └── README.md
├── docs/screenshots/        실행 화면
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

웹 미션은 브라우저로 열어요. 배포된 주소로 바로 볼 수도 있어요.

```bash
cd portfolio-website
python -m http.server 8000   # http://localhost:8000
```

- 포트폴리오 배포 주소: <https://yuuri03.github.io/codyssey/portfolio-website/>

## 공통 사항

- 파이썬 미션은 3.13 에서 만들고 확인했어요. 터미널에서 실행하는 콘솔 프로그램이에요.
- 웹 미션은 Chrome 최신 버전에서 확인했어요. 정적 파일만 있어서 빌드 과정이 없어요.
- 외부 라이브러리는 안 쓰고, 언어와 브라우저가 기본으로 주는 것만 써요.
- 기능 하나를 끝낼 때마다 커밋하고, 브랜치를 나눠 작업한 뒤 main 에 병합해요.
