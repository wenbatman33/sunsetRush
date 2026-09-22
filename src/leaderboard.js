const KEY='sunset-rush-scores-v1';
const compare=(a,b)=>b.score-a.score||b.distance-a.distance||a.created-b.created;
export function readScores(storage=localStorage){
 const raw=storage.getItem(KEY);if(!raw)return[];
 let rows;try{rows=JSON.parse(raw);}catch{return[];}
 return Array.isArray(rows)?rows.filter(s=>s&&typeof s.id==='string'&&typeof s.name==='string'&&s.name.length<=32&&['score','distance','coins','created'].every(k=>Number.isFinite(s[k])&&s[k]>=0)).sort(compare):[];
}
export function leaderboard(period='all',storage=localStorage,now=Date.now()){
 return readScores(storage).filter(s=>period!=='today'||s.created>=now-86400000).slice(0,20);
}
export function saveScore(entry,storage=localStorage){
 const name=entry.name.trim();if(!name||[...name].length>16)throw Error('請輸入 1–16 字的暱稱。');
 const rows=readScores(storage);if(rows.some(s=>s.id===entry.id))throw Error('這場成績已儲存。');
 const record={...entry,name};rows.push(record);rows.sort(compare);
 try{storage.setItem(KEY,JSON.stringify(rows));}catch{throw Error('無法儲存，請確認瀏覽器允許本機儲存。');}
 return{rank:rows.findIndex(s=>s.id===record.id)+1};
}
