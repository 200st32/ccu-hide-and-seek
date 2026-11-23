#!/usr/bin/env python3
"""Pack the CC0 Quaternius character + animations into small .glb files for web/sac.html.

Sources (CC0, by Quaternius — free "Standard" downloads from itch.io, not kept in the repo):
  Universal Base Characters [Standard]  https://quaternius.itch.io/universal-base-characters
  Universal Animation Library [Standard] https://quaternius.itch.io/universal-animation-library

Usage:
  python3 tools/pack_character.py <UBC folder> <UAL folder> web/models

Writes  student.glb  (body + eyes + eyebrows, light skin, 1024 px JPEG textures)
        hair.glb     (Hair_SimpleParted, rigged to the same skeleton)
        anims.glb    (skeleton nodes + only the clips the game uses)
"""
import io, json, os, struct, sys
from PIL import Image

CLIPS = ['Idle_Loop', 'Walk_Loop', 'Jog_Fwd_Loop', 'Sprint_Loop', 'Jump_Start', 'Jump_Loop', 'Jump_Land',
         'Crouch_Idle_Loop', 'Crouch_Fwd_Loop']
TEX = 1024


def read_gltf(path):
    g = json.load(open(path))
    base = os.path.dirname(path)
    bins = [open(os.path.join(base, b['uri']), 'rb').read() for b in g['buffers']]
    return g, bins, base


def read_glb(path):
    b = open(path, 'rb').read()
    n = struct.unpack('<I', b[12:16])[0]
    g = json.loads(b[20:20 + n])
    o = 20 + n
    m = struct.unpack('<I', b[o:o + 4])[0]
    return g, [b[o + 8:o + 8 + m]]


def view_bytes(g, bins, vi):
    v = g['bufferViews'][vi]
    o = v.get('byteOffset', 0)
    return bins[v['buffer']][o:o + v['byteLength']]


def jpeg(path_or_img, size=TEX, q=85):
    im = path_or_img if isinstance(path_or_img, Image.Image) else Image.open(path_or_img)
    im = im.convert('RGB')
    if max(im.size) > size: im = im.resize((size, size * im.size[1] // im.size[0]), Image.LANCZOS)
    out = io.BytesIO(); im.save(out, 'JPEG', quality=q, optimize=True)
    return out.getvalue()


class Writer:
    """Collects bufferViews into one binary chunk."""
    def __init__(self): self.data = bytearray(); self.views = []

    def add(self, blob, target=None, stride=None):
        while len(self.data) % 4: self.data.append(0)
        v = {'buffer': 0, 'byteOffset': len(self.data), 'byteLength': len(blob)}
        if target: v['target'] = target
        if stride: v['byteStride'] = stride
        self.data += blob; self.views.append(v)
        return len(self.views) - 1

    def save(self, g, path):
        while len(self.data) % 4: self.data.append(0)
        g['bufferViews'] = self.views
        g['buffers'] = [{'byteLength': len(self.data)}]
        js = json.dumps(g, separators=(',', ':')).encode()
        js += b' ' * (-len(js) % 4)
        out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(self.data))
        out += struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(self.data), 0x004E4942) + bytes(self.data)
        open(path, 'wb').write(out)
        print(f'{path}: {len(out) / 1e6:.2f} MB')


def repack(g, bins, images, path, keep_accessors=None):
    """Copy every accessor's bufferView into a fresh buffer; images replaced by `images` (list of jpeg bytes)."""
    w = Writer(); vmap = {}
    for a in g.get('accessors', []):
        vi = a['bufferView']
        if vi not in vmap:
            v = g['bufferViews'][vi]
            vmap[vi] = w.add(view_bytes(g, bins, vi), v.get('target'), v.get('byteStride'))
        a['bufferView'] = vmap[vi]
    if images is not None:
        g['images'] = [{'mimeType': 'image/jpeg', 'bufferView': w.add(b)} for b in images]
        g['samplers'] = g.get('samplers') or [{}]
    w.save(g, path)


def main(ubc, ual, out):
    os.makedirs(out, exist_ok=True)
    bc = os.path.join(ubc, 'Base Characters')
    # --- body: swap the dark skin for the light one, drop the roughness map, shrink textures ---
    g, bins, base = read_gltf(os.path.join(bc, 'Godot - UE', 'Superhero_Male_FullBody.gltf'))
    src = {'T_Superhero_Male_Dark': os.path.join(bc, 'Textures', 'T_Superhero_Male_Ligh.png')}
    imgs = []
    for im in g['images']:
        p = src.get(im['name'], os.path.join(base, im['uri']))
        if not os.path.exists(p): p = os.path.join(bc, 'Textures', os.path.basename(im['uri']).replace('_png.png', '.png'))
        small = 'Eye' in im['name']
        imgs.append(jpeg(p, 256 if small else TEX))
    for m in g['materials']:
        pbr = m['pbrMetallicRoughness']
        if 'metallicRoughnessTexture' in pbr: del pbr['metallicRoughnessTexture']; pbr['roughnessFactor'] = 0.62
    for t in g.get('textures', []): t['sampler'] = 0
    repack(g, bins, imgs, os.path.join(out, 'student.glb'))
    # --- hair ---
    hp = os.path.join(ubc, 'Hairstyles', 'Rigged to Head Bone', 'glTF (Godot -Unreal)', 'Hair_SimpleParted.gltf')
    g, bins, base = read_gltf(hp)
    imgs = [jpeg(os.path.join(base, im['uri']), 512) for im in g['images']]
    for t in g.get('textures', []): t['sampler'] = 0
    repack(g, bins, imgs, os.path.join(out, 'hair.glb'))
    # --- animations: keep the skeleton nodes and the listed clips only ---
    g, bins = read_glb(os.path.join(ual, 'Unreal-Godot', 'UAL1_Standard.glb'))
    anims = [a for a in g['animations'] if a['name'] in CLIPS]
    missing = set(CLIPS) - {a['name'] for a in anims}
    if missing: sys.exit(f'missing clips: {missing}')
    acc = sorted({s[k] for a in anims for s in a['samplers'] for k in ('input', 'output')})
    amap = {old: i for i, old in enumerate(acc)}
    accessors = [g['accessors'][i] for i in acc]
    for a in anims:
        for s in a['samplers']: s['input'] = amap[s['input']]; s['output'] = amap[s['output']]
    nodes = [dict(n) for n in g['nodes']]
    for n in nodes: n.pop('mesh', None); n.pop('skin', None)
    ng = {'asset': g['asset'], 'scene': 0, 'scenes': g['scenes'], 'nodes': nodes, 'accessors': accessors, 'animations': anims,
          'bufferViews': g['bufferViews']}
    repack(ng, bins, None, os.path.join(out, 'anims.glb'))


if __name__ == '__main__':
    if len(sys.argv) != 4: sys.exit(__doc__)
    main(*sys.argv[1:])
