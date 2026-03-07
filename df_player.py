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

SYSTEM_PROMPT = """You are a Dwarf Fortress player. You control the game by sending single keystrokes.

RULES:
- Respond with ONLY the key(s) to press, nothing else
- For special keys use: Enter, Escape, Up, Down, Left, Right, Space
- For sequences use comma-separated: d,d  (means press d then d)
- If you see the Options menu (Return to Game / Save Game) → respond: Enter
- If something is seriously wrong that you can't fix → respond: STOP: <reason>
- NEVER use h/j/k/l for cursor movement — always use arrow keys (Up/Down/Left/Right)
- NEVER press Escape twice in a row

CURRENT STRATEGY:
1. Fix mining: cancel suspended designations, place fresh mine with d,d on solid rock (▓)
2. Verify mining job appears in job list (j from main view)
3. Build Craftsdwarf Workshop (b,w,r) for stone crafts
4. Build Trade Depot (b,d) before autumn caravan

KEY REFERENCE (main game view):
- d: Designations menu
- j: Job list (only from main view, NOT in designation mode)
- u: Unit list
- Space: Pause/unpause
- Escape: Exit submenu (careful — at top level opens Options)

DESIGNATION SUBMENU keys:
- d: Plain mine (preferred)
- x: Cancel/remove designation
- Enter: Anchor selection
- Arrow keys: Move cursor

Respond with ONLY the key to press, or STOP: reason."""


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


def ask_model(screen_content, context=""):
    prompt = f"{context}\n\nCURRENT SCREEN:\n{screen_content}\n\nWhat key do you press?"
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
    """Detect main game view by presence of the right-panel menu landmarks."""
    return "Designations" in screen and "Unit List" in screen and "Job List" in screen


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
            response = ask_model(clean, context)
        except subprocess.TimeoutExpired:
            log("⚠️  Model timed out — skipping step")
            continue

        log(f"  Model says: {repr(response)}")

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
        send_key(response)
        time.sleep(args.delay)

    # Final snapshot for chronicle
    log_snapshot(step, strip_ansi(capture_screen()))
    log("Player loop ended. Read session.log to write the chronicle.")


if __name__ == "__main__":
    main()
