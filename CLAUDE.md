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

## Narrative Chronicle Rule
On every conversation compaction, write a narrative-style summary of what has happened in the game so far and append/update it in the **## Chronicle** section below. Write it like a dwarven saga — what was attempted, what succeeded, what perished.

## Chronicle

### The Founding of Libashedan, "Axestirred" — Early Spring, Year 1

Seven dwarves arrived in The Eviscerated Spikes, a freezing mountain region with no trees but thick other vegetation. The site chosen was along a river (Jmpdshngl th Slvry C), with a great mountain to the west ripe for delving. The surroundings were calm — for now — though jaguars were rumored to prowl the wilds.

The expedition leader pressed 'e' to embark and selected "Play Now!" — no careful preparation, no extra supplies. Just seven souls and the earth before them.

Upon arrival, the intro scroll read: *"Strike the earth!"* A supply caravan was expected before winter. The dwarves had all of spring and summer to dig lodgings before the cold entombed them.

Claude opened the Designations menu and was navigating toward the mountain face to begin mining — the first step toward shelter — when the session was interrupted.
