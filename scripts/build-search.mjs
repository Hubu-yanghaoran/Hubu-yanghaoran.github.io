import { createIndex } from 'pagefind';
import { execFileSync } from 'node:child_process';
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
const { index } = await createIndex();
if (!index) throw new Error('Cannot initialize search index');
const html = await index.addDirectory({ path: 'dist' });
if (html.errors?.length) throw new Error(JSON.stringify(html.errors));
let documents = 0, pages = 0;
const titles = [];
for (const folder of readdirSync('public/content', { withFileTypes: true }).filter(f => f.isDirectory())) {
  const base = path.join('public/content', folder.name);
  const note = JSON.parse(readFileSync(path.join(base, 'note.json'), 'utf8'));
  titles.push({url:'/posts/' + folder.name + '/',meta:{title:note.title},excerpt:note.description || '',type:'笔记',category:note.category || '未分类'});
  for (const attachment of note.attachments.filter(a => a.file.toLowerCase().endsWith('.pdf'))) {
    const text = execFileSync('pdftotext', ['-enc', 'UTF-8', '-layout', path.join(base, attachment.file), '-'], { maxBuffer: 32 * 1024 * 1024 }).toString();
    const sections = text.split('\f');
    documents++;
    for (let i = 0; i < sections.length; i++) {
      const content = sections[i].trim();
      if (!content) continue;
      const pdf = '/content/' + folder.name + '/' + encodeURIComponent(attachment.file);
      const result = await index.addCustomRecord({
        url: '/posts/' + folder.name + '/?pdf=' + encodeURIComponent(pdf) + '&page=' + (i + 1),
        content, language: 'zh-cn',
        meta: { title: `${note.title} · ${attachment.label || attachment.file} · 第 ${i + 1} 页`, type: 'PDF' },
        filters: { type: ['PDF'], category: [note.category || '未分类'] },
      });
      if (result.errors?.length) throw new Error(JSON.stringify(result.errors));
      pages++;
    }
  }
}
for (const resource of JSON.parse(readFileSync('src/data/resources.json','utf8'))) titles.push({url:resource.source,meta:{title:resource.name},excerpt:resource.style || '',type:'资源',category:''});
writeFileSync('dist/search-titles.json',JSON.stringify(titles));
const result = await index.writeFiles({ outputPath: 'dist/pagefind' });
if (result.errors?.length) throw new Error(JSON.stringify(result.errors));
await index.deleteIndex();
console.log(`Search ready: ${documents} PDFs, ${pages} text pages, plus website pages. Scanned image-only pages require OCR and are not indexed.`);
