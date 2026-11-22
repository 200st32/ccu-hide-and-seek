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
  `sac.html` already supports it behind `?gpu`.
- Don't copy Google Street View images or Minecraft/Mojang textures into the game.

## Step 2 done: 活動中心 as the play area — `web/sac.html`
Scoped down to **one building**, built from Kai's photos in `student_activity_center/` (incl. `inside_image/2F_layout.jpeg`,
the official floor map) + Kai's description. Standalone page (index.html links to it); same controls/character as index.html.
- Layout follows Kai's `student_activity_center/drawn_layout.png` (plan view; x = east, z = south, lake 寧靜湖 to the south,
  中正大道 景觀大橋 crossing the lake to the east at street level = 3F). Floors `L = [0,4,8,12,16]`, 4 m storeys.
  - Main entrance = a block sticking out at the NE corner (3F, street level, face looking NE). Inside: 3F hall → straight stair
    (12 m wide) down to a half-round 2F landing → fan flight down to the 1F plaza. The 3F floor's SW strip is the bridge in front
    of the entrance (over the landing), from the 麗文 side door / 3F north gallery (NW) to the 健康中心 door (SE).
    Code uses an entrance frame: `UV(u, v)`, u along the entrance face, v inward. 2F passage from the north gallery to the landing
    (solid underneath: no 1F path on the cafeteria side of the stair).
  - Red-arrow path: 1F walkway between the grand stair and the east block (z MPZ..EZ). 熱音社 + 打擊樂社 (1F of the east block,
    under 健康中心) open onto it; it continues into the 1F hallway under the entrance hall/stairs, which leads to 小吃街.
  - East block (1F–3F): 1F music clubs (+ a club opening west), 3F 健康中心 + 學生諮商中心.
    Walkways outside the east block: 3F along its north + west faces (entrance bridge ↔ lake-side 3F walkway), 2F along its
    west face (↔ lake-side 2F walkway); a 2F link deck (the fan's south-east slice, over the red-arrow
    path) joins it to the grand stair's 2F landing.
  - West block (1F–4F, x −76..−28, scaled from the drawing): 演藝廳 sticks out north (z −39.5..−15): back stage (outside door) |
    stage | 22 raked rows from the 3F door down to 1F. Then a corridor along the theatre wall + a band of rooms, the open-air slot (2F west gallery high
    end → ground outside the west face, nothing above it), another band of rooms + corridor, and the south row: club |
    indoor stair 1F–4F (square, switchback) | club | restaurant (1F–2F, half-round glass bay facing the lake).
    The slot is open to the sky: 1F path on its north part, slope (2F → outside) on its south part. 1F rooms there are offices; others clubs.
  - Stairs built by `switchback()` (two straight flights per storey + turn landing): the "circle stair" 1F–4F at the west end of
    the atrium (6.4 m wide, half-round turn, stone walls instead of railings) and the square indoor stair on the south face.
    The square stair goes up to the roof: a small brick stair house (door north) opens onto a rooftop plaza over the
    west block's south rooms (low 1.1 m wall around it, planters + benches). HUD shows `RF` there.
  - One diagonal 3F bridge (green in the drawing) from the north gallery to
    the south-west corner. South side has no rooms: open 2F/3F walkways facing the lake. 1F north = 小吃街.
- Collision: every solid is a vertical prism (polygon + holes, y0..y1 or y0..top(x,z) for ramps); player = cylinder
  (R 0.35, HEAD 1.8, STEP 0.5) with push-out, ground snapping, ceilings; helix colliders available (unused now); uniform grid.
  Stairs are drawn as steps but walked as smooth ramps. Camera ray-marches the same colliders.
- Rendering: all static geometry merged per material (~38k tris); signs packed into one canvas atlas; atrium roof
  modules, roof columns, trees, bushes are InstancedMesh. WebGL by default; `?gpu` loads the three.webgpu build
  (WebGPURenderer → Dawn in Chrome, WebGL2 fallback; no AO on that path).
  - Look: sRGB output + ACES tone mapping; Poly Haven CC0 HDRI (`web/tex/sky_1k.hdr`) as environment + sky; N8AO
    (n8ao@2.0.1, needs postprocessing@6.39.4 in the import map) via EffectComposer → OutputPass, half-res.
  - Textures: CC0 only, in `web/tex/` with `CREDITS.md` (ambientCG mosaic recoloured to terracotta, concrete; HDRI).
    Never use the Google Maps reference images as textures (see `student_activity_center/REFERENCE_NOTES.md`).
  - Atrium roof: sawtooth glass + steel space frame (8 instanced modules) on tall round columns; entrance has a flat
    teal-glass canopy (camera occluder) with the 活動中心 band on the beam over the doors.
  - Camera: pitch −1.05..1.25; every camera sample is lifted ≥ 0.5 m above the floor under it; signs, railings and
    glass are not camera occluders (`cam:false`).
  - Performance: pixel ratio cap 1.5 + dynamic resolution (drops once, floor 1.0, if frames > 18.5 ms); one shadow
    light with a tight shadow camera fitted to `SHADOW_BOX`, 2048 map. Measured on Kai's MacBook (Intel Iris Plus),
    1280×760: ≥ 60 fps with AO, ~120 draw calls (settles at pixel ratio 1.0; ~32–39 fps at a fixed 1.5).
- Debug: `?test` walks 50 scripted routes (every stair/bridge/exit + wall/railing blocks) and prints PASS/FAIL;
  `?shot=x,y,z,yaw,pitch,dist[&nohud]` places player/camera for screenshots. Headless Chrome works with `file://`
  + `--allow-file-access-from-files --use-angle=swiftshader --enable-unsafe-swiftshader`.
  F3 / `?stats` = stats overlay (fps, draw calls, triangles, textures). `?bench=x,y,z,yaw,pitch,dist` = 6 s warm-up +
  6 s measured camera spin, prints fps/p95/draw calls (use real GPU: `--use-angle=metal --disable-gpu-vsync
  --disable-frame-rate-limit --disable-renderer-backgrounding`). Overrides: `?pr= ?shadowmap= ?aos= ?aod= ?noao ?noenv
  ?aoview` (AO buffer only).
- Approximations to revisit with Kai: room sizes (from the drawing's scale), 2F under the entrance hall (solid now), 演藝廳 interior,
  4F extent (north + west only), real club names. No door leaves yet (openings only).

## Roadmap after that
0. Polish 活動中心 from Kai's feedback (more photos of 1F offices / 4F / 演藝廳 would help); campus around it as scenery.
1. Multiplayer: Node + Colyseus server, lobby with room codes, players see each other.
2. Roles & phases: lobby → hide (30 s, seekers blind) → seek (3 min) → results; tag to catch.
3. Hiding mechanics: line of sight, bushes/cars/furniture cover, crouch, footstep sounds, seeker ping.
4. Scoring, polish, deploy (Render / Fly.io).

## Conventions
- Kai prefers step-by-step progress with something runnable after each step, and concise explanations.
- Keep tunables as named constants at the top of their section (FLOOR, WALK, SPRINT, JUMP, SENS_X, ...).
- Note: the folder name contains `&` — always quote paths in shell commands.
