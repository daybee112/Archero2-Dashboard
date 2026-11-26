# Mystling reader (on the device)

The profile's Mystling tab and the Expedition preset screen show mystlings as pictures without names.

- `build_refs.py` cuts the reference tiles into `app/mystling-refs.jpg` + `.json` (120px cells, 10 per row).
  Sources: Daby's Mystling inventory video (Nov 25, the common mystlings he picked), the normal white Snow Owl from a
  preset screen, his Egg Demon screenshot. Each entry has a `look` ("normal" or "variant"): one mystling can have
  several looks (Snow Owl: white normal, black variant). Add a new look as a new cell with the same name.
- `match.py` is the prototype the dashboard's JS mirrors:
  - find the green "In use" label on a profile's Mystling tab and take the tile under it;
  - match the tile's picture (frame and stars left out) by colour correlation, shifted ±6%; a match needs 0.8 and a
    0.1 lead over the next mystling, otherwise it's "not one of the common ones" (the card asks, it isn't flagged);
  - the empty egg slot on a preset is flat beige (low saturation, bright);
  - stars by colour, each star 1 to 5: cyan 1, yellow 2, red 3, pink 4, dark red 5; dull grey-gold = not earned (0).
    Pink stars shade into cyan and white. Dark red hasn't been seen on a real screen yet (guessed: red but darker).
- Checked on 2 profile tabs and 7 preset screens (tests/mystlings.py): all names, the empty slot and every star count.
