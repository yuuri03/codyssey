/* ============================================================
   contact-form.js — 문의 폼 유효성 검사
   흐름: 입력·제출(이벤트) → 검증 결과 상태 변경 → 에러 메시지 표시/숨김(렌더링)

   <form> 에 novalidate 를 걸어 브라우저 기본 검증을 끄고,
   메시지 문구와 표시 위치를 직접 정한다.
   ============================================================ */
(() => {
  'use strict';

  /* 이메일 형식: 공백이 없는 아이디 @ 공백이 없는 도메인 . 두 글자 이상 */
  const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const MIN_MESSAGE_LENGTH = 10;

  const form = document.querySelector('#contact-form');
  const successBox = document.querySelector('#form-success');

  /* 필드마다 '무엇이 잘못됐는지' 를 문장으로 돌려주는 함수를 둔다.
     통과하면 빈 문자열이다. */
  const validators = {
    name: (value) => {
      if (value === '') {
        return '이름을 입력해 주세요.';
      }
      if (value.length < 2) {
        return '이름은 2자 이상 입력해 주세요.';
      }
      return '';
    },
    email: (value) => {
      if (value === '') {
        return '이메일을 입력해 주세요.';
      }
      if (!EMAIL_PATTERN.test(value)) {
        return '이메일 형식이 올바르지 않습니다. (예: answer@example.com)';
      }
      return '';
    },
    message: (value) => {
      if (value === '') {
        return '메시지를 입력해 주세요.';
      }
      if (value.length < MIN_MESSAGE_LENGTH) {
        return `메시지는 ${MIN_MESSAGE_LENGTH}자 이상 입력해 주세요. (현재 ${value.length}자)`;
      }
      return '';
    },
  };

  const fieldNames = Object.keys(validators);

  /* 에러 메시지를 화면에 반영하는 단 하나의 함수 */
  const renderError = (fieldName, message) => {
    const input = document.querySelector(`#${fieldName}`);
    const errorBox = document.querySelector(`#${fieldName}-error`);
    const hasError = message !== '';

    /* 검증에 걸린 칸만 테두리를 붉게 한다.
       classList.toggle(name, hasError) 한 줄로도 되지만, 붙일 때와 뗄 때가
       각각 어느 경우인지 드러나도록 add 와 remove 로 나눠 적었다. */
    if (hasError) {
      input.classList.add('is-invalid');
    } else {
      input.classList.remove('is-invalid');
    }

    input.setAttribute('aria-invalid', String(hasError));
    errorBox.textContent = message;
    errorBox.hidden = !hasError;
  };

  const validateField = (fieldName) => {
    const value = document.querySelector(`#${fieldName}`).value.trim();
    const message = validators[fieldName](value);

    renderError(fieldName, message);
    return message === '';
  };

  const clearAll = () => {
    fieldNames.forEach((fieldName) => renderError(fieldName, ''));
  };

  /* 입력하는 동안: 이미 에러가 떠 있는 칸만 다시 검사한다.
     처음 치는 글자부터 빨간 글씨가 뜨면 오히려 방해가 되기 때문이다. */
  fieldNames.forEach((fieldName) => {
    const input = document.querySelector(`#${fieldName}`);

    input.addEventListener('input', () => {
      if (input.classList.contains('is-invalid')) {
        validateField(fieldName);
      }
    });
  });

  form.addEventListener('submit', (event) => {
    /* 폼의 기본 동작은 페이지를 다시 불러오는 것이다. 이것을 막고 직접 처리한다. */
    event.preventDefault();

    successBox.hidden = true;

    /* map 으로 모든 칸을 검사한 뒤 판정한다.
       every 만 쓰면 첫 실패에서 멈춰 나머지 칸의 에러가 표시되지 않는다. */
    const results = fieldNames.map((fieldName) => validateField(fieldName));
    const isValid = results.every((passed) => passed);

    if (!isValid) {
      const firstInvalid = form.querySelector('.is-invalid');

      firstInvalid.focus();
      return;
    }

    const { name } = Object.fromEntries(new FormData(form));

    successBox.textContent = `${name.trim()} 님, 메시지가 확인되었습니다. 읽고 답장 드리겠습니다.`;
    successBox.hidden = false;

    form.reset();
    clearAll();
  });
})();
