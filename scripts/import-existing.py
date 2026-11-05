"""Import existing site content into the isolated Fuwari preview."""
from pathlib import Path
import json, shutil, html
from urllib.parse import quote
source=Path('/workspace/site-backup-before-fuwari-20261105')
root=Path(__file__).resolve().parents[1]
posts=root/'src/content/posts'
backup=Path('/workspace/fuwari-original-demo-posts')
if not backup.exists(): shutil.move(str(posts), str(backup));posts.mkdir()
for folder in sorted((source/'content').iterdir()):
    if not (folder/'note.json').exists():continue
    item=json.loads((folder/'note.json').read_text())
    dest=root/'public/content'/folder.name
    shutil.copytree(folder,dest,dirs_exist_ok=True)
    slug=folder.name
    pdfs=[{'label':a.get('label',a['file']),'url':'/content/'+slug+'/'+quote(a['file'])} for a in item['attachments'] if a['file'].lower().endswith('.pdf')]
    pdfs.sort(key=lambda a: a['url'].split('/')[-1] != quote(item.get('main','')))
    front={'title':item['title'],'published':item['date'],'description':item['description'],'category':item['category'],'tags':item['tags'],'lang':'zh_CN','pdfs':pdfs}
    if item.get('updated'):front['updated']=item['updated']
    body=item['description']+'\n\n'
    if item.get('main','').endswith('.md'):
        body=(folder/item['main']).read_text()
        lines=body.splitlines()
        if lines and lines[0].removeprefix('# ').strip()==item.get('document_title',item['title']):body='\n'.join(lines[1:]).lstrip()
    body+='\n\n## 文档与附件\n\n'
    for a in item['attachments']:body+=f"- [{a.get('label',a['file'])}](/content/{slug}/{quote(a['file'])})\n"
    if item.get('author'):body+='\n'+item['author']+'\n'
    if item.get('instructions'):body+='\n## 阅读说明\n\n'+'\n\n'.join(item['instructions'])+'\n'
    related=[]
    tags=set(item['tags'])-{'学习笔记','论文翻译','测试'}
    for other in sorted((source/'content').glob('*/note.json')):
        if other.parent==folder:continue
        data=json.loads(other.read_text())
        if tags.intersection(data['tags']):related.append(f"- [{data['title']}](/posts/{other.parent.name}/)")
    if related:body+='\n## 相关笔记与论文\n\n'+'\n'.join(related)+'\n'
    header='---\n'+'\n'.join(k+': '+(v if k in ('published','updated') else json.dumps(v,ensure_ascii=False)) for k,v in front.items())+'\n---\n\n'
    (posts/(slug+'.md')).write_text(header+body)
    (dest/'index.html').write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=/posts/{slug}/"><title>{html.escape(item["title"])}</title><a href="/posts/{slug}/">阅读笔记</a></html>')
shutil.copytree(source/'assets',root/'public/assets',dirs_exist_ok=True)
for filename in ['lumina-preview.pdf','lumina-xelatex.zip']:
    shutil.copy2(source/filename,root/'public'/filename)
(root/'src/data').mkdir(exist_ok=True)
shutil.copy2(source/'template-data.json',root/'src/data/resources.json')
(root/'public/notes.html').write_text('<meta http-equiv="refresh" content="0;url=/archive/">')
print('Imported 5 notes, original attachments and resource metadata.')
