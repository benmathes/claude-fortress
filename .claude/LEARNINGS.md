# Dwarf Fortress / Claude Fortress — LEARNINGS

Consulted at the start of every session. Updated whenever something breaks.

---

## ESC Opens Options Menu (Not a Cancel)

**Problem**: Pressing `ESC` when at the top-level game view opens the "Dwarf Fortress Options" dialog (Save, Return to Game, Abandon). This froze control for multiple turns.

**Root Cause**: In DF, ESC at top-level = Options. ESC *inside* a submenu = cancel back to game.

**Fix**: If you land in Options by accident, use Arrow down to "Return to Game" and press Enter. Never press ESC twice.

**Signpost**: If screen shows "Return to Game / Save Game / Key Bindings" — you're in Options. Press Enter to return.

---

## `j` in Designation Mode ≠ Job List

**Problem**: Sent `j` thinking it would open Job List, but in designation mode `j` = "Place Down Staircase". Created accidental staircases instead of checking jobs.

**Root Cause**: DF's keybindings are context-sensitive. The same key does different things depending on which menu is open.

**Fix**: Always exit designation mode (ESC) before pressing `j` for Job List. Or use the main game view only for menu navigation.

**Signpost**: After pressing ESC to leave designations, wait for the designation menu panel to disappear from the right side before pressing another key.

---

## Arrow Keys, Not hjkl, for Cursor Movement

**Problem**: Used `h`, `j`, `k`, `l` for cursor movement in designation mode. In DF's designation submenu, these are designation type shortcuts (Channel, Down Stair, etc.), not vim-style cursor keys.

**Fix**: Always use arrow keys for cursor movement in ALL DF contexts.

---

## Game Was Paused — "Idlers: 7" Is Normal When Paused

**Problem**: All 7 dwarves showing "No Job" / idling. Spent significant time debugging designations when the real issue was the game was paused (`*PAUSED*` in top bar).

**Fix**: Always check for `*PAUSED*` in the top bar. Press `Space` to unpause. Dwarves don't work while paused.

**Signpost**: If Idlers shows all 7 and nothing is happening, check top bar for `*PAUSED*` before debugging jobs/designations.

---

## Completed vs. Pending Designations

**Problem**: `>` symbols in the mine were interpreted as pending designations. Actually they are **completed** down staircases.

**Fix**:
- `>` = completed down staircase (white/grey in ANSI)
- Red `>` (ANSI `[31m`) = pending mine designation waiting to be dug
- To verify: look at ANSI color code in `tmux capture-pane` output — `[31m` = red = pending

---

## How to Navigate to a Dwarf's Location

To jump the map view to where a dwarf is standing:
1. Press `u` (Unit List)
2. Arrow to select the dwarf
3. Press `z` (Go to unit)
4. Press `ESC` to close unit list — map is now centered on that dwarf

---

## Checking Job Status

To see what every dwarf is doing:
1. Press `j` from game view (NOT in designation mode)
2. Scroll through the list — shows current job for each dwarf
3. "No Job" = idle; "Sleep" = normal rest; "Mine" = actively digging

---

## DFHack is Unresponsive

`dfhack-run` commands time out with no output. Do not attempt DFHack commands. Use manual keystroke approach only.

---

## Session State Recovery Checklist

When resuming a session or something feels broken:
1. `tmux capture-pane -t df -p -e` — capture current screen
2. Check top bar: paused? what mode?
3. If in Options menu → Arrow to "Return to Game" + Enter
4. If in unknown submenu → ESC once (carefully)
5. Check `*PAUSED*` → Space to unpause if needed
6. Check Idlers count — if > 0, investigate why
7. Press `j` (from game view) to check job list

---

## No Mining Jobs in Queue = Designations Are Suspended or Invalid

**Problem**: All dwarves idle, red `>>` designations visible on map, but `j` (job list) shows NO mining jobs at all — not even unassigned ones.

**Root Cause**: When DF can't path to a designation, it auto-suspends it. Suspended designations still show on map but generate no jobs. Alternatively, down-staircase designations (`d→j`) may be invalid if placed on inaccessible tiles.

**Diagnostic**: Press `j` from main game view. If zero mining jobs appear despite visible red designations, the designations are suspended/invalid — NOT a labor problem.

**Fix options to try next session**:
1. Cancel ALL existing designations (`d → x`, box-select whole area, Enter)
2. Make a brand new **plain mine** designation (`d → d`) on solid rock (`▓`) directly adjacent to where dwarves are standing
3. If that job still doesn't appear in `j` list → pathfinding is broken, check Z-levels
4. If job appears but Dastot ignores it → THEN check his mining labor via `v` from main map

**Signpost**: Job list empty = designation problem. Job list shows mining job = labor/dwarf problem.

---

## `v` from Unit List ≠ Full Labor Profile

**Problem**: Pressing `v` from unit list (`u → v`) opens a limited unit view with only "Thoughts", "Relationships", "Customize" options — NO labor tab.

**Fix**: To see full labor profile, must access via main map `v` key (positions cursor on nearest unit). From unit list, `y` (Customize) only shows nickname/profession rename — not labor.

**Note**: Labor management in DF 0.47 Classic is notoriously hard to reach without DFHack. With DFHack unresponsive, labor checking is very difficult via vanilla menus.

---

## Down Staircase vs. Plain Mine Designations

- `d → d` = plain Mine (digs out a floor tile, leaves walls). Shows as highlighted `▓` in red when pending.
- `d → j` = Down Staircase (carves a `>` staircase going down a Z-level). Shows as red `>` when pending.
- The previous session accidentally created down-staircase designations, not plain mines.
- **Prefer `d → d` (plain mine) for initial digging** — simpler, clearer feedback.

---

## Session State Recovery Checklist (Updated)

When resuming a session or something feels broken:
1. `tmux capture-pane -t df -p -e` — capture current screen
2. Check top bar: paused? what mode? no `*PAUSED*` = running
3. If in Options menu → press Enter to "Return to Game"
4. If in unknown submenu → ESC once carefully (NOT twice — second ESC opens Options)
5. Press `j` (from game view) to check job list — if empty despite designations, they're suspended
6. If starting fresh: cancel old designations, make new `d → d` plain mine on adjacent rock tile
7. Unpause with Space, wait 2-3 real seconds, pause again, check `j` list for new jobs
