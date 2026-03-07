#!/usr/bin/env python3
"""
df_player.py — Local model drives DF keystrokes. Claude supervises.

Usage: python df_player.py [--model mlx-community/Qwen2.5-3B-Instruct-4bit]
"""

import subprocess
import time
import sys
import argparse
import re
from datetime import datetime

MODEL = "mlx-community/Qwen2.5-3B-Instruct-4bit"
TMUX_SESSION = "df"
LOOP_DELAY = 1.0  # seconds between actions

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


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--delay", type=float, default=LOOP_DELAY)
    parser.add_argument("--max-steps", type=int, default=200)
    args = parser.parse_args()

    global MODEL
    MODEL = args.model

    log(f"Starting DF player with model: {MODEL}")
    log("Press Ctrl+C to stop and hand back to Claude")
    print()

    step = 0
    last_key = ""
    consecutive_same = 0

    while step < args.max_steps:
        step += 1
        screen = capture_screen()
        clean = strip_ansi(screen)

        # Safety: detect Options menu and handle it
        if "Return to Game" in clean and "Save Game" in clean:
            log("⚠️  Options menu detected — pressing Enter to return")
            send_key("Enter")
            time.sleep(0.5)
            continue

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
            log("Handing control back to Claude.")
            break

        # Detect model spinning on same key
        if response == last_key:
            consecutive_same += 1
            if consecutive_same >= 4:
                log(f"⚠️  Model stuck pressing {repr(response)} repeatedly — stopping")
                break
        else:
            consecutive_same = 0

        last_key = response
        log(f"  Pressing: {repr(response)}")
        send_key(response)
        time.sleep(args.delay)

    log("Player loop ended.")


if __name__ == "__main__":
    main()
