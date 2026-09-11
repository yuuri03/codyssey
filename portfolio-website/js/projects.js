/* ============================================================
   projects.js — GitHub API 연동
   흐름: 검색·필터·페이지 이동(이벤트) → state 변경 → render() 가 다시 그림

   상태는 아래 state 객체 한 곳에만 둔다. 화면을 바꾸는 곳도 render() 하나뿐이라,
   "지금 무엇이 보이는가" 를 알려면 state 만 보면 된다.
   ============================================================ */
(() => {
  'use strict';

  const USERNAME = 'yuuri03';
  const REPOS_URL = `https://api.github.com/users/${USERNAME}/repos?per_page=100&sort=updated`;
  const PER_PAGE = 6;

  const toolbar = document.querySelector('#projects-toolbar');
  const searchInput = document.querySelector('#repo-search');
  const filterBox = document.querySelector('#project-filters');
  const countBox = document.querySelector('#projects-count');
  const statusBox = document.querySelector('#projects-status');
  const grid = document.querySelector('#projects-grid');
  const pager = document.querySelector('#projects-pager');
  const anchor = document.querySelector('#github-repos');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ── 상태 ────────────────────────────────────────────────── */
  const state = {
    status: 'idle', // 'idle' | 'loading' | 'success' | 'error'
    repos: [], // 받아 온 저장소 전체
    language: 'all', // 고른 언어 필터
    query: '', // 검색어
    page: 1, // 현재 페이지 (1부터)
    errorMessage: '',
  };

  const setState = (patch) => {
    Object.assign(state, patch);
    render();
  };

  /* ── 도우미 ──────────────────────────────────────────────── */

  /* 저장소 이름과 설명은 남이 쓴 문자열이다.
     템플릿 리터럴로 innerHTML 에 넣기 전에 태그로 읽힐 문자를 막아 둔다. */
  const escapeHtml = (value) =>
    String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');

  const formatDate = (isoText) =>
    new Date(isoText).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });

  /* 응답 코드마다 사용자가 이해할 수 있는 문장으로 바꾼다 */
  const describeError = async (response) => {
    /* 레이트 리밋은 두 곳에서 확인한다.
       헤더가 더 정확하지만 다른 출처의 응답이라 브라우저가 가려 놓는 경우가 있어,
       본문의 message 도 함께 본다. */
    let apiMessage = '';

    try {
      const body = await response.json();

      apiMessage = typeof body.message === 'string' ? body.message : '';
    } catch (error) {
      apiMessage = '';
    }

    const remaining = response.headers.get('X-RateLimit-Remaining');
    const isRateLimited =
      (response.status === 403 || response.status === 429) &&
      (remaining === '0' || apiMessage.toLowerCase().includes('rate limit'));

    if (isRateLimited) {
      return 'GitHub API 요청 한도를 넘었습니다. 인증 없이 호출하면 시간당 60회까지만 가능하니 잠시 뒤에 다시 시도해 주세요.';
    }
    if (response.status === 404) {
      return `GitHub 사용자 '${USERNAME}' 를 찾을 수 없습니다.`;
    }
    return `저장소 목록을 받아오지 못했습니다. (HTTP ${response.status})`;
  };

  /* ── 걸러내기 ────────────────────────────────────────────────
     원본 state.repos 는 건드리지 않고 매번 새 배열을 만든다.
     그래야 검색어를 지우거나 '전체' 로 돌아갈 때 다시 요청하지 않아도 된다. */
  const selectVisible = () => {
    const keyword = state.query.trim().toLowerCase();

    const matched = state.repos
      .filter(({ language }) => state.language === 'all' || language === state.language)
      .filter(({ name, description, language }) => {
        if (keyword === '') {
          return true;
        }
        /* 이름·설명·언어 중 하나라도 검색어를 품고 있으면 남긴다 */
        return [name, description, language]
          .filter(Boolean)
          .some((field) => field.toLowerCase().includes(keyword));
      });

    const totalPages = Math.max(1, Math.ceil(matched.length / PER_PAGE));
    /* 검색으로 결과가 줄면 현재 페이지가 범위를 넘을 수 있다 */
    const page = Math.min(state.page, totalPages);
    const start = (page - 1) * PER_PAGE;

    return { matched, totalPages, page, visible: matched.slice(start, start + PER_PAGE) };
  };

  /* ── 렌더링 ──────────────────────────────────────────────── */

  /* 버튼 목록은 받아 온 저장소에서 만든다. 언어를 미리 적어 두면 새 언어로
     저장소를 만들 때마다 코드를 고쳐야 하기 때문이다. */
  const renderFilters = (repos) => {
    /* map 으로 언어만 뽑고, filter 로 언어가 없는 저장소를 걷어낸 뒤 중복을 없앤다 */
    const languages = [...new Set(repos.map(({ language }) => language).filter(Boolean))].sort();

    if (languages.length === 0) {
      filterBox.hidden = true;
      filterBox.innerHTML = '';
      return;
    }

    filterBox.innerHTML = ['all', ...languages]
      .map((language) => {
        const isActive = language === state.language;
        const label = language === 'all' ? '전체' : language;

        return `
          <button class="filter-btn${isActive ? ' is-active' : ''}" type="button"
                  data-language="${escapeHtml(language)}" aria-pressed="${isActive}">
            ${escapeHtml(label)}
          </button>
        `;
      })
      .join('');

    filterBox.hidden = false;
  };

  const createCard = (repo) => {
    /* 구조분해 할당으로 필요한 값만 꺼내고, 긴 이름은 짧게 바꿔 받는다 */
    const {
      name,
      description,
      html_url: url,
      language,
      stargazers_count: stars,
      forks_count: forks,
      updated_at: updatedAt,
      fork: isFork,
    } = repo;

    return `
      <article class="card">
        <div class="card__head">
          <h4 class="card__title">
            <a class="card__link" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">
              ${escapeHtml(name)}
            </a>
          </h4>
          <span class="card__lang">${escapeHtml(language || 'Text')}</span>
        </div>
        <p class="card__desc">${escapeHtml(description || '설명이 등록되지 않은 저장소입니다.')}</p>
        <ul class="card__meta">
          <li>★ ${stars}</li>
          <li>⑂ ${forks}</li>
          <li>${formatDate(updatedAt)} 갱신</li>
          ${isFork ? '<li>fork</li>' : ''}
        </ul>
      </article>
    `;
  };

  const renderPager = (page, totalPages) => {
    if (totalPages <= 1) {
      pager.hidden = true;
      pager.innerHTML = '';
      return;
    }

    const numbers = Array.from({ length: totalPages }, (unused, index) => index + 1)
      .map((number) => {
        const isCurrent = number === page;

        return `
          <button class="pager__btn${isCurrent ? ' is-current' : ''}" type="button"
                  data-page="${number}"${isCurrent ? ' aria-current="page"' : ''}>
            ${number}
          </button>
        `;
      })
      .join('');

    pager.innerHTML = `
      <button class="pager__btn pager__btn--arrow" type="button" data-page="${page - 1}"
              aria-label="이전 페이지"${page === 1 ? ' disabled' : ''}>←</button>
      ${numbers}
      <button class="pager__btn pager__btn--arrow" type="button" data-page="${page + 1}"
              aria-label="다음 페이지"${page === totalPages ? ' disabled' : ''}>→</button>
    `;
    pager.hidden = false;
  };

  /* 로딩·에러·빈 상태가 모두 같은 틀을 쓴다. 다른 것은 스피너와 재시도 버튼뿐이다. */
  const renderState = ({ title, description, spinner = false, retry = false }) => `
    <div class="state">
      ${spinner ? '<div class="spinner" aria-hidden="true"></div>' : ''}
      <p class="state__title">${title}</p>
      <p class="state__desc">${description}</p>
      ${retry ? '<button class="btn btn--ghost" type="button" data-retry>다시 시도</button>' : ''}
    </div>
  `;

  /* 목록 자리만 비우고 안내를 띄우는 경우가 잦아 따로 묶어 둔다 */
  const showOnlyState = (markup) => {
    grid.innerHTML = '';
    pager.hidden = true;
    countBox.hidden = true;
    statusBox.innerHTML = markup;
  };

  function render() {
    if (state.status === 'loading') {
      toolbar.hidden = true;
      showOnlyState(
        renderState({
          title: '불러오는 중...',
          description: 'GitHub API 에 저장소 목록을 요청하고 있습니다.',
          spinner: true,
        })
      );
      return;
    }

    if (state.status === 'error') {
      toolbar.hidden = true;
      showOnlyState(
        renderState({
          title: '프로젝트를 불러올 수 없습니다',
          description: escapeHtml(state.errorMessage),
          retry: true,
        })
      );
      return;
    }

    if (state.status !== 'success') {
      return;
    }

    /* 성공했지만 저장소가 하나도 없는 경우 */
    if (state.repos.length === 0) {
      toolbar.hidden = true;
      showOnlyState(
        renderState({
          title: '표시할 프로젝트가 없습니다',
          description: `GitHub 사용자 '${USERNAME}' 에 공개된 저장소가 아직 없습니다.`,
        })
      );
      return;
    }

    toolbar.hidden = false;
    renderFilters(state.repos);

    const { matched, totalPages, page, visible } = selectVisible();

    /* 검색이나 필터 결과가 비었을 때 */
    if (matched.length === 0) {
      showOnlyState(
        renderState({
          title: '조건에 맞는 저장소가 없습니다',
          description: '검색어를 줄이거나 다른 언어를 골라 보세요.',
        })
      );
      return;
    }

    statusBox.innerHTML = '';
    countBox.textContent =
      totalPages > 1
        ? `${matched.length}개 중 ${(page - 1) * PER_PAGE + 1}–${(page - 1) * PER_PAGE + visible.length}번째`
        : `${matched.length}개`;
    countBox.hidden = false;

    grid.innerHTML = visible.map(createCard).join('');
    renderPager(page, totalPages);
  }

  /* ── 데이터 불러오기 ─────────────────────────────────────── */
  const loadRepos = async () => {
    setState({ status: 'loading', errorMessage: '' });

    try {
      const response = await fetch(REPOS_URL, {
        headers: { Accept: 'application/vnd.github+json' },
      });

      if (!response.ok) {
        throw new Error(await describeError(response));
      }

      const data = await response.json();

      /* 별이 많은 순, 같으면 최근에 갱신된 순으로 정렬한다 */
      const repos = data.sort(
        (a, b) =>
          b.stargazers_count - a.stargazers_count ||
          new Date(b.updated_at) - new Date(a.updated_at)
      );

      setState({ status: 'success', repos, language: 'all', query: '', page: 1 });
      searchInput.value = '';
    } catch (error) {
      /* fetch 는 네트워크가 끊겼을 때도 예외를 던진다.
         위에서 만든 안내 문장이 있으면 그대로 쓰고, 없으면 일반 문장으로 대신한다. */
      const message =
        error instanceof TypeError
          ? '네트워크에 연결할 수 없습니다. 인터넷 상태를 확인한 뒤 다시 시도해 주세요.'
          : error.message;

      setState({ status: 'error', repos: [], errorMessage: message });
    }
  };

  /* ── 이벤트 연결 ─────────────────────────────────────────── */

  /* 재시도 버튼은 render() 가 그릴 때마다 새로 만들어진다.
     버튼마다 리스너를 다는 대신, 바깥 상자에서 한 번만 받아 처리한다. */
  statusBox.addEventListener('click', (event) => {
    if (event.target.closest('[data-retry]')) {
      loadRepos();
    }
  });

  /* 필터 버튼도 render() 가 다시 그리므로 같은 방식으로 위임한다.
     버튼은 상태만 바꾸고, 화면을 고치는 일은 render() 가 맡는다. */
  filterBox.addEventListener('click', (event) => {
    const button = event.target.closest('.filter-btn');

    if (!button) {
      return;
    }
    /* 조건이 바뀌면 첫 페이지부터 다시 본다 */
    setState({ language: button.dataset.language, page: 1 });
  });

  searchInput.addEventListener('input', () => {
    setState({ query: searchInput.value, page: 1 });
  });

  pager.addEventListener('click', (event) => {
    const button = event.target.closest('.pager__btn');

    if (!button || button.disabled) {
      return;
    }

    setState({ page: Number(button.dataset.page) });

    /* 페이지를 넘기면 목록의 머리가 화면 밖으로 밀려 있기 쉽다.
       바뀐 목록이 보이도록 저장소 묶음의 시작으로 되돌린다. */
    anchor.scrollIntoView({
      behavior: reducedMotion.matches ? 'auto' : 'smooth',
      block: 'start',
    });
  });

  loadRepos();
})();
