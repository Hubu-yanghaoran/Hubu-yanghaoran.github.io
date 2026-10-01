(() => {
"use strict";
const $ = s => document.querySelector(s);
function node(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function link(text,url){const a=node("a",text);if(/^(https?:\/\/|[^:]+$)/i.test(url)&&!url.startsWith("//"))a.href=url;return a;}
function tags(values){const w=node("div");values.forEach(t=>w.append(node("span",t,"tag")));return w;}
const config=window.SITE;
$(".brand").textContent=config.name;$("#profile-name").textContent=config.name;$("#profile-subtitle").textContent=config.subtitle;$("#profile-github").href=config.github;$("#profile-topics").append(tags(config.interests));
const page=document.body.dataset.page;
document.querySelectorAll(".nav a").forEach(a=>{if(a.dataset.page===page)a.setAttribute("aria-current","page");});
function entry(item,type){const box=node("article",undefined,"entry");const heading=node("h3");heading.append(item.url?link(item.title||item.name,item.url):node("span",item.title||item.name));box.append(heading);box.append(node("p",item.description||item.style));box.append(node("p",type==="templates"?"编译环境："+item.engine:[item.date,item.category].filter(Boolean).join(" · "),"meta"));if(item.tags)box.append(tags(item.tags));if(item.source){const links=node("div",undefined,"links");links.append(link("原作者与项目说明",item.source));box.append(links);}return box;}
function home(){
$("#bio").replaceChildren(...config.bio.map(p=>node("p",p)));
const recent=window.NOTES.slice().sort((a,b)=>(b.date||"").localeCompare(a.date||"")).slice(0,3);
$("#recent-notes").replaceChildren(...(recent.length?recent.map(n=>entry(n,"notes")):[node("p","目前尚未发布公开笔记。发布后，这里会显示最新条目。","empty")]));
if(config.publications.length){$("#publications-section").hidden=false;$("#publications").replaceChildren(...config.publications.map(n=>entry(n,"publication")));}
}
function catalog(type){const data=type==="templates"?window.TEMPLATES:window.NOTES;const search=$("#search"),select=$("#category"),list=$("#results"),count=$("#result-count");
const category=item=>type==="templates"?(/XeLaTeX/.test(item.engine)?"XeLaTeX":/LuaLaTeX/.test(item.engine)?"LuaLaTeX":/pdfLaTeX/.test(item.engine)?"pdfLaTeX":"其他／待确认"):(item.category||"未分类");
[...new Set(data.map(category))].sort().forEach(c=>{const o=node("option",c);o.value=c;select.append(o);});
const update=()=>{
  const q=search.value.trim().toLowerCase();
  const filtered=data.filter(x=>(select.value==="all"||category(x)===select.value)&&JSON.stringify([x.name,x.title,x.style,x.description,x.tags,x.engine,category(x)]).toLowerCase().includes(q));
  if(type==="notes"&&filtered.length){
    const groups=new Map();
    filtered.forEach(item=>{const c=category(item);if(!groups.has(c))groups.set(c,[]);groups.get(c).push(item);});
    count.textContent=groups.size+" 个分类 · "+filtered.length+" / "+data.length+" 篇笔记";
    list.replaceChildren(...[...groups.entries()].sort(([a],[b])=>a.localeCompare(b,"zh-CN")).map(([name,items])=>{
      const group=node("details",undefined,"note-category");
      const summary=node("summary");
      summary.append(node("span",name,"category-name"),node("span",items.length+" 篇笔记","category-count"));
      const body=node("div",undefined,"category-body");
      body.append(...items.map(item=>entry(item,"notes")));
      group.append(summary,body);
      return group;
    }));
  }else{
    count.textContent="显示 "+filtered.length+" / "+data.length+" 项";
    list.replaceChildren(...(filtered.length?filtered.map(x=>entry(x,type)):[node("p",data.length?"没有匹配的内容，请更换关键词或分类。":"尚未发布公开笔记。添加笔记后将自动按分类显示。","empty")]));
  }
};
search.addEventListener("input",update);select.addEventListener("change",update);$("#clear").addEventListener("click",()=>{search.value="";select.value="all";update();search.focus();});update();
}
if(page==="home")home();else catalog(page);
})();
