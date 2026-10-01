(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const node = (tag, text, cls) => {
    const result = document.createElement(tag);
    if (text !== undefined) result.textContent = text;
    if (cls) result.className = cls;
    return result;
  };
  const link = (text, url) => {
    const result = node('a', text);
    if (typeof url === 'string' && /^(https?:\/\/|[^:]+$)/i.test(url) && !url.startsWith('//')) result.href = url;
    return result;
  };
  const tags = values => {
    const result = node('div');
    values.forEach(value => result.append(node('span', value, 'tag')));
    return result;
  };
  function entry(item, type) {
    const result = node('article', undefined, 'entry');
    const heading = node('h3');
    heading.append(item.url ? link(item.title || item.name, item.url) : node('span', item.title || item.name));
    result.append(heading, node('p', item.description || item.style || ''));
    const meta = type === 'templates' ? '编译环境：' + item.engine : [item.updated || item.date, item.category].filter(Boolean).join(' · ');
    result.append(node('p', meta, 'meta'));
    if (Array.isArray(item.tags)) result.append(tags(item.tags));
    if (item.source) {
      const links = node('div', undefined, 'links');
      links.append(link('原作者与项目说明', item.source));
      result.append(links);
    }
    return result;
  }
  const page = document.body.dataset.page;
  // Homepage and profile are already rendered by the shared build templates.
  if (page === 'home') return;
  const data = page === 'templates' ? window.TEMPLATES : window.NOTES;
  if (!Array.isArray(data)) return;
  const search = $('#search'), select = $('#category'), sort = $('#sort');
  const list = $('#results'), count = $('#result-count');
  const engines = item => ['XeLaTeX', 'LuaLaTeX', 'pdfLaTeX'].filter(value => (item.engine || '').includes(value));
  const categories = item => page === 'templates' ? (engines(item).length ? engines(item) : ['其他／待确认']) : [item.category || '未分类'];
  [...new Set(data.flatMap(categories))].sort((a,b) => a.localeCompare(b, 'zh-CN')).forEach(category => {
    const option = node('option', category); option.value = category; select.append(option);
  });
  const expanded = new Map();
  function readUrl() {
    const params = new URLSearchParams(location.search);
    search.value = params.get('q') || '';
    select.value = [...select.options].some(option => option.value === params.get('category')) ? params.get('category') : 'all';
    if (sort) sort.value = ['updated','date','title'].includes(params.get('sort')) ? params.get('sort') : 'updated';
  }
  function update(writeUrl = true) {
    const query = search.value.trim().toLocaleLowerCase();
    const terms = query.split(/\s+/).filter(Boolean);
    const filtered = data.filter(item => {
      const text = [item.name, item.title, item.style, item.description, ...(item.tags || []), item.engine, ...categories(item)].filter(Boolean).join(' ').toLocaleLowerCase();
      return (select.value === 'all' || categories(item).includes(select.value)) && terms.every(term => text.includes(term));
    });
    if (sort) filtered.sort((a,b) => sort.value === 'title' ? a.title.localeCompare(b.title, 'zh-CN') : (b[sort.value] || b.date || '').localeCompare(a[sort.value] || a.date || '') || a.title.localeCompare(b.title, 'zh-CN'));
    if (page === 'notes' && filtered.length) {
      const groups = new Map();
      filtered.forEach(item => {const category = categories(item)[0]; if (!groups.has(category)) groups.set(category, []); groups.get(category).push(item);});
      count.textContent = `${groups.size} 个分类 · ${filtered.length} / ${data.length} 篇笔记`;
      list.replaceChildren(...[...groups].sort(([a],[b]) => a.localeCompare(b,'zh-CN')).map(([category,items]) => {
        const group = node('details', undefined, 'note-category');
        const filtering = Boolean(query) || select.value !== 'all';
        group.open = filtering || Boolean(expanded.get(category));
        const summary = node('summary');
        summary.append(node('span',category,'category-name'),node('span',`${items.length} 篇笔记`,'category-count'));
        const body = node('div',undefined,'category-body');
        body.append(...items.map(item => entry(item,'notes')));
        group.append(summary,body);
        group.addEventListener('toggle', () => {if (!filtering && group.isConnected) expanded.set(category,group.open);});
        return group;
      }));
    } else {
      count.textContent = `显示 ${filtered.length} / ${data.length} 项`;
      list.replaceChildren(...(filtered.length ? filtered.map(item => entry(item,page)) : [node('p',data.length ? '没有匹配的内容，请更换关键词或分类。' : '尚未发布公开笔记。','empty')]));
    }
    if (writeUrl) {
      const url = new URL(location.href);
      for (const key of ['q','category','sort']) url.searchParams.delete(key);
      if (search.value.trim()) url.searchParams.set('q',search.value.trim());
      if (select.value !== 'all') url.searchParams.set('category',select.value);
      if (sort && sort.value !== 'updated') url.searchParams.set('sort',sort.value);
      try {history.replaceState(null,'',url);} catch { /* Local file previews may disallow history updates. */ }
    }
  }
  search.addEventListener('input',() => update());
  select.addEventListener('change',() => update());
  if (sort) sort.addEventListener('change',() => update());
  $('#clear').addEventListener('click',() => {search.value='';select.value='all';if(sort) sort.value='updated';update();search.focus();});
  window.addEventListener('popstate',() => {readUrl();update(false);});
  readUrl();update(false);
})();
