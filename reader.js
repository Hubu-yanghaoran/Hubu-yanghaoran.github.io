(() => {
  'use strict';
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
