---
name: play-df
description: Start Dwarf Fortress (if not running) and play autonomously
disable-model-invocation: true
allowed-tools: Bash, Read
---

You are now playing Dwarf Fortress on behalf of the user. They want zero intervention — do everything yourself.

## Step 1: Ensure DF is running in tmux

Check if the `df` tmux session already exists:
`!`tmux has-session -t df 2>&1 && echo "RUNNING" || echo "NOT_RUNNING"``

**If NOT_RUNNING**: Launch DF now:
```bash
tmux new-session -d -s df -x 220 -y 50
tmux send-keys -t df '"/Applications/Dwarf Fortress LMP/DF v0.47.05/dfhack"' Enter
```
Wait 8 seconds for DF to boot before proceeding.

**If RUNNING**: Capture the current screen and continue from the current game state.

## Step 2: Read context

Read these files before doing anything in-game:
- `.claude/LEARNINGS.md` — known pitfalls and navigation rules. Follow these religiously.
- `chronicle.md` — narrative history of the fortress. Understand where we came from.
- `strategy.md` — current strategic intent and priorities. This is your game plan.
- `CLAUDE.md` — controls reference and interaction model.

The strategy tells you what to do. The chronicle tells you what has happened. The learnings tell you how not to break things.

## Step 3: Capture screen and orient

Run: `tmux capture-pane -t df -p -e`

Determine:
- Are we at the DF main menu? If so, load the existing fortress.
- Are we in an active fortress?
- Is the game paused? (`*PAUSED*` in top bar)
- What mode is the screen in (main view, a submenu, options dialog)?

## Step 4: Play

Follow the **Interaction Model** from CLAUDE.md — Planning Mode then Execution Mode.

### Execution loop
1. Capture screen: `tmux capture-pane -t df -p -e`
2. Decide action based on what you read in `strategy.md`
3. Send keystrokes: `tmux send-keys -t df "KEY" && sleep 0.3`
4. Capture screen again to verify the result
5. Narrate what happened
6. Repeat

### When to stop and report
- If something unexpected and significant happens (flood, siege, dwarf death, major discovery)
- After meaningful progress on whatever `strategy.md` says is the current focus
- After ~20 minutes of play or a natural stopping point

## Step 5: Update the record

After playing:
- Append to `chronicle.md` — what happened this session in narrative dwarven-saga style
- Update `strategy.md` — revise priorities based on what changed, what was accomplished, what new threats or opportunities emerged
- Update `.claude/LEARNINGS.md` if you discovered any new navigation pitfalls or fixes

Commit: `git add chronicle.md strategy.md .claude/LEARNINGS.md && git commit -m "Chronicle: <brief>"`
