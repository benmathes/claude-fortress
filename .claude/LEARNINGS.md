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
