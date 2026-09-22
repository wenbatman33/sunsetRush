import test from 'node:test';
import assert from 'node:assert/strict';
import {roadHeading,roadPose,roadCurvature,subdivideRoadTriangles} from '../src/road.js';
test('curves turn both ways without a sharp heading discontinuity',()=>{
 let left=false,right=false;for(let d=0;d<6000;d+=.5){const k=roadCurvature(d);left ||= k<-.003;right ||= k>.003;assert.ok(Math.abs(roadHeading(d+.5)-roadHeading(d))<.008);}
 assert.ok(left&&right);assert.ok(Math.abs(roadPose(170).x)>40);
});
test('all four lanes stay equally spaced and transverse to road travel',()=>{
 for(let d=0;d<5000;d+=17){const lanes=[-2,-1,0,1].map(l=>roadPose(d,l*3.2,d-12));for(let i=1;i<lanes.length;i++)assert.ok(Math.abs(Math.hypot(lanes[i].x-lanes[i-1].x,lanes[i].z-lanes[i-1].z)-3.2)<1e-9);const center=roadPose(d,0,d);assert.ok(Math.abs(center.x)<1e-9&&Math.abs(center.z)<1e-9);}
});
test('baked segment transforms meet at seams and match moving objects',()=>{
 const placed=(segment,d,x,origin)=>{const center=roadPose(segment),point=roadPose(d,x),root=roadPose(segment,0,origin),h=roadHeading(origin),dx=point.x-center.x,dz=point.z-center.z;return{x:root.x+dx*Math.cos(h)-dz*Math.sin(h),y:root.y+point.y-center.y,z:root.z+dx*Math.sin(h)+dz*Math.cos(h)};};
 for(let d=18;d<2000;d+=18)for(const x of [-8,-6.4,-3.2,0,3.2,8]){
  const origin=d-45,a=placed(d-9,d,x,origin),b=placed(d+9,d,x,origin),object=roadPose(d,x,origin);
  for(const axis of ['x','y','z']){assert.ok(Math.abs(a[axis]-b[axis])<1e-9);assert.ok(Math.abs(a[axis]-object[axis])<1e-9);}
 }
});
test('mesh subdivision preserves winding and interpolates existing UVs',()=>{
 const result=subdivideRoadTriangles([[0,0,0,0,0],[4,0,0,1,0],[0,0,18,0,1]],[0,1,2]);let area=0;
 for(let i=0;i<result.vertices.length;i+=3){const[a,b,c]=result.vertices.slice(i,i+3);assert.ok(Math.max(a[2],b[2],c[2])-Math.min(a[2],b[2],c[2])<=3);const cross=(b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0]);assert.ok(cross>0);area+=cross/2;for(const v of [a,b,c]){assert.ok(Math.abs(v[3]-v[0]/4)<1e-10);assert.ok(Math.abs(v[4]-v[2]/18)<1e-10);}}
 assert.ok(Math.abs(area-36)<1e-9);
});
