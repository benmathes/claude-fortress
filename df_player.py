#!/usr/bin/env python3
"""
df_player.py — Local model drives DF keystrokes. Claude supervises.

Usage: python df_player.py [--model mlx-community/Qwen2.5-7B-Instruct-4bit]
"""

import subprocess
import time
import sys
import argparse
import re
from datetime import datetime
from pathlib import Path

MODEL = "mlx-community/Qwen2.5-7B-Instruct-4bit"
TMUX_SESSION = "df"
LOOP_DELAY = 1.0  # seconds between actions
SESSION_LOG = Path(__file__).parent / "session.log"
SNAPSHOT_EVERY = 10  # capture full screen to log every N steps
HISTORY_LEN = 10  # how many recent actions to include in each prompt
STRATEGY_FILE = Path(__file__).parent / "strategy.md" 

SYSTEM_PROMPT = """You are playing Dwarf Fortress Classic. You control the game one keystroke at a time.

OUTPUT FORMAT: Respond with ONLY a single key or comma-separated sequence. Nothing else. No explanation.
Special keys: Enter, Escape, Up, Down, Left, Right, Space
Sequences: d,d means press d then d

CRITICAL RULES:
- NEVER use h/j/k/l for cursor movement — use Up/Down/Left/Right arrows only
- NEVER use Escape. The script handles all navigation back to the main view automatically.
- After pressing j to check jobs, if the list is empty, your next action should be d (to go to designations) — not Escape.

WHEN YOU SEE THE JOB LIST (screen shows dwarf names with 'No Job', 'Hunt', 'Mine' etc):
- If NO Mine jobs exist → press d (opens designations). Do NOT press Escape.
- If Mine jobs exist → press Space (unpause so dwarves work)
- You are always shown the MAIN GAME VIEW. Do not try to open menus you are already in.

YOUR STATE MACHINE — follow this decision tree every step:

STEP 1 — CHECK JOBS: press j to open job list
  - If job list shows mining jobs → press Escape, then Space to unpause
  - If job list is EMPTY → there are no valid mining designations. Press Escape, go to STEP 2.

STEP 2 — CANCEL OLD DESIGNATIONS: press d to open designations menu, then x for remove/cancel
  - Move cursor with arrow keys over any red ">>" tiles on the map
  - Press Enter to start selection, move to cover the area, press Enter to confirm
  - Press Escape when done cancelling

STEP 3 — PLACE NEW MINE (multi-step sequence):
  a. Press d → opens designation menu (right panel changes)
  b. Press d → enters Mine designation mode (cursor appears on map)
  c. Use arrow keys to move cursor onto a solid rock tile (▓) near the surface entrance
  d. Press Enter → anchors the start corner
  e. Press Enter again → confirms the designation (you'll see it highlighted in red)
  f. Press Escape → exits designation mode back to main view
  IMPORTANT: You must press Enter TWICE to place a designation. d,d alone does nothing.

STEP 4 — VERIFY: press j to check job list again
  - If mining jobs now appear → press Escape, press Space to unpause, let them work
  - If still empty → the rock is unreachable, try a different tile (STEP 3 again)

STEP 5 — ONCE MINING WORKS, build workshops:
  - Craftsdwarf workshop: b, w, r — place it, press Enter to confirm
  - Trade depot: b, d — place it on open ground

What is your next single action?"""


def capture_screen():
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", TMUX_SESSION, "-p", "-e"],
        capture_output=True, text=True
    )
    return result.stdout


def send_key(key):
    """Send a key or comma-separated sequence of keys to tmux."""
    keys = [k.strip() for k in key.split(",")]
    for k in keys:
        subprocess.run(
            ["tmux", "send-keys", "-t", TMUX_SESSION, k, ""],
            capture_output=True
        )
        time.sleep(0.15)


def ask_model(screen_content, history, context=""):
    strategy = STRATEGY_FILE.read_text() if STRATEGY_FILE.exists() else ""
    history_text = "\n".join(f"  {i+1}. {h}" for i, h in enumerate(history)) or "  (none yet)"
    prompt = f"""{context}

CURRENT STRATEGY:
{strategy}

RECENT ACTIONS (oldest to newest):
{history_text}

CURRENT SCREEN:
{screen_content}

What is your next single action?"""
    result = subprocess.run(
        ["llm", "-m", MODEL, "-s", SYSTEM_PROMPT, prompt],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout.strip()


def strip_ansi(text):
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


def is_paused(screen):
    return "*PAUSED*" in screen


def is_main_view(screen):
    """Accept main game view OR job list (both are valid states for model decisions)."""
    # Main game view: right panel has Designations + Unit List
    if ("d: Designations" in screen or "Designations" in screen) and "Unit List" in screen:
        return True
    # Job list view: bottom shows "v: View Unit  z: Go to Unit"
    if "v: View Unit" in screen and "z: Go to Unit" in screen:
        return True
    return False


def ensure_main_view():
    """Press Escape until we're back at the main game view. Max 5 attempts."""
    for _ in range(5):
        screen = strip_ansi(capture_screen())
        if "Return to Game" in screen and "Save Game" in screen:
            log("\u26a0\ufe0f  Options menu \u2014 pressing Enter")
            send_key("Enter")
            time.sleep(0.5)
        elif is_main_view(screen):
            return True
        else:
            send_key("Escape")
            time.sleep(0.4)
    return is_main_view(strip_ansi(capture_screen()))


def log(msg, also_file=True):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    if also_file:
        with open(SESSION_LOG, "a") as f:
            f.write(line + "\n")


def log_snapshot(step, screen):
    """Write a full screen snapshot to the log for chronicle purposes."""
    ts = datetime.now().strftime("%H:%M:%S")
    with open(SESSION_LOG, "a") as f:
        f.write(f"\n--- SCREEN SNAPSHOT step={step} at {ts} ---\n")
        f.write(screen)
        f.write(f"--- END SNAPSHOT ---\n\n")


def main():
    global MODEL
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--delay", type=float, default=LOOP_DELAY)
    parser.add_argument("--max-steps", type=int, default=200)
    args = parser.parse_args()
    MODEL = args.model

    # Start fresh log for this session
    with open(SESSION_LOG, "w") as f:
        f.write(f"=== DF Player Session {datetime.now().isoformat()} ===\n")
        f.write(f"Model: {MODEL}\n\n")

    log(f"Starting DF player with model: {MODEL}")
    log(f"Session log: {SESSION_LOG}")
    log("Press Ctrl+C to stop and hand back to Claude")
    print()

    step = 0
    last_key = ""
    consecutive_same = 0
    history = []  # rolling list of recent actions

    while step < args.max_steps:
        step += 1
        screen = capture_screen()
        clean = strip_ansi(screen)

        # Periodic screen snapshot for chronicle
        if step % SNAPSHOT_EVERY == 1:
            log_snapshot(step, clean)

        # Normalize to main game view before asking the model anything
        if not ensure_main_view():
            log("⚠️  Could not reach main view after 5 attempts — stopping")
            break

        context = f"Step {step}. Last key pressed: {last_key or 'none'}"
        if is_paused(clean):
            context += " [GAME IS PAUSED]"

        log(f"Step {step} — querying model...")
        try:
            response = ask_model(clean, history[-HISTORY_LEN:], context)
        except subprocess.TimeoutExpired:
            log("⚠️  Model timed out — skipping step")
            continue

        log(f"  Model says: {repr(response)}")

        # Don't let the model navigate with Escape — the script owns that
        if response.lower() in ("escape", "esc"):
            log("  (intercepted Escape — script handles navigation, skipping)")
            history.append("tried Escape (intercepted)")
            time.sleep(args.delay)
            continue

        if response.upper().startswith("STOP"):
            reason = response[5:].strip(": ")
            log(f"🛑 Model requested stop: {reason}")
            log_snapshot(step, clean)
            log("Handing control back to Claude.")
            break

        # Detect model spinning on same key
        if response == last_key:
            consecutive_same += 1
            if consecutive_same >= 4:
                log(f"⚠️  Model stuck pressing {repr(response)} repeatedly — stopping")
                log_snapshot(step, clean)
                break
        else:
            consecutive_same = 0

        last_key = response
        log(f"  Pressing: {repr(response)}")
        history.append(f"pressed {repr(response)}")
        send_key(response)
        time.sleep(args.delay)

    # Final snapshot for chronicle
    log_snapshot(step, strip_ansi(capture_screen()))
    log("Player loop ended. Read session.log to write the chronicle.")


if __name__ == "__main__":
    main()
