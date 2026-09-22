import test from 'node:test';import assert from'node:assert/strict';import{createState,step,row,replay,score,LANE,MAX_TICKS,ROW_SPACING,LANES}from'../src/simulation.js';
test('irregular course has a safe lane, varied obstacles and ramps',()=>{const types=new Set(),gaps=new Set();for(let seed=0;seed<25;seed++)for(let i=0;i<200;i++){const os=row(seed,i),blocked=new Set(os.filter(o=>!['coin','ramp'].includes(o.type)).map(o=>o.lane));assert.ok(blocked.size<4);assert.ok(os.filter(o=>o.type==='coin').every(o=>!blocked.has(o.lane)));os.forEach(o=>types.add(o.type));if(i)gaps.add(os[0].d-row(seed,i-1)[0].d);}assert.ok(types.size>=9);assert.ok(gaps.size>20);});
test('all four lanes including opposite lanes are reachable and bounded',()=>{const s=createState(1);step(s,['left','left','left']);assert.equal(s.lane,-2);for(let i=0;i<28;i++)step(s,['left']);assert.ok(Math.abs(s.x+2*LANE)<.03);step(s,['right','right','right']);step(s,['right','right']);assert.equal(s.lane,1);});
test('manual jump lands and ramps launch higher',()=>{const s=createState(1);step(s,['jump']);let max=0;for(let i=0;i<70;i++){step(s);max=Math.max(max,s.y);}assert.ok(max>3);assert.equal(s.y,0);const r=row(12,1).find(o=>o.type==='ramp'),a=createState(12);a.distance=r.d-2;a.x=r.lane*LANE;a.lane=r.lane;step(a);assert.equal(a.lastEvent,'ramp');max=0;for(let i=0;i<50;i++){step(a);max=Math.max(max,a.y);}assert.ok(max>4.9);});
test('each impact halts travel, three impacts end the run permanently',()=>{const s=createState(2);s.lane=-2;s.x=-2*LANE;for(let hit=1;hit<=3;hit++){s.invincible=0;s.crashTicks=0;s.traffic[0].d=s.distance+1;s.traffic[0].lane=-2;step(s);assert.equal(s.health,3-hit);assert.equal(s.speed,0);const d=s.distance;for(let i=0;i<20;i++)step(s);assert.equal(s.distance,d);assert.equal(s.dead,hit===3);}const t=s.tick;step(s,['jump']);assert.equal(s.tick,t);});
test('speed increases continuously toward a cap after recovery',()=>{const a=createState(1),b=createState(1);b.distance=2500;step(a);step(b);assert.ok(b.speed>a.speed+20);assert.ok(b.speed<=84);});
test('server replay matches exact score and rejects unfinished or invalid input',()=>{const s=createState(98),events=[[0,'left'],[0,'left'],[0,'left']];while(!s.dead)step(s,s.tick===0?['left','left','left']:[]);const r=replay(98,s.tick,events);assert.equal(score(r),score(s));assert.equal(r.health,0);assert.throws(()=>replay(98,s.tick-1,events));assert.throws(()=>replay(98,MAX_TICKS+1,[]));assert.throws(()=>replay(98,3,[[0,'teleport']]));});
test('the static obstacle route remains open through all four scenes',()=>{const s=createState(2026);s.traffic=[];while(s.distance<1500&&!s.dead){const i=Math.max(0,Math.floor((s.distance-55)/ROW_SPACING));const safe=row(s.seed,i).find(o=>o.type==='coin').lane;step(s,s.lane<safe?['right']:s.lane>safe?['left']:[]);}assert.equal(s.dead,false);assert.ok(s.distance>=1500);});

test('coins, obstacles and ramps cover all four lanes with opposing traffic on the left',()=>{const coins=new Set(),obstacles=new Set(),ramps=new Set();for(let i=0;i<300;i++)for(const o of row(2026,i)){assert.ok(LANES.includes(o.lane));(o.type==='coin'?coins:o.type==='ramp'?ramps:obstacles).add(o.lane);}for(const lanes of [coins,obstacles,ramps])assert.deepEqual([...lanes].sort((a,b)=>a-b),LANES);assert.deepEqual([...new Set(createState(2026).traffic.map(c=>c.lane))].sort((a,b)=>a-b),[-2,-1]);});

test('jump lands within 0.8 seconds and accelerates downward under gravity',()=>{const s=createState(8);s.traffic=[];step(s,['jump']);const heights=[s.y];while(s.jumpAge>=0){step(s);heights.push(s.y);}assert.equal(heights.length,48);assert.equal(s.y,0);const earlyDrop=heights[27]-heights[28],lateDrop=heights[44]-heights[45];assert.ok(lateDrop>earlyDrop*3);assert.ok(Math.max(...heights)>3);});

test('airborne steering is ignored for manual jumps and ramps, including landing frame',()=>{
 for(const ramp of [false,true]){
  const s=createState(12);s.traffic=[];
  if(ramp){const r=row(12,1).find(o=>o.type==='ramp');s.distance=r.d-2;s.lane=r.lane;s.x=r.lane*LANE;step(s);assert.equal(s.lastEvent,'ramp');}
  else{step(s,['left']);step(s,['jump','right']);}
  const lane=s.lane,x=s.x;assert.ok(s.jumpAge>=0);
  while(s.jumpAge>=0){step(s,['left','right']);assert.equal(s.lane,lane);assert.equal(s.x,x);}
  step(s);assert.equal(s.lane,lane); // Air inputs are discarded, not queued.
  const direction=lane===1?'left':'right';step(s,[direction]);assert.equal(s.lane,lane+(direction==='left'?-1:1));assert.notEqual(s.x,x);
 }
});
