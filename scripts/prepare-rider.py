"""Adapt the downloaded CC0 Quaternius rig: suit materials and seated riding pose.
Usage: python3 scripts/prepare-rider.py /path/to/Universal-Base-Characters.zip
Preserves source geometry, skin weights and bones; creates no replacement geometry.
"""
import json,math,struct,sys,zipfile
from pathlib import Path
z=zipfile.ZipFile(sys.argv[1]);base='Universal Base Characters[Standard]/Base Characters/Godot - UE/'
j=json.loads(z.read(base+'Superhero_Male_FullBody.gltf'));blob=bytearray(z.read(base+j['buffers'][0]['uri']))
def mul(a,b):
 x,y,z,w=a;X,Y,Z,W=b
 return [w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z]
def inv(q):return [-q[0],-q[1],-q[2],q[3]]
def rot(q,v):return mul(mul(q,[*v,0]),inv(q))[:3]
def norm(v):
 n=math.sqrt(sum(x*x for x in v));return [x/n for x in v]
def delta(a,b):
 a=norm(a);b=norm(b);q=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0],1+sum(x*y for x,y in zip(a,b))];return norm(q)
parents={c:i for i,n in enumerate(j['nodes']) for c in n.get('children',[])};names={n.get('name'):i for i,n in enumerate(j['nodes'])}
def world(i):
 n=j['nodes'][i];q=n.get('rotation',[0,0,0,1]);p=n.get('translation',[0,0,0]);
 if i not in parents:return p,q
 pp,pq=world(parents[i]);return [a+b for a,b in zip(pp,rot(pq,p))],mul(pq,q)
def aim(name,child,direction):
 i=names[name];p,q=world(i);cp,_=world(names[child]);dq=delta([a-b for a,b in zip(cp,p)],direction);pq=world(parents[i])[1];j['nodes'][i]['rotation']=mul(inv(pq),mul(dq,q))
for n,c,d in [('spine_01','spine_02',[0,1,.32]),('spine_02','spine_03',[0,1,.4]),('spine_03','neck_01',[0,1,.4]),('neck_01','Head',[0,1,-.2])]:aim(n,c,d)
for side,sign in [('l',1),('r',-1)]:
 aim('upperarm_'+side,'lowerarm_'+side,[sign*.28,-.65,.62]);aim('lowerarm_'+side,'hand_'+side,[-sign*.13,-.18,.95])
 aim('thigh_'+side,'calf_'+side,[sign*.25,-.42,.75]);aim('calf_'+side,'foot_'+side,[0,-.82,-.55]);aim('foot_'+side,'ball_'+side,[0,-.1,.95])
# Close fingers around the grips instead of leaving open palms.
for name,i in names.items():
 if name and any(name.startswith(x) for x in ['index_02','middle_02','ring_02','pinky_02']):j['nodes'][i]['rotation']=mul(j['nodes'][i].get('rotation',[0,0,0,1]),[math.sin(.35),0,0,math.cos(.35)])
def read_accessor(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];stride=v.get('byteStride',struct.calcsize(fmt)*count);start=v.get('byteOffset',0)+a.get('byteOffset',0);return [struct.unpack_from('<'+fmt*count,blob,start+k*stride) for k in range(a['count'])]
def add_indices(values):
 while len(blob)%4:blob.append(0)
 offset=len(blob);blob.extend(struct.pack('<'+'I'*len(values),*values));j['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(values)*4,'target':34963});j['accessors'].append({'bufferView':len(j['bufferViews'])-1,'componentType':5125,'count':len(values),'type':'SCALAR'});return len(j['accessors'])-1
p=j['meshes'][2]['primitives'][0];positions=read_accessor(p['attributes']['POSITION']);indices=[v[0] for v in read_accessor(p['indices'])];groups=[[],[],[]]
for k in range(0,len(indices),3):
 tri=indices[k:k+3];x,y,_=[sum(positions[t][a] for t in tri)/3 for a in range(3)]
 if y>1.55:continue
 material=0 if y>1.03 and abs(x)<.7 else 1
 if y>1.18 and y<1.5 and abs(x)<.115:material=2
 groups[material].extend(tri)
attrs={k:v for k,v in p['attributes'].items() if k in ['POSITION','NORMAL','TEXCOORD_0','JOINTS_0','WEIGHTS_0']}
j['meshes'][2]['primitives']=[{'attributes':attrs,'indices':add_indices(v),'material':i} for i,v in enumerate(groups) if v]
j['nodes'][68]['children']=[67,64]
j['materials']=[{'name':name,'pbrMetallicRoughness':{'baseColorFactor':color,'metallicFactor':0,'roughnessFactor':rough}} for name,color,rough in [('racing-leather',[.72,.045,.025,1],.64),('racing-armor',[.028,.044,.055,1],.8),('racing-stripe',[.94,.87,.68,1],.58)]]
j.pop('images',None);j.pop('textures',None);j.pop('samplers',None);j.pop('animations',None)
# Remove unused face meshes to keep their original material references out of export.
j['meshes']=[j['meshes'][2]];j['nodes'][67]['mesh']=0
for i in [65,66]:j['nodes'][i].pop('mesh',None);j['nodes'][i].pop('skin',None)
j['buffers']=[{'byteLength':len(blob)}];out=json.dumps(j,separators=(',',':')).encode();out+=b' '*((-len(out))%4);blob+=b'\0'*((-len(blob))%4)
Path('public/assets/models/racing-rider.glb').write_bytes(struct.pack('<4sII',b'glTF',2,12+8+len(out)+8+len(blob))+struct.pack('<I4s',len(out),b'JSON')+out+struct.pack('<I4s',len(blob),b'BIN\0')+blob)
Path('public/assets/licenses/quaternius-characters.txt').write_text(z.read('Universal Base Characters[Standard]/License_Standard.txt').decode().replace('\r','').strip()+'\n')
print('Posed joints:',{name:[round(v,3) for v in world(names[name])[0]] for name in ['pelvis','Head','hand_l','foot_l']})
