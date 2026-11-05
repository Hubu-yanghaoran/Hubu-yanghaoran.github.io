/* Site-owned preference UI; no external theme runtime is required. */
(() => {
  'use strict';
  const key = 'yhr-appearance-v1';
  const defaults = { theme: 'academic', view: 'cards', font: 'sans', size: '16' };
  const choices = { theme: ['academic', 'paper', 'garden'], view: ['cards', 'list', 'shelf'], font: ['sans', 'serif'], size: ['16', '18', '20'] };
  const root = document.documentElement;
  function validate(value) {
    return Object.fromEntries(Object.entries(defaults).map(([name, fallback]) => [name, choices[name].includes(value?.[name]) ? value[name] : fallback]));
  }
  function readSaved() {
    try { return validate(JSON.parse(localStorage.getItem(key))); }
    catch { return { ...defaults }; }
  }
  let state = readSaved();
  function apply() {
    root.dataset.theme = state.theme;
    root.dataset.notesView = state.view;
    root.dataset.readingFont = state.font;
    root.style.setProperty('--reading-size', state.size + 'px');
  }
  apply();
  document.addEventListener('DOMContentLoaded', () => {
    const library = document.body.classList.contains('notes-library');
    const panel = document.querySelector('.appearance-panel');
    const status = document.querySelector('#appearance-status');
    const controls = [...document.querySelectorAll('[data-preference]')];
    const viewButtons = [...document.querySelectorAll('button[data-notes-view]')];
    const descriptions = { cards: '卡片展示摘要与标签，适合探索阅读。', list: '列表紧凑展示资料，适合快速查找。', shelf: '书架突出文档标题，适合挑选下一篇阅读。' };
    function viewFromUrl() {
      if (!library) return;
      const view = new URLSearchParams(location.search).get('view');
      if (choices.view.includes(view)) state.view = view;
    }
    function sync() {
      apply();
      controls.forEach(control => { control.value = state[control.dataset.preference]; });
      viewButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.notesView === state.view)));
      const description = document.querySelector('#view-description');
      if (description) description.textContent = descriptions[state.view];
    }
    function save() {
      try { localStorage.setItem(key, JSON.stringify(state)); if (status) status.textContent = '偏好已保存在此设备。'; }
      catch { if (status) status.textContent = '当前浏览器无法保存，设置仅在本页生效。'; }
    }
    function writeUrl() {
      if (!library) return;
      const url = new URL(location.href);
      if (state.view === defaults.view) url.searchParams.delete('view');
      else url.searchParams.set('view', state.view);
      try { history.replaceState(null, '', url); } catch { /* file previews */ }
    }
    viewFromUrl(); sync();
    document.querySelectorAll('[data-enhance]').forEach(element => { element.hidden = false; });
    controls.forEach(control => control.addEventListener('change', () => {
      const name = control.dataset.preference;
      if (choices[name]?.includes(control.value)) { state[name] = control.value; sync(); save(); }
    }));
    viewButtons.forEach(button => button.addEventListener('click', () => {
      state.view = button.dataset.notesView; sync(); save(); writeUrl();
    }));
    document.querySelector('#appearance-reset')?.addEventListener('click', () => { state = { ...defaults }; sync(); save(); writeUrl(); });
    document.addEventListener('click', event => { if (panel?.open && !panel.contains(event.target)) panel.open = false; });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && panel?.open) { panel.open = false; panel.querySelector('summary').focus(); }
    });
    window.addEventListener('storage', event => { if (event.key === key || event.key === null) { state = readSaved(); viewFromUrl(); sync(); } });
    window.addEventListener('popstate', () => { state = readSaved(); viewFromUrl(); sync(); });
  });
})();
