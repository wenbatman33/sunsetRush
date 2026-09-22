# Derive surfaces from Kenney's CC0 Racing Kit. All vertices come from the original model.
import json,struct,pathlib,copy
b=pathlib.Path('public/assets/models/roadStraight.glb').read_bytes();l=struct.unpack_from('<I',b,12)[0];source=json.loads(b[20:20+l]);raw=b[28+l:]
def values(ai):
 a=source['accessors'][ai];v=source['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];fmt={5126:'f',5123:'H',5125:'I'}[a['componentType']];st=v.get('byteStride',struct.calcsize(fmt)*n);off=v.get('byteOffset',0)+a.get('byteOffset',0);return [struct.unpack_from('<'+fmt*n,raw,off+i*st)for i in range(a['count'])]
for name,material in [('asphalt',2),('lane-mark',1)]:
 p=source['meshes'][0]['primitives'][material];positions=values(p['attributes']['POSITION']);indices=[a[0]for a in values(p['indices'])]
 if material==1:indices=[x for i in range(0,len(indices),3)if all(positions[k][0]>.5 and positions[k][1]>.019 for k in indices[i:i+3])for x in indices[i:i+3]]
 used=sorted(set(indices));remap={old:new for new,old in enumerate(used)};binary=bytearray();j={'asset':{'version':'2.0','copyright':'Kenney CC0, Racing Kit. Extracted original road surface / edge strip.'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'mesh':0}],'meshes':[{'primitives':[]}],'materials':[copy.deepcopy(source['materials'][material])],'buffers':[],'bufferViews':[],'accessors':[]}
 def add(data,typ,component,fmt):
  while len(binary)%4:binary.append(0)
  off=len(binary)
  for tup in data:binary.extend(struct.pack('<'+fmt*len(tup),*tup))
  view=len(j['bufferViews']);j['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(binary)-off})
  a={'bufferView':view,'componentType':component,'count':len(data),'type':typ}
  if typ=='VEC3':a.update(min=[min(x[k]for x in data)for k in range(3)],max=[max(x[k]for x in data)for k in range(3)])
  idx=len(j['accessors']);j['accessors'].append(a);return idx
 attrs={}
 for key,ai in p['attributes'].items():
  a=source['accessors'][ai];v=values(ai);attrs[key]=add([v[i]for i in used],a['type'],5126,'f')
 ix=add([(remap[i],)for i in indices],'SCALAR',5123,'H');j['meshes'][0]['primitives']=[{'attributes':attrs,'indices':ix,'material':0}];j['buffers']=[{'byteLength':len(binary)}]
 js=json.dumps(j,separators=(',',':')).encode();js+=b' '*((-len(js))%4);binary+=b'\0'*((-len(binary))%4)
 pathlib.Path('public/assets/models/'+name+'.glb').write_bytes(struct.pack('<4sII',b'glTF',2,28+len(js)+len(binary))+struct.pack('<I4s',len(js),b'JSON')+js+struct.pack('<I4s',len(binary),b'BIN\0')+binary)
