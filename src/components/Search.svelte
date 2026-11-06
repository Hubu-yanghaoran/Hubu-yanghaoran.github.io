<script lang="ts">
import I18nKey from "@i18n/i18nKey";
import { i18n } from "@i18n/translation";
import Icon from "@iconify/svelte";
import { url } from "@utils/url-utils.ts";
import { onMount } from "svelte";
import { searchTitles } from '../utils/title-search';
import type { SearchResult } from "@/global";
let keywordDesktop='',keywordMobile='',result:SearchResult[]=[],initialized=false,request=0;
const togglePanel=()=>document.getElementById('search-panel')?.classList.toggle('float-panel-closed');
function visible(show:boolean,desktop:boolean){if(desktop)document.getElementById('search-panel')?.classList.toggle('float-panel-closed',!show);}
async function search(keyword:string,desktop:boolean){
 const current=++request;
 if(!keyword.trim()){result=[];visible(false,desktop);return;}
 try {const matches=await searchTitles(keyword);if(current!==request)return;result=matches.slice(0,8);visible(true,desktop);}
 catch{if(current===request){result=[];visible(true,desktop);}}
}
onMount(()=>{
 initialized=true;
 const shortcut=(event:KeyboardEvent)=>{if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k'){event.preventDefault();location.assign(url('/search/'));}};
 document.addEventListener('keydown',shortcut);return()=>{request++;document.removeEventListener('keydown',shortcut);};
});
$: if(initialized) search(keywordDesktop,true);
$: if(initialized) search(keywordMobile,false);
</script>

<!-- search bar for desktop view -->
<div id="search-bar" class="hidden lg:flex transition-all items-center h-11 mr-2 rounded-lg
      bg-black/[0.04] hover:bg-black/[0.06] focus-within:bg-black/[0.06]
      dark:bg-white/5 dark:hover:bg-white/10 dark:focus-within:bg-white/10
">
    <Icon icon="material-symbols:search" class="absolute text-[1.25rem] pointer-events-none ml-3 transition my-auto text-black/30 dark:text-white/30"></Icon>
    <input placeholder="搜索标题" bind:value={keywordDesktop} on:focus={() => search(keywordDesktop, true)}
           class="transition-all pl-10 text-sm bg-transparent outline-0
         h-full w-40 active:w-60 focus:w-60 text-black/50 dark:text-white/50"
    >
</div>

<!-- toggle btn for phone/tablet view -->
<button on:click={togglePanel} aria-label="Search Panel" id="search-switch"
        class="btn-plain scale-animation lg:!hidden rounded-lg w-11 h-11 active:scale-90">
    <Icon icon="material-symbols:search" class="text-[1.25rem]"></Icon>
</button>

<!-- search panel -->
<div id="search-panel" class="float-panel float-panel-closed search-panel absolute md:w-[30rem]
top-20 left-4 md:left-[unset] right-4 shadow-2xl rounded-2xl p-2">

    <!-- search bar inside panel for phone/tablet -->
    <div id="search-bar-inside" class="flex relative lg:hidden transition-all items-center h-11 rounded-xl
      bg-black/[0.04] hover:bg-black/[0.06] focus-within:bg-black/[0.06]
      dark:bg-white/5 dark:hover:bg-white/10 dark:focus-within:bg-white/10
  ">
        <Icon icon="material-symbols:search" class="absolute text-[1.25rem] pointer-events-none ml-3 transition my-auto text-black/30 dark:text-white/30"></Icon>
        <input placeholder="搜索标题" bind:value={keywordMobile}
               class="pl-10 absolute inset-0 text-sm bg-transparent outline-0
               focus:w-60 text-black/50 dark:text-white/50"
        >
    </div>

    <!-- search results -->
    {#each result as item}
        <a href={item.url}
           class="transition first-of-type:mt-2 lg:first-of-type:mt-0 group block
       rounded-xl text-lg px-3 py-2 hover:bg-[var(--btn-plain-bg-hover)] active:bg-[var(--btn-plain-bg-active)]">
            <div class="transition text-90 inline-flex font-bold group-hover:text-[var(--primary)]">
                {item.meta.title}<Icon icon="fa6-solid:chevron-right" class="transition text-[0.75rem] translate-x-1 my-auto text-[var(--primary)]"></Icon>
            </div>
            <div class="transition text-sm text-50">
                {item.excerpt}
            </div>
        </a>
    {/each}
    <a class="block text-sm text-[var(--primary)] px-3 py-2" href={url("/search/") + "?q=" + encodeURIComponent(keywordDesktop || keywordMobile)}>高级搜索与全部结果 →</a>
</div>

<style>
  input:focus {
    outline: 0;
  }
  .search-panel {
    max-height: calc(100vh - 100px);
    overflow-y: auto;
  }
</style>
