export type ReadingState={saved:string[];read:string[]};
const key='yhr-reading-v1';
let memoryOnly=false;
let fallback:ReadingState={saved:[],read:[]};
export function getReading():ReadingState {
 if(memoryOnly)return fallback;
 try{const value=JSON.parse(localStorage.getItem(key)||'{}');return {saved:Array.isArray(value.saved)?value.saved.filter((x:unknown)=>typeof x==='string').slice(0,500):[],read:Array.isArray(value.read)?value.read.filter((x:unknown)=>typeof x==='string').slice(0,500):[]};}catch{memoryOnly=true;return fallback;}
}
export function toggleReading(slug:string,kind:keyof ReadingState){const state=getReading();state[kind]=state[kind].includes(slug)?state[kind].filter(x=>x!==slug):[...state[kind],slug];fallback=state;let saved=true;try{localStorage.setItem(key,JSON.stringify(state));}catch{memoryOnly=true;saved=false;}window.dispatchEvent(new Event('yhr-reading-change'));return saved;}
