import test from 'node:test';import assert from 'node:assert/strict';
import{qualityProfile,createMotion,landingImpulse,advanceMotion}from'../src/presentation.js';
test('high-DPI clarity is retained with less expensive mobile effects',()=>{
 const mobile=qualityProfile({coarse:true,width:390,dpr:3});const desktop=qualityProfile({width:1440,dpr:2});
 assert.equal(mobile.pixelRatio,2);assert.equal(mobile.ssao,false);assert.equal(mobile.samples,2);assert.equal(desktop.ssao,true);assert.ok(desktop.shadowSize>mobile.shadowSize);assert.equal(qualityProfile({webgl2:false}).ssao,false);
});
test('landing suspension compresses and settles without cumulative drift',()=>{
 const m=createMotion();landingImpulse(m);let lowest=0;for(let i=0;i<180;i++){advanceMotion(m,{dt:1/60});lowest=Math.min(lowest,m.compression);}assert.ok(lowest<-.03);assert.ok(lowest>=-.12);assert.ok(Math.abs(m.compression)<.001);
});
test('lean recovers in air and animation freezes while paused',()=>{
 const m=createMotion();for(let i=0;i<20;i++)advanceMotion(m,{dt:1/60,laneDelta:3.2,speed:40});assert.ok(m.lean<-.4);const frozen={...m};advanceMotion(m,{dt:.05,active:false});assert.deepEqual(m,frozen);for(let i=0;i<60;i++)advanceMotion(m,{dt:1/60,airborne:true,laneDelta:3.2});assert.ok(Math.abs(m.lean)<.001);
});
