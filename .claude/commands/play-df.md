---
name: play-df
description: Start Dwarf Fortress (if not running) and play autonomously via local model
disable-model-invocation: true
allowed-tools: Bash, Read
---

You are the supervisor for an autonomous Dwarf Fortress player. A fast local model (Qwen2.5-3B) drives the keystrokes. You orient, launch, monitor, and update the record afterward.

## Step 1: Read context

Read these files before doing anything:
- `.claude/LEARNINGS.md` — known pitfalls. Follow religiously.
- `chronicle.md` — narrative history of the fortress.
- `strategy.md` — current priorities and game plan.

## Step 2: Ensure DF is running (idempotent)

Run this to check state:
```bash
tmux has-session -t df 2>/dev/null && echo "SESSION_EXISTS" || echo "NO_SESSION"
```

Then capture the screen to determine what's actually showing:
```bash
tmux capture-pane -t df -p -e 2>/dev/null
```

**Decision tree:**
- **No tmux session** → create session and launch DF:
  ```bash
  tmux new-session -d -s df -x 220 -y 50
  tmux send-keys -t df '"/Applications/Dwarf Fortress LMP/DF v0.47.05/dfhack"' Enter
  sleep 10
  ```
- **Session exists, screen shows DF main menu** → load the fortress: press `l`, select the save, Enter
- **Session exists, screen shows active fortress** → continue from current state, no action needed
- **Session exists, screen shows Options menu** → press Enter to return to game

## Step 3: Open a watch window (only if needed)

Check if a watch window is already attached:
```bash
tmux list-clients -t df 2>/dev/null
```

If no clients are listed (or only read-only ones), open a new terminal:
```bash
osascript -e 'tell application "Terminal" to do script "tmux attach -t df"'
```

If clients already exist, skip this step — don't open a redundant tab.

## Step 4: Launch the local model player

```bash
cd /Users/benmathes/coding/claude-fortress && python df_player.py
```

The player loop runs until it calls STOP, gets stuck, or hits max steps. Watch the output here for what the model is doing.

## Step 5: After the player stops — update the record

Capture the final screen state, then:
- Append to `chronicle.md` — what happened this session in narrative dwarven-saga style
- Update `strategy.md` — revise priorities based on what changed
- Update `.claude/LEARNINGS.md` if new pitfalls were discovered

```bash
git add chronicle.md strategy.md .claude/LEARNINGS.md && git commit -m "Chronicle: <brief>"
```
