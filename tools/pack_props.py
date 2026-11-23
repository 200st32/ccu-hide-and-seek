#!/usr/bin/env python3
"""Pack Poly Haven (CC0) glTF downloads into single .glb files with small JPEG textures for web/sac.html.

Download a model's 1k glTF from https://polyhaven.com/models (or https://api.polyhaven.com/files/<id>), then:
  python3 tools/pack_props.py <folder with <id>_1k.gltf> web/models/<id>.glb [texture px, default 512]
"""
import glob, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pack_character import read_gltf, repack, jpeg


def main(folder, out, size=512):
    path = glob.glob(os.path.join(folder, '*.gltf'))[0]
    g, bins, base = read_gltf(path)
    imgs = [jpeg(os.path.join(base, im['uri']), int(size), 88) for im in g.get('images', [])]
    for t in g.get('textures', []): t['sampler'] = 0
    g['samplers'] = [{}]
    repack(g, bins, imgs, out)


if __name__ == '__main__':
    if len(sys.argv) < 3: sys.exit(__doc__)
    main(*sys.argv[1:])
