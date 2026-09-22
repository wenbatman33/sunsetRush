"""Prepare the CC BY Poly by Google motorcycle: preserve source geometry/texture,
normalise metres, split existing wheel components, and separate glass/lamp materials.
"""
import struct,json,math,zlib,collections
from pathlib import Path
raw=Path('public/assets/models/street-motorcycle-source.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);base=n+28

def read(ai):
 a=j['accessors'][ai];v=j['bufferViews'][a['bufferView']];fmt={5126:'f',5123:'H'}[a['componentType']];c={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']];return[struct.unpack_from('<'+fmt*c,raw,base+v.get('byteOffset',0)+a.get('byteOffset',0)+i*v.get('byteStride',struct.calcsize(fmt)*c))for i in range(a['count'])]
pts=read(0);uvs=read(1);idx=[x[0]for x in read(2)];v=j['bufferViews'][j['images'][0]['bufferView']];png=raw[base+v.get('byteOffset',0):base+v.get('byteOffset',0)+v['byteLength']]
w,h,depth,color,*_=struct.unpack('>IIBBBBB',png[16:29]);assert depth==8 and color==2
chunks=[];off=8
while off<len(png):
 length=struct.unpack_from('>I',png,off)[0]
 if png[off+4:off+8]==b'IDAT':chunks.append(png[off+8:off+8+length])
 off+=length+12
scan=zlib.decompress(b''.join(chunks));pixels=[];prev=[0]*(w*3)
for y in range(h):
 off=y*(1+w*3);f=scan[off];row=list(scan[off+1:off+1+w*3])
 for x in range(w*3):
  a=row[x-3]if x>=3 else 0;b=prev[x];c=prev[x-3]if x>=3 else 0;p=a+b-c
  predictor=0 if f==0 else a if f==1 else b if f==2 else(a+b)//2 if f==3 else min([(abs(p-a),a),(abs(p-b),b),(abs(p-c),c)],key=lambda q:q[0])[1]
  row[x]=(row[x]+predictor)%256
 pixels.append(row);prev=row
parents=list(range(len(pts)));weld={}
def root(a):
 while parents[a]!=a:parents[a]=parents[parents[a]];a=parents[a]
 return a
def union(a,b):parents[root(a)]=root(b)
for i,p in enumerate(pts):
 key=tuple(round(x,3)for x in p)
 if key in weld:union(i,weld[key])
 else:weld[key]=i
for k in range(0,len(idx),3):union(idx[k],idx[k+1]);union(idx[k],idx[k+2])
groups=collections.defaultdict(list)
for k in range(0,len(idx),3):groups[root(idx[k])].append(idx[k:k+3])
# Smooth curvature within 40 degrees, retaining intentional panel creases.
adjacent=collections.defaultdict(list)
for tri_start in range(0,len(idx),3):
 tri=idx[tri_start:tri_start+3];p,a,b=[pts[i]for i in tri];a=[a[k]-p[k]for k in range(3)];b=[b[k]-p[k]for k in range(3)];normal=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];length=math.sqrt(sum(v*v for v in normal))
 if length:
  normal=[-normal[0]/length,normal[1]/length,-normal[2]/length]
  for i in tri:adjacent[tuple(round(v,4)for v in pts[i])].append(normal)
scale=1.5/67.17902374267578;zc=(-64.68347930908203+62.80489730834961)/2
blob=bytearray();views=[];accessors=[];meshes=[];nodes=[{'name':'street-motorcycle','children':[]}]
def acc(values,c,kind=5126):
 while len(blob)%4:blob.append(0)
 off=len(blob);flat=[x for v in values for x in v]if c>1 else values;fmt='f'if kind==5126 else'I';blob.extend(struct.pack('<'+fmt*len(flat),*flat));views.append({'buffer':0,'byteOffset':off,'byteLength':len(blob)-off});a={'bufferView':len(views)-1,'componentType':kind,'count':len(values),'type':{1:'SCALAR',2:'VEC2',3:'VEC3'}[c]}
 if c==3:a.update(min=[min(v[k]for v in values)for k in range(3)],max=[max(v[k]for v in values)for k in range(3)])
 accessors.append(a);return len(accessors)-1
wheelParents={}
for name,z in [('front',-46.44),('rear',44.24)]:
 wheelParents[name]=len(nodes);nodes.append({'name':'wheel-'+name,'translation':[0,18.25*scale,-(z-zc)*scale],'children':[]});nodes[0]['children'].append(len(nodes)-1)
for gi,tris in enumerate(sorted(groups.values(),key=len,reverse=True)):
 allp=[pts[i]for t in tris for i in t];lo=[min(v[k]for v in allp)for k in range(3)];hi=[max(v[k]for v in allp)for k in range(3)]
 wheel=gi<10;side='front'if(hi[2]+lo[2])<0 else'rear';parent=wheelParents[side]if wheel else 0;pivot=nodes[parent].get('translation',[0,0,0]);parts=collections.defaultdict(list)
 for tri in tris:
  u,v=[sum(uvs[i][k]for i in tri)/3 for k in range(2)];x=min(w-1,max(0,int(u*w)));y=min(h-1,max(0,int(v*h)));rgb=pixels[y][x*3:x*3+3];p=[sum(pts[i][k]for i in tri)/3 for k in range(3)]
  bright=min(rgb)>155;mat=1 if gi in [0,1] else 2 if bright and p[1]>54 and p[2]<-15 else 3 if bright and p[1]>38 and p[2]<-35 else 0
  parts[mat].append(tri)
 prim=[]
 for mat,ts in parts.items():
  ps=[];uv=[];ns=[]
  for tri in ts:
   points=[[-pts[i][0]*scale-pivot[0],pts[i][1]*scale-pivot[1],-(pts[i][2]-zc)*scale-pivot[2]]for i in tri]
   a=[points[1][k]-points[0][k]for k in range(3)];b=[points[2][k]-points[0][k]for k in range(3)];normal=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];length=math.sqrt(sum(x*x for x in normal));normal=[x/length for x in normal]if length else[0,1,0]
   ps.extend(points);uv.extend(uvs[i]for i in tri);
   for vi in tri:
    neighbors=[q for q in adjacent[tuple(round(v,4)for v in pts[vi])]if sum(q[k]*normal[k]for k in range(3))>.766]
    smooth=[sum(q[k]for q in neighbors)for k in range(3)];length=math.sqrt(sum(v*v for v in smooth));ns.append([v/length for v in smooth]if length else normal)
  prim.append({'attributes':{'POSITION':acc(ps,3),'NORMAL':acc(ns,3),'TEXCOORD_0':acc(uv,2)},'material':mat})
 meshes.append({'primitives':prim});nodes.append({'name':'motorcycle-part-'+str(gi),'mesh':len(meshes)-1});nodes[parent]['children'].append(len(nodes)-1)
while len(blob)%4:blob.append(0)
off=len(blob);blob.extend(png);views.append({'buffer':0,'byteOffset':off,'byteLength':len(png)})
mats=[{'name':'motorcycle-finish','pbrMetallicRoughness':{'baseColorTexture':{'index':0},'metallicFactor':.08,'roughnessFactor':.48}},{'name':'motorcycle-tires','pbrMetallicRoughness':{'baseColorTexture':{'index':0},'metallicFactor':0,'roughnessFactor':.95}},{'name':'motorcycle-windscreen','doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':[.08,.14,.18,1],'metallicFactor':.05,'roughnessFactor':.24}},{'name':'motorcycle-headlights','pbrMetallicRoughness':{'baseColorFactor':[.8,.85,.86,1],'metallicFactor':.1,'roughnessFactor':.3},'emissiveFactor':[.08,.085,.09]}]
out={'asset':{'version':'2.0','copyright':'Motorcycle by Poly by Google, CC BY 3.0; https://poly.pizza/m/dse64pqMKAR'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':nodes,'meshes':meshes,'materials':mats,'textures':[{'source':0}],'images':[{'bufferView':len(views)-1,'mimeType':'image/png'}],'accessors':accessors,'bufferViews':views,'buffers':[{'byteLength':len(blob)}]}
a=json.dumps(out,separators=(',',':')).encode();a+=b' '*((-len(a))%4);blob+=b'\0'*((-len(blob))%4);Path('public/assets/models/street-motorcycle.glb').write_bytes(struct.pack('<4sII',b'glTF',2,28+len(a)+len(blob))+struct.pack('<I4s',len(a),b'JSON')+a+struct.pack('<I4s',len(blob),b'BIN\0')+blob)
print('Prepared original motorcycle with',len(meshes),'parts and two separate wheels')
