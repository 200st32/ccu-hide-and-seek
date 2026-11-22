# Game design — CCU Hide & Seek

## Concept
Online multiplayer hide-and-seek in the browser, third-person 3D, on the 中正大學 campus. Rounds of ~3–5 minutes,
friends join with a 4-letter room code. Minimum 4 players.

## Round flow
| Phase | Length | What happens |
|---|---|---|
| Lobby | — | Join by room code; host starts when ≥4 players |
| Hide | 30 s | Hiders move; seekers frozen with a black screen + countdown |
| Seek | 3 min | Seekers hunt; get close and press Space to catch |
| Results | — | Seekers win if all caught; hiders win if anyone survives. Roles rotate |

Seekers: 1 for 4–5 players, 2 for 6–9, 3 for 10+.
Caught hiders: classic (spectate) or infection (become seekers) — undecided, infection suits small groups.

## Hiding mechanics
1. Line of sight — walls, floors and doors hide players naturally in 3D.
2. Hiding spots — bushes, parked cars, furniture; a hider in cover is only visible to seekers within ~2 m.
3. Crouch — smaller, slower, quieter.
4. Footsteps — sprinting makes noise / short-lived footprints; walking is silent.
5. Seeker ping — every 30 s, rough direction to the nearest hider.
6. Optional hider taunt — reveal position for bonus points.
7. Indoors — enterable rooms, doors (an open door is a clue), multiple floors, darker interiors.

## Scoring
Hider +1 per 10 s survived, +5 for surviving the round. Seeker +3 per catch, +5 for catching everyone.

## Architecture
```
Browser (Three.js)  ←─ WebSocket ─→  Node.js (Colyseus)
 renders, sends input only             rooms, authoritative positions,
                                       catches, timers, per-player visibility filtering
```
