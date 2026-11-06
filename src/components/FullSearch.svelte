<script lang="ts">
import { onMount } from 'svelte';
export let categories: string[] = [];
let query='', type='', category='', status='输入关键词，搜索笔记、资源与论文正文。';
let results: {url:string;meta:{title?:string};excerpt:string}[]=[];
let limit=20, request=0, ready=false;
let engine: any;
function plain(text:string) {return new DOMParser().parseFromString(text,'text/html').body.textContent || '';}
async function search() {
  const current=++request;
  if (!query.trim()) {results=[];status='输入关键词，搜索笔记、资源与论文正文。';return;}
  if (!ready) return;
  status='正在搜索…';
  try {
    const filters: Record<string,string>={};if(type)filters.type=type;if(category)filters.category=category;
    const response=await engine.search(query,{filters});
    const loaded=await Promise.all(response.results.slice(0,limit).map((r:any)=>r.data()));
    if(current!==request)return;
    results=loaded;status=response.results.length ? `找到 ${response.results.length} 项结果，显示 ${loaded.length} 项。` : '没有找到匹配内容，请尝试其他关键词或筛选条件。';
  } catch {if(current===request){results=[];status='搜索暂时无法加载，请稍后重试。';}}
}
onMount(()=>{
 const params=new URLSearchParams(location.search);query=params.get('q')||'';
 let alive=true;
 const source= '/pagefind/pagefind.js';
 import(/* @vite-ignore */ source).then(module=>{if(alive){engine=module;ready=true;search();}}).catch(()=>{if(alive)status='搜索暂时无法加载，请稍后重试。';});
 return()=>{alive=false;request++;clearTimeout(debounce);};
});
let debounce: ReturnType<typeof setTimeout>;
function scheduleSearch() {
 clearTimeout(debounce);
 debounce=setTimeout(()=>{
   search();
 },180);
}

</script>
<div class="space-y-4">
<label for="full-query" class="sr-only">全站搜索关键词</label>
<input id="full-query" type="search" bind:value={query} on:input={(event)=>{query=event.currentTarget.value;scheduleSearch();}} placeholder="搜索标题、笔记正文、论文内容…" class="w-full rounded-xl px-4 py-3 bg-black/5 dark:bg-white/5 text-black/80 dark:text-white/80 outline-[var(--primary)]" />
<div class="flex flex-wrap gap-3">
<label class="text-sm text-black/60 dark:text-white/60">类型 <select bind:value={type} on:change={(event)=>{type=event.currentTarget.value;scheduleSearch();}} class="rounded-lg p-2 bg-[var(--card-bg)]"><option value="">全部</option><option>笔记</option><option>PDF</option><option>资源</option></select></label>
<label class="text-sm text-black/60 dark:text-white/60">主题 <select bind:value={category} on:change={(event)=>{category=event.currentTarget.value;scheduleSearch();}} class="rounded-lg p-2 bg-[var(--card-bg)]"><option value="">全部</option>{#each categories as item}<option>{item}</option>{/each}</select></label>
</div>
<p role="status" aria-live="polite" class="text-sm text-black/50 dark:text-white/50">{status}</p>
{#each results as result}<article class="py-4 border-t border-black/10 dark:border-white/10"><a href={result.url} class="font-bold text-lg text-[var(--primary)]">{result.meta.title || '搜索结果'}</a><p class="mt-2 text-sm text-black/60 dark:text-white/60">{plain(result.excerpt)}</p></article>{/each}
{#if results.length===limit}<button class="btn-regular px-4 py-2 rounded-lg" on:click={()=>{limit+=20;scheduleSearch();}}>显示更多</button>{/if}
</div>
