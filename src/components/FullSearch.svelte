<script lang="ts">
import { onMount } from 'svelte';
import { searchTitles } from '../utils/title-search';
export let categories: string[] = [];
let query='', type='', category='', status='输入标题关键词，查找笔记和资源。';
let results: {url:string;meta:{title?:string};excerpt:string}[]=[];
let limit=20, request=0, ready=false, total=0;
let scope='titles', advanced=false;
let engine: any;
let debounce: ReturnType<typeof setTimeout>;
function plain(text:string) {return new DOMParser().parseFromString(text,'text/html').body.textContent || '';}
async function search() {
 const current=++request;
 if (!query.trim()) {results=[];total=0;status='输入标题关键词，查找笔记和资源。';return;}
 if (!ready) return;
 status='正在搜索…';
 try {
  const filters: Record<string,string>={};if(type)filters.type=type;if(category)filters.category=category;
  let loaded, count;
  if(scope==='titles') {const matches=await searchTitles(query,filters);count=matches.length;loaded=matches.slice(0,limit);}
  else {
   if(!engine){const source='/pagefind/pagefind.js';engine=await import(/* @vite-ignore */ source);}
   const response=await engine.search(query,{filters});count=response.results.length;
   loaded=await Promise.all(response.results.slice(0,limit).map((r:any)=>r.data()));
  }
  if(current!==request)return;
  results=loaded;total=count;
  status=count ? `找到 ${count} 项结果，显示 ${loaded.length} 项。` : (scope==='titles'?'没有找到匹配标题，可展开高级搜索查找正文和 PDF 全文。':'没有找到匹配内容，请尝试其他关键词或筛选条件。');
 } catch {if(current===request){results=[];total=0;status='搜索暂时无法加载，请稍后重试。';}}
}
function scheduleSearch(){clearTimeout(debounce);debounce=setTimeout(search,180);}
onMount(()=>{query=new URLSearchParams(location.search).get('q')||'';ready=true;search();return()=>{request++;clearTimeout(debounce);};});
</script>

<div class="space-y-4">
<label for="full-query" class="sr-only">全站搜索关键词</label>
<input id="full-query" type="search" bind:value={query} on:input={(event)=>{query=event.currentTarget.value;scheduleSearch();}} placeholder={scope==='titles' ? '搜索笔记或资源标题…' : '搜索正文或论文内容…'} class="w-full rounded-xl px-4 py-3 bg-black/5 dark:bg-white/5 text-black/80 dark:text-white/80 outline-[var(--primary)]" />
<details class="text-sm text-black/60 dark:text-white/60" on:toggle={(event)=>{advanced=event.currentTarget.open;if(!advanced){scope='titles';type='';category='';}limit=20;scheduleSearch();}}>
<summary class="cursor-pointer py-2 text-[var(--primary)]">高级搜索</summary>
<div class="flex flex-wrap gap-3 mt-3">
<label>搜索范围 <select id="search-scope" bind:value={scope} on:change={(event)=>{scope=event.currentTarget.value;limit=20;scheduleSearch();}} class="rounded-lg p-2 bg-[var(--card-bg)]"><option value="titles">仅标题</option><option value="fulltext">正文与 PDF 全文</option></select></label>
<label class="text-sm text-black/60 dark:text-white/60">类型 <select bind:value={type} on:change={(event)=>{type=event.currentTarget.value;scheduleSearch();}} class="rounded-lg p-2 bg-[var(--card-bg)]"><option value="">全部</option><option>笔记</option><option>PDF</option><option>资源</option></select></label>
<label class="text-sm text-black/60 dark:text-white/60">主题 <select bind:value={category} on:change={(event)=>{category=event.currentTarget.value;scheduleSearch();}} class="rounded-lg p-2 bg-[var(--card-bg)]"><option value="">全部</option>{#each categories as item}<option>{item}</option>{/each}</select></label>
</div>
</details>
<p role="status" aria-live="polite" class="text-sm text-black/50 dark:text-white/50">{status}</p>
{#each results as result}<article class="py-4 border-t border-black/10 dark:border-white/10"><a href={result.url} class="font-bold text-lg text-[var(--primary)]">{result.meta.title || '搜索结果'}</a><p class="mt-2 text-sm text-black/60 dark:text-white/60">{plain(result.excerpt)}</p></article>{/each}
{#if results.length<total}<button class="btn-regular px-4 py-2 rounded-lg" on:click={()=>{limit+=20;scheduleSearch();}}>显示更多</button>{/if}
</div>
