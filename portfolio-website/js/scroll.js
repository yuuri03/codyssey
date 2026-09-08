/* ============================================================
   scroll.js — 스크롤 위치에 반응하는 것들
   1) 헤더 배경 (60px 이상)
   2) 맨 위로 버튼 (300px 이상)
   3) 섹션 등장 애니메이션 (Intersection Observer, threshold 0.2)
   4) 현재 보고 있는 섹션의 메뉴 표시
   ============================================================ */
(() => {
  'use strict';

  /* 기준값을 상수로 모아 둔다. README 에 적은 값과 여기가 같아야 한다. */
  const HEADER_SHIFT_Y = 60;
  const SCROLL_TOP_SHOW_Y = 300;
  const REVEAL_THRESHOLD = 0.2;

  const header = document.querySelector('#header');
  const scrollTopButton = document.querySelector('#scroll-top');
  const revealTargets = document.querySelectorAll('[data-reveal]');
  const sections = document.querySelectorAll('main section[id]');
  const navLinks = document.querySelectorAll('.nav__link');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ── 1 · 2. 스크롤 위치 → 상태 → 클래스 ──────────────────── */
  const scrollState = {
    isHeaderShifted: false,
    isScrollTopVisible: false,
  };

  const renderScrollState = () => {
    header.classList.toggle('is-scrolled', scrollState.isHeaderShifted);
    scrollTopButton.classList.toggle('is-visible', scrollState.isScrollTopVisible);
  };

  const readScrollPosition = () => {
    const y = window.scrollY;
    const nextHeaderShifted = y > HEADER_SHIFT_Y;
    const nextScrollTopVisible = y > SCROLL_TOP_SHOW_Y;

    /* 값이 바뀔 때만 DOM 을 건드린다. 스크롤 이벤트는 초당 수십 번 들어온다. */
    if (
      nextHeaderShifted === scrollState.isHeaderShifted &&
      nextScrollTopVisible === scrollState.isScrollTopVisible
    ) {
      return;
    }

    scrollState.isHeaderShifted = nextHeaderShifted;
    scrollState.isScrollTopVisible = nextScrollTopVisible;
    renderScrollState();
  };

  /* 스크롤 이벤트마다 계산하지 않고, 다음 화면 그리기 직전에 한 번만 계산한다 */
  let ticking = false;

  window.addEventListener(
    'scroll',
    () => {
      if (ticking) {
        return;
      }
      ticking = true;
      window.requestAnimationFrame(() => {
        readScrollPosition();
        ticking = false;
      });
    },
    { passive: true }
  );

  /* CSS 전환이 동작하도록, 숨김은 hidden 속성이 아니라 클래스로 다룬다 */
  scrollTopButton.hidden = false;
  readScrollPosition();

  scrollTopButton.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: reducedMotion.matches ? 'auto' : 'smooth',
    });
  });

  /* ── 3. 등장 애니메이션 ──────────────────────────────────── */
  if ('IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) {
            return;
          }
          entry.target.classList.add('is-visible');
          /* 한 번 나타난 섹션은 더 볼 필요가 없다 */
          observer.unobserve(entry.target);
        });
      },
      { threshold: REVEAL_THRESHOLD }
    );

    revealTargets.forEach((target) => revealObserver.observe(target));
  } else {
    /* 관찰자를 못 쓰는 환경에서는 애니메이션 없이 그냥 보여 준다 */
    revealTargets.forEach((target) => target.classList.add('is-visible'));
  }

  /* ── 4. 현재 섹션 표시 ───────────────────────────────────── */
  if ('IntersectionObserver' in window) {
    const linkById = new Map();

    navLinks.forEach((link) => linkById.set(link.getAttribute('href').slice(1), link));

    const sectionObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const link = linkById.get(entry.target.id);

          if (!link) {
            return;
          }
          link.classList.toggle('is-active', entry.isIntersecting);
        });
      },
      /* 화면 가운데 띠에 걸린 섹션 하나만 활성으로 잡히도록 위아래를 잘라 낸다 */
      { rootMargin: '-45% 0px -45% 0px' }
    );

    sections.forEach((section) => sectionObserver.observe(section));
  }
})();
