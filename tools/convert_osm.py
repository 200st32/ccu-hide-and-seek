"""Convert data/map.osm (OpenStreetMap export) -> data/campus.json used by web/index.html.

Usage:  python3 tools/convert_osm.py
Then paste data/campus.json into the `const DATA = ...` line in web/index.html
(or switch the page to fetch() it once a dev server is in place).
"""
import xml.etree.ElementTree as ET, json, math, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
r = ET.parse(ROOT/'data'/'map.osm').getroot()
nodes = {n.get('id'):(float(n.get('lat')), float(n.get('lon'))) for n in r.iter('node')}
ways = {w.get('id'):w for w in r.findall('way')}
tags = lambda e: {x.get('k'):x.get('v') for x in e.findall('tag')}
# local metric projection; origin = centre of export bounds
b = r.find('bounds').attrib
LAT0 = (float(b['minlat'])+float(b['maxlat']))/2; LON0 = (float(b['minlon'])+float(b['maxlon']))/2
KX = 111320*math.cos(math.radians(LAT0)); KZ = 110540
def P(nid):
    la, lo = nodes[nid]; return [round((lo-LON0)*KX, 1), round(-(la-LAT0)*KZ, 1)]
def wpts(w): return [P(n.get('ref')) for n in w.findall('nd') if n.get('ref') in nodes]

def rings(rel, role):
    segs = [wpts(ways[m.get('ref')]) for m in rel.findall('member') if m.get('type')=='way' and m.get('role')==role and m.get('ref') in ways]
    out = []
    while segs:
        ring = segs.pop(0)
        changed = True
        while ring[0] != ring[-1] and changed:
            changed = False
            for i, s in enumerate(segs):
                if s[0] == ring[-1]: ring += s[1:]
                elif s[-1] == ring[-1]: ring += s[::-1][1:]
                elif s[-1] == ring[0]: ring = s + ring[1:]
                elif s[0] == ring[0]: ring = s[::-1] + ring[1:]
                else: continue
                segs.pop(i); changed = True; break
        out.append(ring)
    return out

LEVEL_DEFAULT = {'dormitory':5, 'university':4}
out = {'origin':[LAT0, LON0], 'bounds':None, 'buildings':[], 'water':[], 'areas':[], 'roads':[], 'waterways':[], 'treerows':[]}
bx = [(float(b['minlon'])-LON0)*KX, (float(b['maxlon'])-LON0)*KX]; bz = [-(float(b['maxlat'])-LAT0)*KZ, -(float(b['minlat'])-LAT0)*KZ]
out['bounds'] = [round(bx[0]), round(bz[0]), round(bx[1]), round(bz[1])]

def add_area(t, outer, holes=[]):
    name = t.get('name', ''); en = t.get('name:en', '')
    if 'building' in t:
        lv = t.get('building:levels')
        lv = int(float(lv)) if lv else (2 if name in ('體育館','禮堂','游泳池') else LEVEL_DEFAULT.get(t['building'], 3))
        h = 9 if name in ('體育館','禮堂') else (7 if name == '游泳池' else None)
        out['buildings'].append({'n':name, 'e':en, 'f':lv, 'h':h, 'p':outer, 'holes':holes})
    elif t.get('natural') == 'water':
        out['water'].append({'n':name, 'p':outer, 'holes':holes})
    else:
        kind = None
        if t.get('leisure') == 'track': kind = 'track'
        elif t.get('leisure') in ('pitch','golf_course'): kind = 'pitch'
        elif t.get('leisure') in ('sports_centre','swimming_pool'): kind = 'pool' if 'swimming' in t.get('leisure','') else 'paved'
        elif t.get('amenity') in ('parking','motorcycle_parking','bicycle_parking'): kind = 'parking'
        elif t.get('natural') in ('wood',) or t.get('landuse') == 'forest': kind = 'wood'
        elif t.get('natural') == 'grassland' or t.get('landuse') == 'grass': kind = 'grass'
        if kind: out['areas'].append({'k':kind, 'n':name, 'p':outer, 'holes':holes})

ROADW = {'tertiary':10, 'unclassified':7, 'living_street':7, 'service':5, 'pedestrian':8, 'footway':2.5, 'steps':3, 'path':2, 'cycleway':2.5}
for w in ways.values():
    t = tags(w); pts = wpts(w)
    if len(pts) < 2: continue
    closed = pts[0] == pts[-1]
    if 'highway' in t and t['highway'] in ROADW and not (closed and t.get('area') == 'yes'):
        out['roads'].append({'n':t.get('name',''), 'k':t['highway'], 'w':ROADW[t['highway']], 'p':pts})
    elif 'waterway' in t:
        out['waterways'].append({'n':t.get('name',''), 'w':6 if t['waterway']=='drain' else 4, 'p':pts})
    elif t.get('natural') == 'tree_row':
        out['treerows'].append(pts)
    elif closed:
        add_area(t, pts)
for rel in r.findall('relation'):
    t = tags(rel)
    if t.get('type') != 'multipolygon': continue
    outers = rings(rel, 'outer'); inners = rings(rel, 'inner')
    for o in outers:
        if len(o) > 3: add_area(t, o, [i for i in inners if len(i) > 3])
# site relation 理學院一館: name its untagged buildings
for rel in r.findall('relation'):
    t = tags(rel)
    if t.get('type') == 'site' and t.get('name') == '理學院一館':
        for m in rel.findall('member'):
            if m.get('type') == 'way' and m.get('ref') in ways:
                pts = wpts(ways[m.get('ref')])
                for bd in out['buildings']:
                    if bd['p'] == pts and not bd['n']: bd['n'] = '理學院一館'; bd['e'] = 'College of Science 1'
json.dump(out, open(ROOT/'data'/'campus.json','w'), ensure_ascii=False, separators=(',',':'))
print('bounds', out['bounds'], {k:len(v) for k,v in out.items() if isinstance(v, list)})
print('unnamed buildings', sum(1 for b in out['buildings'] if not b['n']))
