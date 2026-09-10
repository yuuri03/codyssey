/* ============================================================
   projects.js — GitHub API 연동
   흐름: 요청(이벤트) → status 상태 변경 → render() 가 화면을 다시 그림

   상태는 아래 state 객체 한 곳에만 둔다. 화면을 바꾸는 곳도 render() 하나뿐이라,
   "지금 무엇이 보이는가" 를 알려면 state 만 보면 된다.
   ============================================================ */
(() => {
  'use strict';

  const USERNAME = 'yuuri03';
  const REPOS_URL = `https://api.github.com/users/${USERNAME}/repos?per_page=100&sort=updated`;

  const statusBox = document.querySelector('#projects-status');
  const grid = document.querySelector('#projects-grid');
  const filterBox = document.querySelector('#project-filters');

  /* ── 상태 ────────────────────────────────────────────────── */
  const state = {
    status: 'idle', // 'idle' | 'loading' | 'success' | 'error'
    repos: [], // 받아 온 저장소 전체
    language: 'all', // 고른 언어 필터
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
        const label = language === 'all' ? `전체 (${repos.length})` : language;

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
          <h3 class="card__title">
            <a class="card__link" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">
              ${escapeHtml(name)}
            </a>
          </h3>
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

  /* 로딩·에러·빈 상태가 모두 같은 틀을 쓴다. 다른 것은 스피너와 재시도 버튼뿐이다. */
  const renderState = ({ title, description, spinner = false, retry = false }) => `
    <div class="state">
      ${spinner ? '<div class="spinner" aria-hidden="true"></div>' : ''}
      <p class="state__title">${title}</p>
      <p class="state__desc">${description}</p>
      ${retry ? '<button class="btn btn--ghost" type="button" data-retry>다시 시도</button>' : ''}
    </div>
  `;

  function render() {
    if (state.status === 'loading') {
      filterBox.hidden = true;
      grid.innerHTML = '';
      statusBox.innerHTML = renderState({
        title: '불러오는 중...',
        description: 'GitHub API 에 저장소 목록을 요청하고 있습니다.',
        spinner: true,
      });
      return;
    }

    if (state.status === 'error') {
      filterBox.hidden = true;
      grid.innerHTML = '';
      statusBox.innerHTML = renderState({
        title: '프로젝트를 불러올 수 없습니다',
        description: escapeHtml(state.errorMessage),
        retry: true,
      });
      return;
    }

    if (state.status !== 'success') {
      return;
    }

    /* 성공했지만 저장소가 하나도 없는 경우 */
    if (state.repos.length === 0) {
      filterBox.hidden = true;
      grid.innerHTML = '';
      statusBox.innerHTML = renderState({
        title: '표시할 프로젝트가 없습니다',
        description: `GitHub 사용자 '${USERNAME}' 에 공개된 저장소가 아직 없습니다.`,
      });
      return;
    }

    renderFilters(state.repos);

    /* 고른 언어만 남긴다. 원본 state.repos 는 그대로 두고 새 배열을 만든다.
       그래야 필터를 '전체' 로 되돌릴 때 다시 요청하지 않아도 된다. */
    const visible =
      state.language === 'all'
        ? state.repos
        : state.repos.filter(({ language }) => language === state.language);

    if (visible.length === 0) {
      grid.innerHTML = '';
      statusBox.innerHTML = renderState({
        title: '조건에 맞는 프로젝트가 없습니다',
        description: `${escapeHtml(state.language)} 로 만든 저장소가 없습니다. 다른 언어를 골라 보세요.`,
      });
      return;
    }

    statusBox.innerHTML = '';
    grid.innerHTML = visible.map(createCard).join('');
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

      setState({ status: 'success', repos, language: 'all' });
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

  /* 필터 버튼도 render() 가 다시 그리므로 같은 방식으로 바깥에서 한 번만 받는다.
     버튼은 상태만 바꾸고, 화면을 고치는 일은 render() 가 맡는다. */
  filterBox.addEventListener('click', (event) => {
    const button = event.target.closest('.filter-btn');

    if (!button) {
      return;
    }
    setState({ language: button.dataset.language });
  });

  loadRepos();
})();
