/* ============================================================
   hero.js — 타이핑 효과 (보너스 과제)
   문장을 한 글자씩 늘렸다 줄이며 다음 문장으로 넘어간다.

   setInterval 을 쓰지 않고 setTimeout 을 매번 다시 거는 이유는,
   글자를 찍을 때(90ms)와 지울 때(45ms), 다 찍고 머무를 때(1600ms)의
   간격이 서로 다르기 때문이다. 고정 간격으로는 이 셋을 표현할 수 없다.
   ============================================================ */
(() => {
  'use strict';

  const PHRASES = [
    '이벤트 → 상태 → 화면을 연결합니다.',
    '웹이 어떻게 도는지 배우는 중입니다.',
    '라이브러리 없이 직접 만들어 봅니다.',
  ];

  const TYPE_DELAY = 90; // 한 글자 찍는 간격
  const ERASE_DELAY = 45; // 한 글자 지우는 간격
  const HOLD_DELAY = 1600; // 문장을 다 찍고 머무는 시간

  const output = document.querySelector('#typing-text');

  /* 움직임을 줄이는 설정을 켠 사용자에게는 애니메이션 없이 첫 문장만 보여 준다 */
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    output.textContent = PHRASES[0];
    return;
  }

  let phraseIndex = 0;
  let charCount = 0;
  let isErasing = false;

  const tick = () => {
    const phrase = PHRASES[phraseIndex];

    charCount += isErasing ? -1 : 1;

    /* slice 로 잘라 넣는다. 한 글자씩 이어 붙이면 지울 때 되돌릴 수가 없고,
       화면과 charCount 가 어긋나기 시작하면 맞추기 어렵다. */
    output.textContent = phrase.slice(0, charCount);

    /* 다 찍었으면 지우기로 바꾸고, 그 자리에 잠시 머문다 */
    if (!isErasing && charCount === phrase.length) {
      isErasing = true;
      window.setTimeout(tick, HOLD_DELAY);
      return;
    }

    /* 다 지웠으면 다음 문장으로 넘어간다 */
    if (isErasing && charCount === 0) {
      isErasing = false;
      phraseIndex = (phraseIndex + 1) % PHRASES.length;
    }

    window.setTimeout(tick, isErasing ? ERASE_DELAY : TYPE_DELAY);
  };

  tick();
})();
