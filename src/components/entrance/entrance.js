(() => {
/** Runs on initial document load; outside Swup's replacement containers. */
const element = document.querySelector('[data-entrance]');
if (element) {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const dismiss = () => { element.hidden = true; };
  try {
    const storage = element.dataset.frequency === 'once' ? localStorage : sessionStorage;
    const key = element.dataset.storageKey || 'yhr-entrance-v1';
    if (!reduced.matches && !storage.getItem(key)) {
      storage.setItem(key, 'seen');
      element.hidden = false;
      element.addEventListener('animationend', event => {
        if (event.target === element) dismiss();
      });
      // Independent guard if animations are interrupted by browser extensions.
      window.setTimeout(dismiss, 2800);
    }
  } catch { dismiss(); /* Restricted storage: do not repeatedly play the intro. */ }
  reduced.addEventListener('change', event => { if (event.matches) dismiss(); });
  window.addEventListener('pageshow', event => { if (event.persisted) dismiss(); });
}

})();
