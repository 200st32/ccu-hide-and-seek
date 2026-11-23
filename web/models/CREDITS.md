# Models — all CC0 1.0 (public domain)

| File | Source | Author |
|---|---|---|
| `student_m.glb`, `student_f.glb` | Universal Base Characters [Standard] — `Superhero_Male_FullBody` / `Superhero_Female_FullBody` (light skin textures), textures shrunk to 1024 px JPEG | Quaternius — https://quaternius.itch.io/universal-base-characters |
| `hair_m.glb`, `hair_f.glb` | Universal Base Characters [Standard] — `Hair_SimpleParted` / `Hair_Long` (rigged to head bone) | Quaternius |
| `anims.glb` | Universal Animation Library [Standard] — skeleton + Idle, Walk, Jog, Sprint, Jump (start/loop/land), Crouch clips | Quaternius — https://quaternius.itch.io/universal-animation-library |

Rebuild with `python3 tools/pack_character.py <UBC folder> <UAL folder> web/models` (needs Pillow).
Clothes (T-shirt, jeans, shoes) are not in the model: `sac.html` paints them on in the shader from the skin weights.
