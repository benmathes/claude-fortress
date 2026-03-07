---
name: play-df
description: Start Dwarf Fortress (if not running) and play autonomously
---

You are playing Dwarf Fortress on behalf of the user. Zero intervention required.

## Step 1: Read context

Read these files:
- `.claude/LEARNINGS.md` — known pitfalls. Follow religiously.
- `chronicle.md` — narrative history of the fortress.
- `strategy.md` — current priorities and game plan.

## Step 2: Ensure DF is running (idempotent)

```bash
tmux has-session -t df 2>/dev/null && echo "SESSION_EXISTS" || echo "NO_SESSION"
```

- **No session** → create and launch:
  ```bash
  tmux new-session -d -s df -x 220 -y 50
  tmux send-keys -t df '"/Applications/Dwarf Fortress LMP/DF v0.47.05/dfhack"' Enter
  sleep 10
  ```
- **Session exists, at DF main menu** → load fortress: `l`, select save, Enter
- **Session exists, active fortress** → continue, no action needed
- **Session exists, Options menu showing** → press Enter to return

## Step 3: Open watch window (only if needed)

```bash
tmux list-clients -t df 2>/dev/null
```

If no writable clients attached, open one:
```bash
osascript -e 'tell application "Terminal" to do script "tmux attach -t df"'
```

## Step 4: Play

Use the execution loop from CLAUDE.md. You drive the keystrokes directly via tmux.

For each action:
1. `tmux capture-pane -t df -p -e` — capture screen
2. Read it. Determine current menu/state.
3. Decide next action based on `strategy.md`
4. `tmux send-keys -t df "KEY" ""` — send keystroke
5. Wait 0.3s, capture again to verify
6. Narrate what happened

**Stop and report if**: flood, siege, death, major event, or after meaningful progress.

## Step 5: Update the record

```bash
git add chronicle.md strategy.md .claude/LEARNINGS.md && git commit -m "Chronicle: <brief>"
```
