/* ============================================================
   hero.js — 타이핑 효과 (보너스 과제)
   문장을 한 글자씩 늘렸다 줄이며, 다음 문장으로 넘어간다.
   ============================================================ */
(() => {
  'use strict';

  const PHRASES = [
    '웹이 어떻게 도는지 배우는 중입니다.',
    '이벤트 → 상태 → 화면을 연결합니다.',
    '라이브러리 없이 직접 만들어 봅니다.',
  ];

  const TYPE_DELAY = 90; // 한 글자 찍는 간격
  const ERASE_DELAY = 45; // 한 글자 지우는 간격
  const HOLD_DELAY = 1600; // 문장을 다 찍고 머무는 시간

  const output = document.querySelector('#typing-text');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* 움직임을 줄이는 설정이면 애니메이션 없이 첫 문장만 보여 준다 */
  if (reducedMotion.matches) {
    output.textContent = PHRASES[0];
    return;
  }

  let phraseIndex = 0;
  let charCount = 0;
  let isErasing = false;

  const tick = () => {
    const phrase = PHRASES[phraseIndex];

    charCount += isErasing ? -1 : 1;
    output.textContent = phrase.slice(0, charCount);

    if (!isErasing && charCount === phrase.length) {
      isErasing = true;
      window.setTimeout(tick, HOLD_DELAY);
      return;
    }

    if (isErasing && charCount === 0) {
      isErasing = false;
      phraseIndex = (phraseIndex + 1) % PHRASES.length;
    }

    window.setTimeout(tick, isErasing ? ERASE_DELAY : TYPE_DELAY);
  };

  tick();
})();
