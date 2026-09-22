import test from 'node:test';import assert from 'node:assert/strict';import{saveScore,leaderboard,readScores}from'../src/leaderboard.js';
test('local leaderboard persists, sorts, filters dates and prevents duplicate saves',()=>{
 const data=new Map(),storage={getItem:k=>data.get(k)||null,setItem:(k,v)=>data.set(k,v)},now=Date.now();
 const entry={id:'a',name:'騎士',score:200,distance:100,coins:4,created:now-90000000};saveScore(entry,storage);
 assert.equal(saveScore({...entry,id:'b',score:300,created:now},storage).rank,1);
 assert.deepEqual(leaderboard('all',storage).map(s=>s.id),['b','a']);assert.equal(leaderboard('today',storage,now).length,1);
 assert.equal(readScores({...storage}).length,2);assert.throws(()=>saveScore(entry,storage));
 assert.throws(()=>saveScore({...entry,id:'c'}, {getItem:()=>null,setItem:()=>{throw Error('quota');}}),/無法儲存/);
 assert.deepEqual(readScores({getItem:()=>'{bad json'}),[]);
});
