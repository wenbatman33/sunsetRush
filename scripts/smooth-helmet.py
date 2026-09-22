"""Smooth normals on the existing untextured CC0 helmet without changing geometry."""
import json,struct,math
from pathlib import Path
p=Path('public/assets/models/helmet.glb');raw=bytearray(p.read_bytes());n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);base=20+n+8
for mesh in j['meshes']:
 for prim in mesh['primitives']:
  pa=j['accessors'][prim['attributes']['POSITION']];na=j['accessors'][prim['attributes']['NORMAL']];pv=j['bufferViews'][pa['bufferView']];nv=j['bufferViews'][na['bufferView']];points=[];groups={}
  for i in range(pa['count']):
   pos=struct.unpack_from('<3h',raw,base+pv.get('byteOffset',0)+pa.get('byteOffset',0)+i*pv.get('byteStride',12));key=tuple(round(x,5) for x in pos);off=base+nv.get('byteOffset',0)+na.get('byteOffset',0)+i*nv.get('byteStride',12);normal=struct.unpack_from('<3h',raw,off);points.append((key,off));groups.setdefault(key,[]).append(normal)
  for key,off in points:
   total=[sum(v[k] for v in groups[key]) for k in range(3)];length=math.sqrt(sum(v*v for v in total))
   if length>1e-8:struct.pack_into('<3h',raw,off,*(round(v/length*32767) for v in total))
p.write_bytes(raw)
