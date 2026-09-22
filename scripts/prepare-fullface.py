"""Author a replacement full-face helmet surface from the supplied shape reference.
The surface profile replaces the rejected spherical silhouette. The visor is a
material region on the same continuous surface, so it cannot protrude or intersect.
Exports an actual GLB asset; no runtime drawing, SVG or canvas textures.
"""
import math,struct,json
from pathlib import Path
# Cross-sections: height, lateral radius, fore/aft radius, fore/aft centre.
profile=[(0,0,.112,.129,-.018),(.14,.027,.14,.15,0),(.29,.074,.153,.176,.015),(6/14,.133,.159,.187,.005),(9/14,.235,.164,.172,-.01),(.7857,.300,.133,.139,-.024),(.92857,.344,.06,.068,-.025),(1,.354,0,0,-.024)]
def section(u):
 for k in range(len(profile)-1):
  if u<=profile[k+1][0]:break
 a,b=profile[k:k+2];t=(u-a[0])/(b[0]-a[0]);out=[]
 for n in range(1,5):
  before=profile[max(0,k-1)];after=profile[min(len(profile)-1,k+2)]
  ma=(b[n]-before[n])/(b[0]-before[0]);mb=(after[n]-a[n])/(after[0]-a[0]);h=b[0]-a[0]
  out.append((2*t**3-3*t*t+1)*a[n]+(t**3-2*t*t+t)*ma*h+(-2*t**3+3*t*t)*b[n]+(t**3-t*t)*mb*h)
 return out
rows,cols=56,96
verts=[];indices=[[],[],[]]
for i in range(rows+1):
 u=i/rows;y,rx,rz,cz=section(u)
 for k in range(cols+1):
  angle=-math.pi+2*math.pi*k/cols
  verts.append([rx*math.sin(angle),y,cz+rz*math.cos(angle)])
for i in range(rows):
 for k in range(cols):
  u=(i+.5)/rows;angle=-math.pi+2*math.pi*(k+.5)/cols
  opening=6/14<u<9/14 and abs(angle)<math.radians(75)
  glass=6/14+.012<u<9/14-.012 and abs(angle)<math.radians(71)
  mat=2 if glass else 1 if opening or u<.034 else 0
  # Vents remain flush with the shell rather than attached floating shapes.
  if .235<u<.255 and abs(angle)<.16:mat=1
  if .744<u<.771 and .28<abs(angle)<.34:mat=1
  a=i*(cols+1)+k;b=a+cols+1
  indices[mat].extend([a,a+1,b,a+1,b+1,b])
# Dark rolled edge and inner lining around the real neck opening.
start=len(verts)
for y,rx,rz,cz in [(0,.112,.129,-.018),(.007,.10,.117,-.018),(.04,.10,.117,-.018)]:
 for k in range(cols+1):
  angle=-math.pi+2*math.pi*k/cols;verts.append([rx*math.sin(angle),y,cz+rz*math.cos(angle)])
for ring in range(2):
 for k in range(cols):
  a=start+ring*(cols+1)+k;b=a+cols+1;indices[1].extend([a,b,a+1,a+1,b,b+1])
normals=[[0,0,0]for v in verts]
for group in indices:
 for k in range(0,len(group),3):
  tri=group[k:k+3];p,a,b=[verts[i]for i in tri];a=[a[i]-p[i]for i in range(3)];b=[b[i]-p[i]for i in range(3)];n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
  for v in tri:
   for d in range(3):normals[v][d]+=n[d]
for i in range(rows+1):
 a=i*(cols+1);b=a+cols;n=[normals[a][d]+normals[b][d]for d in range(3)];normals[a]=n[:];normals[b]=n[:]
for k,n in enumerate(normals):
 length=math.sqrt(sum(v*v for v in n));normals[k]=[v/length for v in n]if length>1e-9 else[0,1,0]
blob=bytearray();views=[];accessors=[]
def accessor(values,kind,components,target):
 while len(blob)%4:blob.append(0)
 off=len(blob);flat=[v for item in values for v in item]if components>1 else values;fmt='f'if kind==5126 else'I';blob.extend(struct.pack('<'+fmt*len(flat),*flat));views.append({'buffer':0,'byteOffset':off,'byteLength':len(blob)-off,'target':target});a={'bufferView':len(views)-1,'componentType':kind,'count':len(values),'type':{1:'SCALAR',3:'VEC3'}[components]}
 if components==3:a.update(min=[min(v[k]for v in values)for k in range(3)],max=[max(v[k]for v in values)for k in range(3)])
 accessors.append(a);return len(accessors)-1
pos=accessor(verts,5126,3,34962);normal=accessor(normals,5126,3,34962);primitives=[{'attributes':{'POSITION':pos,'NORMAL':normal},'indices':accessor(group,5125,1,34963),'material':i}for i,group in enumerate(indices)]
mats=[{'name':'helmet-shell','pbrMetallicRoughness':{'baseColorFactor':[.89,.9,.88,1],'metallicFactor':.02,'roughnessFactor':.3},'extensions':{'KHR_materials_clearcoat':{'clearcoatFactor':.65,'clearcoatRoughnessFactor':.2}}},{'name':'helmet-gasket','doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':[.015,.019,.022,1],'metallicFactor':0,'roughnessFactor':.77}},{'name':'helmet-flush-visor','pbrMetallicRoughness':{'baseColorFactor':[.012,.025,.037,1],'metallicFactor':.08,'roughnessFactor':.19}}]
j={'asset':{'version':'2.0','generator':'Sunset Rush full-face shell revision'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':'full-face-helmet','mesh':0}],'meshes':[{'name':'continuous-shell-and-visor','primitives':primitives}],'materials':mats,'extensionsUsed':['KHR_materials_clearcoat'],'buffers':[{'byteLength':len(blob)}],'bufferViews':views,'accessors':accessors}
raw=json.dumps(j,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4);blob+=b'\0'*((-len(blob))%4)
out=struct.pack('<4sII',b'glTF',2,28+len(raw)+len(blob))+struct.pack('<I4s',len(raw),b'JSON')+raw+struct.pack('<I4s',len(blob),b'BIN\0')+blob
Path('public/assets/models/fullface-helmet.glb').write_bytes(out)
assert len(indices[2])>0 and max(v[1]for v in verts)<.36
print('Full-face helmet:',len(out),'bytes;',sum(len(x)//3 for x in indices),'triangles; flush visor shares shell vertices')
