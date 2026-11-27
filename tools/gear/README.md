# Gear reader (on the device)

- `build_refs.py` makes `app/gear-refs.jpg` + `.json` (whole gear tiles, 120x144 cells, 10 per row, each with its set and
  slot) and `app/gear-digits.json` (the yellow +N digits 2, 3, 4 as 26x17 masks). Sources: the pilot profile video's Gear
  tabs (Dragoon, Oracle), Daby's Nov 25 Team Info presets (daybee, Heynow, Shoex, Archerojj, Gaga94's Griffin amulet) and
  his Griffin preset clip (Nov 25).
- `find.py` finds whole tiles along a preset's gear row (split at the cream gaps). A row starting at x≈131 (1180-wide)
  begins with the weapon; at x≈156 it begins with the armor (the weapon is scrolled off).
- `feat.py` / `proto.py`: the set is told by the piece's colours once the tile's magenta/red background is left out
  (shares of gold, blue, silver, dark: Griffin gold+black, Oracle silver+blue, Dragoon silver+dark, no gold) plus a picture
  correlation, compared only with references for the same slot. Needs a 0.1 lead, otherwise the slot is left to Claude /
  the review. Checked on 40 preset tiles from references that didn't include them: 40/40.
- Quality: frame colour just under the Lv label and along the bottom edge. Chaotic ~319, Mythic ~349 (every high piece
  shows a gold S, so the S says nothing). Mythic+N: yellow digit on the badge at the bottom; no digit (orange diamond)
  = plain Mythic. "1" isn't in the masks yet: a thin upright stroke is read as 1. Legendary (gold frame) not seen yet.
- Profile Gear tab: weapon, amulet, ring on the left; helmet, armor, boots on the right; positions in `GEAR_PROFILE`
  (590-wide), with the panel's height found by where the frames are.
