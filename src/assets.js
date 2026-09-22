// Explicit gzip files work on static hosts (including Pages) without server rules.
// Decompression changes no geometry or texture bytes and needs no decoder download.
export async function assetBytes(url){
 const compressed=typeof DecompressionStream==='function';
 const response=await fetch(url+(compressed?'.gz':''));
 if(!response.ok)throw new Error(`Asset ${url}: HTTP ${response.status}`);
 if(!compressed)return response.arrayBuffer();
 // Some hosts already decode Content-Encoding: gzip before exposing the body.
 const bytes=await response.arrayBuffer();
 const header=new Uint8Array(bytes,0,Math.min(2,bytes.byteLength));
 if(header[0]!==0x1f||header[1]!==0x8b)return bytes;
 return new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
}
