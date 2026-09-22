import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {assetBytes} from '../src/assets.js';
test('every compressed model and HDR decode to the original bytes',async t=>{
 const files=(await readdir('public/assets/models')).filter(n=>n.endsWith('.glb')).map(n=>'public/assets/models/'+n);
 files.push('public/assets/textures/sky.hdr');
 t.mock.method(globalThis,'fetch',async url=>new Response(await readFile(url)));
 for(const path of files)assert.deepEqual(Buffer.from(await assetBytes(path)),await readFile(path),path);
});
test('hosts with automatic HTTP decoding and older browsers both load original bytes',async t=>{
 const original=await readFile('public/assets/models/fullface-helmet.glb');
 t.mock.method(globalThis,'fetch',async()=>new Response(original));
 assert.deepEqual(Buffer.from(await assetBytes('helmet.glb')),original);
 const decoder=globalThis.DecompressionStream;
 try{globalThis.DecompressionStream=undefined;assert.deepEqual(Buffer.from(await assetBytes('helmet.glb')),original);}finally{globalThis.DecompressionStream=decoder;}
});
