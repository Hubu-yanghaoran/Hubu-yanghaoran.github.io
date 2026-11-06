export interface TitleResult {
  url: string;
  meta: { title: string };
  excerpt: string;
  type: string;
  category: string;
}
let catalog: Promise<TitleResult[]> | undefined;
export async function searchTitles(query: string, filters: {type?:string;category?:string} = {}) {
  if (!catalog) catalog = fetch('/search-titles.json').then(response => {
    if (!response.ok) throw new Error('Title catalog unavailable');
    return response.json() as Promise<TitleResult[]>;
  }).catch(error=>{catalog=undefined;throw error;});
  const terms = query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  if (!terms.length) return [];
  return (await catalog).filter(item => terms.every(term=>item.meta.title.toLocaleLowerCase().includes(term)) && (!filters.type || item.type===filters.type) && (!filters.category || item.category===filters.category))
    .sort((a,b) => Number(b.meta.title.toLocaleLowerCase().startsWith(query.toLocaleLowerCase())) - Number(a.meta.title.toLocaleLowerCase().startsWith(query.toLocaleLowerCase())));
}
