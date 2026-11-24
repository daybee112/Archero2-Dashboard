# Rune icon references

`app/rune-refs.jpg` is a grid of reference rune icons (120 px cells, 10 per row) and `app/rune-refs.json` names each
cell and its type. The page matches rune icons against these on the device (see "Rune icons" in `app/index.html`).

Made from Daby's recordings of rune popups (Nov 23, 2026): 46 icons covering 43 runes. Still missing (no reference,
so they always stay blank): Potion Spring, Orbital Orb, Meteor Split, Echo Scythe (all Etched).

Scripts (Python prototypes, paths point at the original frame folders):
- `find_icon.py`: finds the icon tile in a popup screenshot.
- `build_refs.py`: crops and labels the references; `refs.json` lists the source frame for each.
- `match.py`, `run_screen.py`: the prototype matcher the page's version was ported from.

To add a rune: crop its popup icon the same way, append the cell to the grid and its name/type to `rune-refs.json`.
