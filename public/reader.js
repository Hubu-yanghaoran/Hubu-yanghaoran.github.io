(() => {
  'use strict';
  const reader = document.querySelector('#pdf-reader');
  if (reader) {
    const frame = reader.querySelector('#pdf-frame');
    const choices = [...reader.querySelectorAll('[data-pdf-url]')];
    choices.forEach(choice => choice.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      const url = choice.dataset.pdfUrl;
      if (choice.getAttribute('aria-current') === 'true') return;
      frame.src = choice.dataset.viewerUrl;
      frame.title = choice.textContent + '在线预览';
      reader.querySelector('#pdf-current').textContent = choice.textContent;
      reader.querySelector('#pdf-open').href = url;
      reader.querySelector('#pdf-download').href = url;
      choices.forEach(link => link.setAttribute('aria-current', String(link === choice)));
    }));
    const expand = reader.querySelector('#pdf-expand');
    expand.hidden = false;
    const setExpanded = expanded => {
      document.body.classList.toggle('reading-expanded', expanded);
      expand.setAttribute('aria-pressed', String(expanded));
      expand.textContent = expanded ? '收起阅读' : '展开阅读';
    };
    expand.addEventListener('click', () => setExpanded(expand.getAttribute('aria-pressed') !== 'true'));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && expand.getAttribute('aria-pressed') === 'true') {
        setExpanded(false);
        expand.focus();
      }
    });
  }
  const toc = document.querySelector('.toc-disclosure');
  if (toc) {
    const narrow = window.matchMedia('(max-width: 820px)');
    toc.open = !narrow.matches;
    narrow.addEventListener('change', event => {toc.open = !event.matches;});
  }
  const body = document.querySelector('#note-body');
  if (!body) return;
  body.querySelectorAll('.math').forEach(element => {
    if (!window.katex) return;
    const source = element.textContent;
    try {
      window.katex.render(source, element, {
        displayMode: element.classList.contains('block') || element.tagName === 'DIV',
        throwOnError: true, trust: false, maxExpand: 1000, maxSize: 20,
        output: 'htmlAndMathml'
      });
    } catch {
      element.textContent = source;
      element.classList.add('math-error');
      element.title = '公式未能排版，已保留原始 TeX';
    }
  });
})();
