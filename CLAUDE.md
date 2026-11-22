# CCU Hide & Seek (中正大學 躲貓貓)

A multiplayer 3D hide-and-seek game set on the 國立中正大學 (National Chung Cheng University) campus.
Owner: Kai. Read `docs/DESIGN.md` for the full game design.

## Current state (prototype, step 1 done)
- `web/index.html` — single-file browser game: Three.js 0.170 (ES module from jsdelivr CDN), **WebGL** renderer.
  Open it through any static server (e.g. `python3 -m http.server` from `web/`) — not via `file://`.
  - Third-person character (box-built humanoid), WASD/arrows, Shift sprint (stamina bar), Space jump
    (crouch → rise → fall → landing squash animation), mouse-look with pointer lock + edge-turn fallback, scroll zoom,
    touch joystick on mobile.
  - Real-world scale: **1 unit = 1 m**, person 1.75 m, storey 3.6 m, jog 4.5 m/s, sprint 7.5 m/s, jump ~0.9 m.
  - Campus built from OpenStreetMap data (embedded as `const DATA = {...}` in the page):
    24 buildings extruded from real footprints × `building:levels`, 122 roads/paths as ribbons, 寧靜湖 + stream
    (water blocks movement; roads crossing water act as bridges), grass/wood/track/pitch/parking areas,
    OSM tree rows, scattered trees, bushes (no collider → future hiding spots), parked cars (solid), 校門 at the south end of 中正大道.
  - Collision: point-in-polygon push-out for buildings, circle colliders (trees, cars, gate), water slide-back.
  - Camera raycasts against buildings so it never clips into walls.
  - HUD: location name, minimap drawn from the same data, OSM attribution (required by ODbL — keep it).
- `data/map.osm` — OSM export (core campus only, ~700 × 930 m). `data/campus.json` — converted output.
- `tools/convert_osm.py` — map.osm → campus.json (local metric projection centred on the export bounds; x = east, z = south).

## Decisions already made
- Browser game; third-person camera; low-poly art style; UI is bilingual (中文 + English).
- Multiplayer: authoritative **Node.js + Colyseus** server, room codes, ≥4 players; server decides positions/catches and
  only sends each client what it may see (anti-cheat).
- Physics stays on CPU (own collision now, **Rapier** WASM later for interiors/stairs). No GPU physics.
- Rendering: switch to Three.js `WebGPURenderer` (WebGL2 fallback) only when the scene gets heavy (e.g. Minecraft import).
- Don't copy Google Street View images or Minecraft/Mojang textures into the game.

## Next task (in progress): one detailed building
Kai wants to scope down to **a single building** with real exterior + interior as the play area (rest of campus = scenery).
Candidate: **活動中心** (4F, footprint `學生活動中心` in campus.json); alternatives 共同教室 (easiest), 圖書資訊大樓 (hardest).
Waiting on references from Kai: exterior photos, floor plans / 逃生避難圖 / interior photos, or a Minecraft build of CCU
(if provided: parse `.mca`/`.schem` with amulet-core or anvil-parser, greedy-mesh, colour by block type, align to OSM).
Plan: exterior facade → floor slabs, corridors, rooms, doors, stairs → furniture/hiding spots → restrict play area.

## Roadmap after that
1. Multiplayer: Node + Colyseus server, lobby with room codes, players see each other.
2. Roles & phases: lobby → hide (30 s, seekers blind) → seek (3 min) → results; tag to catch.
3. Hiding mechanics: line of sight, bushes/cars/furniture cover, crouch, footstep sounds, seeker ping.
4. Scoring, polish, deploy (Render / Fly.io).

## Conventions
- Kai prefers step-by-step progress with something runnable after each step, and concise explanations.
- Keep tunables as named constants at the top of their section (FLOOR, WALK, SPRINT, JUMP, SENS_X, ...).
- Note: the folder name contains `&` — always quote paths in shell commands.
