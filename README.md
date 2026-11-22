# 中正大學 躲貓貓 · CCU Hide & Seek

Multiplayer 3D hide-and-seek on the National Chung Cheng University campus (prototype).

## Run
```bash
cd "web"
python3 -m http.server 8000
# open http://localhost:8000
```

## Layout
```
web/index.html            the game (Three.js, single file, campus data embedded)
data/map.osm              OpenStreetMap export of the core campus
data/campus.json          converted map data
data/campus_preview.png   2D plot of campus.json
tools/convert_osm.py      map.osm -> campus.json
docs/DESIGN.md            game design
CLAUDE.md                 project context for Claude Code
```

Map data © OpenStreetMap contributors (ODbL).
