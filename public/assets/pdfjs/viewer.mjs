import * as pdfjsLib from './pdf.min.mjs';
globalThis.pdfjsLib = pdfjsLib;
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL('./pdf.worker.min.mjs', import.meta.url).href;
const status = document.querySelector('#viewer-status');
// Keep the reader chrome in the site's palette; document pages retain their colors.
try {
  const parentRoot = window.parent.document.documentElement;
  const syncTheme = () => { document.documentElement.dataset.theme = parentRoot.dataset.theme || 'academic'; };
  syncTheme();
  new MutationObserver(syncTheme).observe(parentRoot, { attributes: true, attributeFilter: ['data-theme'] });
} catch { /* A standalone or cross-origin embedding keeps the default palette. */ }
try {
  const { EventBus, PDFViewer, PDFLinkService } = await import('./pdf_viewer.mjs');
  const file = new URLSearchParams(location.search).get('file');
  if (!file) throw new Error('没有指定阅读文档');
  const url = new URL(file, location.href);
  if (url.origin !== location.origin || !url.pathname.toLowerCase().endsWith('.pdf')) throw new Error('仅支持本站 PDF 文档');
  const eventBus = new EventBus();
  const linkService = new PDFLinkService({ eventBus, externalLinkTarget: 2, externalLinkRel: 'noopener noreferrer' });
  const viewer = new PDFViewer({
    container: document.querySelector('#viewer-container'), eventBus, linkService,
    annotationEditorMode: pdfjsLib.AnnotationEditorType.DISABLE,
    enableScripting: false, maxCanvasPixels: 8388608,
  });
  linkService.setViewer(viewer);
  const previous = document.querySelector('#previous');
  const next = document.querySelector('#next');
  const number = document.querySelector('#page-number');
  let total = 0;
  const updatePage = () => {
    number.value = viewer.currentPageNumber;
    previous.disabled = viewer.currentPageNumber <= 1;
    next.disabled = viewer.currentPageNumber >= total;
  };
  eventBus.on('pagesinit', () => {
    viewer.currentScaleValue = 'page-width';
    const requestedPage = Number(new URLSearchParams(location.search).get('page'));
    if (Number.isInteger(requestedPage) && requestedPage >= 1 && requestedPage <= total) viewer.currentPageNumber = requestedPage;
    document.querySelectorAll('button,input').forEach(control => { control.disabled = false; });
    updatePage();
  });
  eventBus.on('pagerendered', event => {
    if (event.error) {
      status.textContent = '这一页未能显示，请使用独立窗口或下载阅读。';
      status.hidden = false;
    } else {
      status.hidden = true;
      document.body.dataset.rendered = 'true';
    }
  });
  eventBus.on('pagechanging', updatePage);
  previous.addEventListener('click', () => { if (viewer.currentPageNumber > 1) viewer.currentPageNumber--; });
  next.addEventListener('click', () => { if (viewer.currentPageNumber < total) viewer.currentPageNumber++; });
  number.addEventListener('change', () => {
    const value = Number(number.value);
    if (Number.isInteger(value) && value >= 1 && value <= total) viewer.currentPageNumber = value;
    updatePage();
  });
  document.querySelector('#zoom-out').addEventListener('click', () => { viewer.currentScale = Math.max(.25, viewer.currentScale / 1.2); });
  document.querySelector('#zoom-in').addEventListener('click', () => { viewer.currentScale = Math.min(5, viewer.currentScale * 1.2); });
  document.querySelector('#fit').addEventListener('click', () => { viewer.currentScaleValue = 'page-width'; });
  new ResizeObserver(() => {
    if (viewer.currentScaleValue === 'page-width') viewer.currentScaleValue = 'page-width';
  }).observe(document.querySelector('#viewer-container'));
  const doc = await pdfjsLib.getDocument({
    url: url.href, cMapUrl: new URL('./cmaps/', import.meta.url).href, cMapPacked: true,
    standardFontDataUrl: new URL('./standard_fonts/', import.meta.url).href,
    wasmUrl: new URL('./wasm/', import.meta.url).href, isEvalSupported: false,
  }).promise;
  total = doc.numPages;
  number.max = total;
  document.querySelector('#page-count').textContent = '/ ' + total;
  viewer.setDocument(doc);
  linkService.setDocument(doc);
} catch (error) {
  console.error('PDF preview:', error);
  status.textContent = 'PDF 未能载入，请使用页面中的“独立窗口”或下载阅读。';
  status.hidden = false;
}
