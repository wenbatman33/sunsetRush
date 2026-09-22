export const STEP=1/60,LANE=3.2,MAX_TICKS=72000,ROW_SPACING=76;
export const LANES=Object.freeze([-2,-1,0,1]),ROAD_CENTER=-LANE/2,ROAD_WIDTH=LANE*4+.4;
export function random(seed,n){let x=(seed^Math.imul(n+1,0x9e3779b9))>>>0;x^=x>>>16;x=Math.imul(x,0x21f0aaad);x^=x>>>15;x=Math.imul(x,0x735a2d97);return((x^x>>>15)>>>0)/4294967296;}
export function row(seed,i){
 const r=n=>random(seed,i*31+n),d=100+i*ROW_SPACING+Math.floor(r(0)*32)-16,safe=LANES[Math.floor(r(1)*LANES.length)];
 const blocked=LANES.filter(l=>l!==safe);
 for(let j=blocked.length-1;j>0;j--){const k=Math.floor(r(20+j)*(j+1));[blocked[j],blocked[k]]=[blocked[k],blocked[j]];}
 const count=i<2?1:r(3)>.38?2:1,types=['sedan','taxi','delivery','suv','barrier','cone','box'];
 const objects=blocked.slice(0,count).map((lane,j)=>({id:`o${i}-${j}`,lane,d:d+j*(r(4)>.5?12:-10),type:types[Math.floor(r(5+j)*types.length)]}));
 const ramp=i===1||i>2&&r(9)>.7;
 if(ramp)objects.push({id:`r${i}`,lane:safe,d:d-24,type:'ramp'});
 const coins=3+Math.floor(r(10)*4),start=d-12;
 for(let j=0;j<coins;j++)objects.push({id:`c${i}-${j}`,lane:safe,d:start+j*5,type:'coin',air:ramp});
 return objects;
}
export function createState(seed){return{seed,tick:0,distance:0,lane:0,x:0,y:0,jumpAge:-1,jumpDuration:48,jumpHeight:3.1,health:3,coins:0,hits:0,invincible:0,crashTicks:0,recovery:0,dead:false,speed:40,consumed:new Set(),lastEvent:null,traffic:Array.from({length:6},(_,i)=>({id:'traffic'+i,type:['sedan','taxi','delivery'][i%3],lane:i%2?-1:-2,d:65+i*57+random(seed,i+900)*25,cycle:0}))};}
export function score(s){return Math.floor(s.distance)+s.coins*25;}
function hit(s){s.health--;s.hits++;s.crashTicks=42;s.speed=0;s.invincible=65;s.lastEvent='hit';if(s.health<=0)s.dead=true;}
export function step(s,actions=[]){
 if(s.dead)return;s.lastEvent=null;
 if(s.crashTicks>0){s.tick++;s.crashTicks--;s.speed=0;if(!s.crashTicks)s.recovery=90;return;}
 for(const a of actions){if(a==='left'&&s.jumpAge<0)s.lane=Math.max(LANES[0],s.lane-1);if(a==='right'&&s.jumpAge<0)s.lane=Math.min(LANES[LANES.length-1],s.lane+1);if(a==='jump'&&s.jumpAge<0){s.jumpAge=0;s.jumpDuration=48;s.jumpHeight=3.1;s.lastEvent='jump';}}
 s.tick++;s.speed=Math.min(84,40+s.distance/95)*(s.recovery>0?.45+.55*(1-s.recovery/90):1);if(s.recovery>0)s.recovery--;s.distance+=s.speed*STEP;if(s.jumpAge<0)s.x+=(s.lane*LANE-s.x)*.19;
 if(s.jumpAge>=0){s.jumpAge++;const progress=Math.min(1,s.jumpAge/s.jumpDuration);s.y=4*s.jumpHeight*progress*(1-progress);if(s.jumpAge>=s.jumpDuration){s.jumpAge=-1;s.y=0;s.lastEvent='land';}}
 if(s.invincible>0)s.invincible--;
 const near=Math.max(0,Math.floor((s.distance-150)/ROW_SPACING));
 for(let i=near;i<near+4;i++)for(const o of row(s.seed,i)){
  if(s.consumed.has(o.id)||Math.abs(o.d-s.distance)>(o.type==='coin'?1.4:2.2)||Math.abs(o.lane*LANE-s.x)>1.12)continue;
  if(o.type==='ramp'){if(s.jumpAge<0){s.jumpAge=0;s.jumpDuration=64;s.jumpHeight=5;s.lastEvent='ramp';s.consumed.add(o.id);}}
  else if(o.type==='coin'){if(o.air?s.y>1.6:s.y<1.5){s.coins++;s.consumed.add(o.id);s.lastEvent='coin';}}
  else if(s.y<(['barrier','cone','box'].includes(o.type)?1.25:2.7)&&!s.invincible){hit(s);s.consumed.add(o.id);}
 }
 for(const car of s.traffic){car.d-=24*STEP;if(car.d-s.distance< -12){car.cycle++;car.d=s.distance+170+random(s.seed,car.cycle*13+Number(car.id.slice(7)))*160;}if(!s.invincible&&Math.abs(car.d-s.distance)<2.5&&Math.abs(car.lane*LANE-s.x)<1.25&&s.y<2.9)hit(s);}
 if(s.tick>=MAX_TICKS)s.dead=true;
 if(s.tick%600===0)for(const id of s.consumed){const i=Number(id.slice(1).split('-')[0]);if(100+i*ROW_SPACING<s.distance-80)s.consumed.delete(id);}
}
export function replay(seed,ticks,inputs){
 if(!Number.isInteger(ticks)||ticks<1||ticks>MAX_TICKS||!Array.isArray(inputs)||inputs.length>12000)throw Error('Invalid run');
 let prev=-1;for(const e of inputs){if(!Array.isArray(e)||e.length!==2||!Number.isInteger(e[0])||e[0]<prev||e[0]<0||e[0]>=ticks||!['left','right','jump'].includes(e[1]))throw Error('Invalid input');prev=e[0];}
 const s=createState(seed);let p=0;while(s.tick<ticks&&!s.dead){const a=[];while(p<inputs.length&&inputs[p][0]===s.tick)a.push(inputs[p++][1]);if(a.length>3)throw Error('Too many actions');step(s,a);}if(s.tick!==ticks||!s.dead)throw Error('Run has not ended');return s;
}
