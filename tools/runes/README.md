# Rune icon references

`app/rune-refs.jpg` is a grid of reference rune icons (120 px cells, 10 per row) and `app/rune-refs.json` names each
cell and its type. The page matches rune icons against these on the device (see "Rune icons" in `app/index.html`).

Made from Daby's recordings of rune popups (Nov 23, 2026): 46 icons covering 43 runes, plus 105 small icons cut
from real profile Runes and Team Info preset screens (each checked by eye), so matching works at the size runes
actually appear, on Mythic red frames, and behind some glow. Cells marked `small: true` in the JSON are those. Potion Spring, Meteor Split and Orbital Orb
were added Nov 24 (popups plus 4 small icons). Nov 26: Echo Scythe added (popup + 1 small) and one small cell that was
cut as Pulsing Orb relabelled to Echo Scythe (it was an Echo Scythe); small cells added for Vine Bind, Rootguard,
Plant Crit, Plant Summon, Equinox Bloom and Orbital Orb from Daby's preset screenshots.

Scripts (Python prototypes, paths point at the original frame folders):
- `find_icon.py`: finds the icon tile in a popup screenshot.
- `build_refs.py`: crops and labels the references; `refs.json` lists the source frame for each.
- `match.py`, `run_screen.py`: the prototype matcher the page's version was ported from.

To add a rune: crop its popup icon the same way, append the cell to the grid and its name/type to `rune-refs.json`.

Matching rules (in the page): a name needs a score of at least 0.6, names for each type are chosen together
(each rune once, scored against leaving the slot blank), and a slot keeps its name only if any other choice
costs at least 0.05. Otherwise it stays blank.

Sprite rule (per Daby): Melee Sprite and Healing Sprite are nearly identical at screen size. Two sprite icons on
one screen are both equipped (named the better-scoring way round); a single sprite icon is taken as Healing Sprite.

## Twinborn runes (not handled yet, per Daby 2026-11-24)

A Twinborn rune is two Mythic runes of the same slot type combined into one, with both effects. On the profile Runes
ring it shows as one icon that **alternates between the two runes' icons**, with a **number badge on each side**
(left and right of the frame, e.g. "3" and "3"). Normal runes have no side badges on that screen.

Example: Hago26's third Enhancement slot, two Meteor runes (Giant Meteor + Potion Magnet). The Nov 23 video caught
the Potion Magnet frame, his Nov 24 screenshot caught the Giant Meteor frame, so each read was "right" for its frame.

Today the matcher reads whichever icon is showing in that still, so a Twinborn slot is saved as one of its two
runes. Where to start:
- detect the two side badges (small round badges just outside the frame at mid-height) and flag the slot as Twinborn;
- in a video, collect the slot's icon from every still of the Runes screen (the icon alternates) and keep both names;
- read the side badge numbers (likely the two runes' +N levels; confirm with Daby);
- store it as one slot holding two runes, quality Mythic, and count both for inventory and build analysis.
Twinborn runes are rare at ArchAcademy's power level.
