/* ============================================================
   navigation.js — 햄버거 메뉴와 부드러운 스크롤
   흐름: 버튼 클릭(이벤트) → 열림/닫힘 상태 변경 → 클래스 토글(렌더링)
   ============================================================ */
(() => {
  'use strict';

  const hamburger = document.querySelector('#hamburger');
  const menu = document.querySelector('#nav-menu');
  const anchorLinks = document.querySelectorAll('a[href^="#"]:not(.skip-link)');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  let isMenuOpen = false;

  const renderMenu = () => {
    menu.classList.toggle('is-open', isMenuOpen);
    hamburger.classList.toggle('is-active', isMenuOpen);
    hamburger.setAttribute('aria-expanded', String(isMenuOpen));
    hamburger.setAttribute('aria-label', isMenuOpen ? '메뉴 닫기' : '메뉴 열기');
  };

  const setMenu = (open) => {
    if (isMenuOpen === open) {
      return;
    }
    isMenuOpen = open;
    renderMenu();
  };

  hamburger.addEventListener('click', () => setMenu(!isMenuOpen));

  /* 메뉴가 열린 채로 남지 않도록, 닫아야 할 상황을 모아 둔다 */
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      setMenu(false);
    }
  });

  document.addEventListener('click', (event) => {
    const clickedInsideNav = event.target.closest('.nav');

    if (!clickedInsideNav) {
      setMenu(false);
    }
  });

  /* 창이 넓어져 메뉴가 헤더 안으로 들어가면 열림 상태를 정리한다 */
  window.matchMedia('(min-width: 768px)').addEventListener('change', (event) => {
    if (event.matches) {
      setMenu(false);
    }
  });

  /* 앵커 링크: 기본 점프 대신 부드럽게 이동시킨다.
     헤더에 가려지지 않는 것은 CSS 의 scroll-padding-top 이 처리한다. */
  anchorLinks.forEach((link) => {
    link.addEventListener('click', (event) => {
      const targetId = link.getAttribute('href');

      if (targetId === '#') {
        return;
      }

      const target = document.querySelector(targetId);

      if (!target) {
        return;
      }

      event.preventDefault();
      setMenu(false);

      target.scrollIntoView({
        behavior: reducedMotion.matches ? 'auto' : 'smooth',
        block: 'start',
      });

      /* 주소창의 해시도 맞춰 둬야 새로고침·뒤로가기가 자연스럽다 */
      history.replaceState(null, '', targetId);
    });
  });
})();
