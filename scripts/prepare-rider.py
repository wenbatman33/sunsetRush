"""Adapt the downloaded CC0 Quaternius rig: suit materials and seated riding pose.
Usage: python3 scripts/prepare-rider.py /path/to/Universal-Base-Characters.zip
Preserves source geometry, skin weights and bones; creates no replacement geometry.
"""
import json,math,struct,sys,zipfile
from pathlib import Path
archive=zipfile.ZipFile(sys.argv[1]);base='Universal Base Characters[Standard]/Base Characters/Godot - UE/'
j=json.loads(archive.read(base+'Superhero_Male_FullBody.gltf'));blob=bytearray(archive.read(base+j['buffers'][0]['uri']))
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
# Anchor the hips over the saddle; solve limbs to the actual grips and footrests.
# Targets are in the source rig's metres, before the shared rider mount transform.
def sub(a,b):return [x-y for x,y in zip(a,b)]
def length(v):return math.sqrt(sum(x*x for x in v))
def solve_limb(root,middle,end,target,pole):
 p,_=world(names[root]);m,_=world(names[middle]);e,_=world(names[end])
 a=length(sub(m,p));b=length(sub(e,m));direction=norm(sub(target,p));distance=min(length(sub(target,p)),a+b-.0001)
 along=(a*a-b*b+distance*distance)/(2*distance);height=math.sqrt(max(0,a*a-along*along))
 bend=sub(pole,p);dot=sum(x*y for x,y in zip(bend,direction));bend=norm([bend[k]-direction[k]*dot for k in range(3)])
 elbow=[p[k]+direction[k]*along+bend[k]*height for k in range(3)]
 aim(root,middle,sub(elbow,p));m,_=world(names[middle]);aim(middle,end,sub(target,m))
aim('pelvis','spine_01',[0,1,.8])
for n,c,d in [('spine_01','spine_02',[0,1,1.8]),('spine_02','spine_03',[0,1,1.9]),('spine_03','neck_01',[0,1,1.8]),('neck_01','Head',[0,1,-.15])]:aim(n,c,d)
for side,sign in [('l',1),('r',-1)]:
 solve_limb('upperarm_'+side,'lowerarm_'+side,'hand_'+side,[sign*.40,1.0,.714],[sign*.8,1.10,.32])
 aim('hand_'+side,'middle_01_'+side,[0,-.14,1])
 solve_limb('thigh_'+side,'calf_'+side,'foot_'+side,[sign*.37,.28,.17],[sign*.53,.70,.65])
 aim('foot_'+side,'ball_'+side,[0,-.15,1])
 # Curl every finger toward the underside of the handlebar grip.
 for finger in ['index','middle','ring','pinky']:
  for joint,child,d in [('01','02',[0,-.6,1]),('02','03',[0,-1,-.35]),('03','04_leaf',[0,.2,-1])]:
   aim(finger+'_'+joint+'_'+side,finger+'_'+child+'_'+side,d)
 j['nodes'][names['hand_'+side]]['scale']=[.78,.78,.78]
# Reject a pose if wrists or ankles miss their mounting targets.
for side,sign in [('l',1),('r',-1)]:
 for joint,target in [('hand_'+side,[sign*.40,1.0,.714]),('foot_'+side,[sign*.37,.28,.17])]:
  assert length(sub(world(names[joint])[0],target))<.003,(joint,'mount target missed')
def read_accessor(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];stride=v.get('byteStride',struct.calcsize(fmt)*count);start=v.get('byteOffset',0)+a.get('byteOffset',0);return [struct.unpack_from('<'+fmt*count,blob,start+k*stride) for k in range(a['count'])]
def add_indices(values):
 while len(blob)%4:blob.append(0)
 offset=len(blob);blob.extend(struct.pack('<'+'I'*len(values),*values));j['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(values)*4,'target':34963});j['accessors'].append({'bufferView':len(j['bufferViews'])-1,'componentType':5125,'count':len(values),'type':'SCALAR'});return len(j['accessors'])-1
p=j['meshes'][2]['primitives'][0];positions=read_accessor(p['attributes']['POSITION']);indices=[v[0] for v in read_accessor(p['indices'])]
kept=[]
for k in range(0,len(indices),3):
 tri=indices[k:k+3]
 if sum(positions[t][1] for t in tri)/3<1.55:kept.extend(tri)
# Blend existing vertex colours at cuffs and waist to avoid sawtooth triangle edges.
colors=[]
for x,y,z in positions:
 red=max(0,min(1,(y-1.01)/.045))*max(0,min(1,(.69-abs(x))/.035))
 dark=[.025,.037,.047];suit=[.56,.065,.035]
 colors.extend([dark[k]+(suit[k]-dark[k])*red for k in range(3)]+[1])
while len(blob)%4:blob.append(0)
offset=len(blob);blob.extend(struct.pack('<'+'f'*len(colors),*colors));j['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(colors)*4,'target':34962});j['accessors'].append({'bufferView':len(j['bufferViews'])-1,'componentType':5126,'count':len(positions),'type':'VEC4'})
attrs={k:v for k,v in p['attributes'].items() if k in ['POSITION','NORMAL','JOINTS_0','WEIGHTS_0']};attrs['COLOR_0']=len(j['accessors'])-1
j['meshes'][2]['primitives']=[{'attributes':attrs,'indices':add_indices(kept),'material':0}]
j['nodes'][68]['children']=[67,64]
j['materials']=[{'name':'riding-suit','pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'metallicFactor':0,'roughnessFactor':.85}}]
j.pop('images',None);j.pop('textures',None);j.pop('samplers',None);j.pop('animations',None)
# Remove unused face meshes to keep their original material references out of export.
j['meshes']=[j['meshes'][2]];j['nodes'][67]['mesh']=0
for i in [65,66]:j['nodes'][i].pop('mesh',None);j['nodes'][i].pop('skin',None)
j['buffers']=[{'byteLength':len(blob)}];out=json.dumps(j,separators=(',',':')).encode();out+=b' '*((-len(out))%4);blob+=b'\0'*((-len(blob))%4)
Path('public/assets/models/racing-rider.glb').write_bytes(struct.pack('<4sII',b'glTF',2,12+8+len(out)+8+len(blob))+struct.pack('<I4s',len(out),b'JSON')+out+struct.pack('<I4s',len(blob),b'BIN\0')+blob)
Path('public/assets/licenses/quaternius-characters.txt').write_text('\n'.join(line.rstrip() for line in archive.read('Universal Base Characters[Standard]/License_Standard.txt').decode().splitlines()).strip()+'\n')
print('Posed joints:',{name:[round(v,3) for v in world(names[name])[0]] for name in ['pelvis','Head','hand_l','foot_l']})
