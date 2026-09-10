/* ============================================================
   theme.js — 다크 모드
   흐름: 토글 클릭(이벤트) → 테마 상태 변경 → data-theme 갱신(렌더링)
   상태는 <html> 의 data-theme 한 곳에만 두고, 색은 CSS 변수가 알아서 바꾼다.
   ============================================================ */
(() => {
  'use strict';

  const STORAGE_KEY = 'portfolio-theme';
  const root = document.documentElement;
  const toggleButton = document.querySelector('#theme-toggle');
  const toggleIcon = document.querySelector('#theme-toggle-icon');

  /* localStorage 는 시크릿 모드나 저장 차단 설정에서 예외를 던진다.
     테마 하나 때문에 페이지 전체가 멈추면 안 되므로 감싸 둔다. */
  const writeStored = (theme) => {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (error) {
      /* 저장에 실패해도 이번 방문 동안은 테마가 적용된 상태로 남는다 */
    }
  };

  /* 상태를 화면에 반영하는 단 하나의 함수 */
  const applyTheme = (theme) => {
    const isDark = theme === 'dark';

    root.dataset.theme = theme;
    toggleIcon.textContent = isDark ? '☀' : '☾';
    toggleButton.setAttribute('aria-pressed', String(isDark));
    toggleButton.setAttribute('aria-label', isDark ? '라이트 모드로 전환' : '다크 모드로 전환');
  };

  /* 초기 테마는 <head> 의 인라인 스크립트가 이미 정해 두었다.
     여기서는 그 결과를 버튼 모양과 맞추기만 한다. */
  applyTheme(root.dataset.theme === 'dark' ? 'dark' : 'light');

  toggleButton.addEventListener('click', () => {
    const nextTheme = root.dataset.theme === 'dark' ? 'light' : 'dark';

    applyTheme(nextTheme);
    writeStored(nextTheme);
  });
})();
