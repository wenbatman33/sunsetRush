// Distance is measured along the route; lane offsets follow its normal.
// Integrating the tangent keeps four lanes equally spaced through each bend.
const points=[{x:0,z:0}];
export function roadHeading(distance){const s=Math.max(0,distance-25),t=Math.min(1,s/40);return(.72*Math.sin(s/105)+.19*Math.sin(s/245))*t*t*(3-2*t);}
export function roadHeight(d){return Math.sin(d/110)*2.5+Math.sin(d/250)*5;}
export function roadSlope(d){return Math.cos(d/110)*2.5/110+Math.cos(d/250)*5/250;}
export function roadCurvature(d){return(roadHeading(d+.5)-roadHeading(d-.5));}
export function roadCenter(d){
 if(d<0)return{x:0,z:d};
 const index=Math.floor(d);
 while(points.length<=index+1){const n=points.length,p=points[n-1],heading=roadHeading(n-.5);points.push({x:p.x+Math.sin(heading),z:p.z+Math.cos(heading)});}
 const a=points[index],b=points[index+1],t=d-index;return{x:a.x+(b.x-a.x)*t,z:a.z+(b.z-a.z)*t};
}
export function roadPose(d,offset=0,origin=0){
 const p=roadCenter(d),o=roadCenter(origin),h=roadHeading(d),base=roadHeading(origin);
 const dx=p.x+Math.cos(h)*offset-o.x,dz=p.z-Math.sin(h)*offset-o.z;
 return{x:dx*Math.cos(base)-dz*Math.sin(base),y:roadHeight(d)-roadHeight(origin),z:dx*Math.sin(base)+dz*Math.cos(base),heading:h-base,pitch:Math.atan(roadSlope(d))};
}
// Subdivide the actual downloaded mesh, interpolating every existing attribute.
// No replacement artwork is drawn. Long triangles need intermediate points to bend.
export function subdivideRoadTriangles(vertices,indices,maxSpan=3){
 const out=[],faces=[];
 function add(a,b,c){
  const span=Math.max(a[2],b[2],c[2])-Math.min(a[2],b[2],c[2]);
  if(span<=maxSpan){const n=out.length;out.push(a,b,c);faces.push(n,n+1,n+2);return;}
  const edges=[[a,b,c],[b,c,a],[c,a,b]].sort((x,y)=>Math.abs(y[0][2]-y[1][2])-Math.abs(x[0][2]-x[1][2]));
  const [p,q,r]=edges[0],mid=p.map((v,k)=>(v+q[k])/2);add(p,mid,r);add(mid,q,r);
 }
 for(let i=0;i<indices.length;i+=3)add(vertices[indices[i]],vertices[indices[i+1]],vertices[indices[i+2]]);
 return{vertices:out,indices:faces};
}
