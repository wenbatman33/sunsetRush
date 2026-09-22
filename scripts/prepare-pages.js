import {cp,mkdir,rm,writeFile} from 'node:fs/promises';
// Copy original files only: no bundler, transpilation or minification.
await rm('_site',{recursive:true,force:true});
await mkdir('_site/vendor/babylon',{recursive:true});
for(const name of ['index.html','src'])await cp(name,`_site/${name}`,{recursive:true});
await cp('public','_site',{recursive:true});
for(const name of ['core','loaders'])await cp(`node_modules/@babylonjs/${name}`,`_site/vendor/babylon/${name}`,{recursive:true,filter:source=>!source.endsWith('.map')&&!source.endsWith('.d.ts')});
await writeFile('_site/.nojekyll','');
console.log('Copied native ESM site to _site (no build).');
