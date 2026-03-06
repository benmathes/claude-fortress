# Claude Fortress

## Purpose
Claude acts as a natural-language interface on top of Dwarf Fortress (Classic/ASCII).

## Interaction Model
Two modes, like planning vs. execution:

### Planning Mode (conversation)
- User describes intent in plain English: "I want to dig out a stockpile room" or "what's going on with my dwarves?"
- Claude interprets the current game state from screenshots/terminal output
- Claude explains what's happening, surfaces dangers, suggests options
- Claude asks clarifying questions before executing anything non-trivial

### Execution Mode (Claude drives)
- Once user confirms a plan, Claude translates it to DF keystrokes and executes them
- Claude narrates what it's doing as it does it
- Claude returns to Planning Mode after completing the action

## Strategy/Taste Decisions — Always Pause and Ask
Pause and ask the user on **high-level strategic questions**, not tactical ones. Claude handles tactics autonomously.

**Ask about** (high-level):
- Overall fortress philosophy (e.g. "wealth and trade" vs. "military fortress" vs. "survive at all costs")
- How to respond to major threats or opportunities
- What the fortress should prioritize this season
- Major tradeoffs that shape the whole game arc

**Do NOT ask about** (handle autonomously):
- Which exact tile to dig
- Where to place a specific stockpile
- Corridor width or room dimensions

## How to Ask Strategic Questions
When asking the user a strategy question, always include:
1. **The decision** — what's at stake right now
2. **The options** — 2-3 distinct paths
3. **Tradeoffs and implications** — what each path costs and gains, near-term and long-term

Never present bare options without context. The user needs to understand consequences to make a good call.

## Setup
- Installed via Homebrew: `brew install --cask dwarf-fortress-lmp`
- Classic ASCII version with DFHack
- Requires Rosetta 2 (already installed)

## How Claude Interfaces with the Game
- DF runs in a tmux session named `df` (TEXT/ncurses mode)
- Keystrokes sent via `tmux send-keys -t df`
- Screen captured via `tmux capture-pane -t df -p -e`

## UI Rule: Always Show Full Screen With Colors
When asking the user for any input or decision, ALWAYS show the full DF screen first. No exceptions.

- Command: `tmux capture-pane -t df -p -e` (via Bash tool)
- ANSI color codes pass through Claude Code's terminal — no conversion needed
- Always show the FULL output, never trim or collapse
- Show commentary/questions AFTER the screen output

## Game Instance
- DF app bundle installed by Homebrew cask at: `/Applications/Dwarf Fortress LMP/`

## Learning Loop
When something feels off (dwarves idle, can't control screen, designations not working):
1. **Debug first**: Capture screen, read the current state carefully, check LEARNINGS.md for known issues
2. **Log the fix**: After resolving, update `.claude/LEARNINGS.md` with what went wrong and the fix
3. **Commit learnings**: `git add .claude/LEARNINGS.md && git commit -m "LEARNINGS: <brief>"`

Never repeat the same mistake twice. Always consult LEARNINGS.md at session start.

## Dwarf Fortress Controls Reference
Source: https://dwarffortresswiki.org/index.php/DF2014:Controls

### Essential Navigation
| Key | Action |
|-----|--------|
| Arrow keys | Move cursor / scroll map |
| Shift+Arrow | Fast cursor movement |
| `<` / `>` | Z-level up / down |
| `Space` | Pause / unpause |
| `.` (period) | Advance one tick (while paused) |
| `Tab` | Switch map/menu focus |
| `ESC` | Cancel current menu OR opens Options if at top-level |

### CRITICAL: ESC Behavior
- In a **submenu** (designations, build, etc.): ESC cancels back to game
- At **top-level game view** (no submenu open): ESC opens Options dialog ("Return to Game", "Save", "Abandon")
- To close Options dialog → select "Return to Game" and press Enter
- **Do NOT press ESC twice** — it will open Options and you'll be stuck

### Main Game Menus (press key from game view)
| Key | Menu |
|-----|------|
| `d` | Designations submenu |
| `b` | Build structures |
| `p` | Stockpiles |
| `u` | Unit list |
| `j` | Job list |
| `z` | Status screen |
| `m` | Military |
| `k` | Look at tile |

### Designation Submenu (`d` → ...)
**WARNING: In designation mode, hjkl are NOT cursor keys — they are designation type shortcuts!**
| Key | Designation |
|-----|-------------|
| `d` | Mine (dig out solid rock) |
| `h` | Channel (dig down, creates ramp) |
| `u` | Up staircase |
| `j` | Down staircase |
| `i` | Up/Down staircase |
| `r` | Up ramp |
| `t` | Chop trees |
| `s` | Smooth stone |
| `e` | Engrave stone |
| `x` | Remove designation |
| Arrow keys | Move cursor (ALWAYS use arrows, never hjkl) |
| `Enter` | Anchor selection start / confirm selection |
| `ESC` | Exit designation mode |

### Build Submenu (`b` → ...)
| Key | Structure |
|-----|-----------|
| `w` | Workshop |
| `d` | Trade depot |
| `f` | Furnace |
| `s` | Siege engine |

### Workshop Submenu (`b` → `w` → ...)
| Key | Workshop type |
|-----|---------------|
| `r` | Craftsdwarf's workshop |
| `c` | Carpenter's workshop |
| `m` | Mason's workshop |
| `s` | Still |
| `f` | Farmer's workshop |

### Unit List (`u`)
| Key | Action |
|-----|--------|
| Arrow up/down | Navigate units |
| `z` | Jump map view to selected unit |
| `Enter` | View unit details |

### Tile Symbols Reference
| Symbol | Meaning |
|--------|---------|
| `▓` | Solid unexcavated rock |
| `·` | Open floor / excavated tile |
| `>` | Down staircase (completed) |
| `<` | Up staircase (completed) |
| `▼` | Down ramp or slope |
| `▲` | Up ramp or slope |
| `☺` | Dwarf |
| `σ Æ ÷` | Stone boulders (hauled material) |
| Red `>>` (ANSI 31m) | Pending mine designation |

## Narrative Chronicle Rule
On every conversation compaction, write a narrative-style summary of what has happened in the game so far and append/update it in the **## Chronicle** section below. Write it like a dwarven saga — what was attempted, what succeeded, what perished.

After saving the narrative, always commit and push: `git add CLAUDE.md && git commit -m "Chronicle: <brief description>" && git push`

## Chronicle

### The Founding of Libashedan, "Axestirred" — Early to Mid Spring, Year 1

Seven dwarves arrived in The Eviscerated Spikes, a freezing mountain region with no trees but thick other vegetation. The site chosen was along a river (Jmpdshngl th Slvry C), with a great mountain to the west ripe for delving. The surroundings were calm — for now — though jaguars were rumored to prowl the wilds.

The expedition leader pressed 'e' to embark and selected "Play Now!" — no careful preparation, no extra supplies. Just seven souls and the earth before them.

Upon arrival, the intro scroll read: *"Strike the earth!"* A supply caravan was expected before winter. The dwarves had all of spring and summer to dig lodgings before the cold entombed them.

**The Strategy Chosen: Trading Hub.** With no trees and a freezing climate, the mountain itself would be the fortress's salvation. Stone crafts for the autumn caravan. The seven specialists: Dastot Vúshurist (Miner), Edëm Obokgusgash (Woodworker), Bim Kosothtâmol (Expedition Leader), Athel Dolushdegël (Stoneworker), Thîkut Asmelodshith (Jeweler), Dumat èrithidok (Fish Cleaner), and Lorbam Rigòthodkish (Fisherdwarf).

**The First Delving.** Mining designations were placed along the mountain face. Dastot carved the earth. However, early confusion with DF's designation controls led to an unintended series of *down staircases* rather than a horizontal entrance hall — the miner pressed `j` (Down Stair) instead of flat-mining. The result: a cluster of descending shafts rather than a proper fortress entrance. Stone boulders (σ, Æ, ÷) were carried out as evidence of completed work.

**The Great Idleness.** By 14th Slate (mid-Spring), all seven dwarves stood idle. The surface-level designations had been fully completed — staircases dug, stones hauled. New mining designations were placed on the z-level below, accessible via the newly-dug down-stairs. Dastot and companions briefly rested (Sleep job), then rose again. The mine continued to be worked.

**Current State — Mid Spring, Year 1.** The fortress has a shaft of down-stairs entering the mountain. Some stones have been harvested. No workshops have been built yet. No trade depot. The autumn caravan is coming and the dwarves have not yet begun producing crafts. Time is short.
