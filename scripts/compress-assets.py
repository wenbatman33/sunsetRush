"""Recreate lossless model/HDR downloads and WebP road maps. Requires Pillow."""
from pathlib import Path
import gzip
from PIL import Image
root = Path(__file__).resolve().parents[1]
for path in list((root/'public/assets/models').glob('*.glb')) + [root/'public/assets/textures/sky.hdr']:
    Path(str(path)+'.gz').write_bytes(gzip.compress(path.read_bytes(), compresslevel=9, mtime=0))
for path in (root/'public/assets/textures').glob('*.jpg'):
    Image.open(path).save(path.with_suffix('.webp'), quality=88, method=6)
