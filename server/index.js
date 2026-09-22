import express from 'express';
import { resolve } from 'node:path';
const app=express();app.disable('x-powered-by');
// Static native ESM hosting only; scores stay in the browser.
app.use('/src',express.static(resolve('src')));
app.use('/vendor/babylon/core',express.static(resolve('node_modules/@babylonjs/core')));
app.use('/vendor/babylon/loaders',express.static(resolve('node_modules/@babylonjs/loaders')));
app.use(express.static(resolve('public')));
app.get('/',(req,res)=>res.sendFile(resolve('index.html')));
app.listen(Number(process.env.PORT||5173),'0.0.0.0',()=>console.log('Sunset Rush: http://localhost:'+(process.env.PORT||5173)));
