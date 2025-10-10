'''
Screen recording with python

just need pynput and pandas installed
'''

import time
import pandas as pd
from pynput import keyboard, mouse

# Globals for use in monitoring and recording keyboard
events = []
stop_flag = False  # shared flag

def now():
    return time.time()

# --- Keyboard callbacks ---
def on_key_press(key):
    global stop_flag
    # Track modifier states
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        on_key_press.ctrl_pressed = True
    elif key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
        on_key_press.alt_pressed = True
    # Stop if Ctrl + Alt pressed together
    if on_key_press.ctrl_pressed and on_key_press.alt_pressed:
        print("\nCtrl + Alt detected — stopping recording...")
        stop_flag = True
        return False  # stop keyboard listener
    else:
        pass  # non-character key
    # Record normal key press
    try:
        key_str = key.char
    except AttributeError:
        key_str = str(key)
    events.append({
        "timestamp": now(),
        "device": "keyboard",
        "event": "press",
        "detail": key_str,
        "x": None,
        "y": None
    })

on_key_press.ctrl_pressed = False
on_key_press.alt_pressed = False

def on_key_release(key):
    global stop_flag
    # Reset ctrl state
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        on_key_press.ctrl_pressed = False
    try:
        key_str = key.char
    except AttributeError:
        key_str = str(key)
    events.append({
        "timestamp": now(),
        "device": "keyboard",
        "event": "release",
        "detail": key_str,
        "x": None,
        "y": None
    })


# Mouse event callbacks
def on_move(x, y):
    events.append({
        "timestamp": now(),
        "device": "mouse",
        "event": "move",
        "detail": "",
        "x": x,
        "y": y
    })

def on_click(x, y, button, pressed):
    # Explicitly distinguish left/right clicks
    btn = str(button).split(".")[-1]  # e.g. "Button.left" → "left"
    event_type = f"{btn}_{'press' if pressed else 'release'}"
    events.append({
        "timestamp": now(),
        "device": "mouse",
        "event": event_type,
        "detail": "",
        "x": x,
        "y": y
    })

def on_scroll(x, y, dx, dy):
    events.append({
        "timestamp": now(),
        "device": "mouse",
        "event": "scroll",
        "detail": f"dx={dx},dy={dy}",
        "x": x,
        "y": y
    })

def record(duration_seconds=10,time_sleep=0.005):
    """Records mouse + keyboard input until Ctrl+Alt is pressed or time expires."""
    global stop_flag, events, on_key_press
    events.clear()
    stop_flag = False
    kb_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    ms_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    kb_listener.start()
    ms_listener.start()
    print(f"Recording started for up to {duration_seconds} seconds.")
    print("Press Ctrl+Alt to stop early.\n")
    start = now()
    while not stop_flag and (now() - start < duration_seconds):
        time.sleep(time_sleep)
    # Stop listeners safely
    kb_listener.stop()
    ms_listener.stop()
    on_key_press.ctrl_pressed = False
    on_key_press.alt_pressed = False
    time.sleep(0.05)
    df = pd.DataFrame(events)
    if stop_flag:
        # getting rid of last two rows if they recorded Key.alt_l or Key.ctrl_l
        l2 = df.index > df.shape[0]-2
        kv = df['detail'].isin(['Key.alt_l','Key.ctrl_l'])
        ac = l2 & kv
        df = df[~ac].copy()
        stop_flag = False
    # if first record is enter in terminal, getting rid of that
    if df['detail'][0] == 'Key.enter':
        df = df.tail(-1).reset_index(drop=True)
    print(f"\nRecording stopped. {len(df)} events captured.")
    events.clear()
    return df

def replay(df, speed=1.0):
    """
    Replay the recorded keyboard and mouse events stored in a pandas DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        Must have columns: ['timestamp', 'device', 'event', 'detail', 'x', 'y']
    speed : float
        Playback speed multiplier (1.0 = real time, 2.0 = twice as fast, etc.)
    """
    kb = keyboard.Controller()
    ms = mouse.Controller()
    # Sort just in case
    df = df.sort_values("timestamp").reset_index(drop=True)
    # Use relative timing between events
    start_time = df.loc[0, "timestamp"]
    print("Replaying events...")
    for i, row in df.iterrows():
        if i > 0:
            # Sleep for time difference between events (scaled by speed)
            dt = (row["timestamp"] - df.loc[i-1, "timestamp"]) / speed
            if dt > 0:
                time.sleep(dt)
        if row["device"] == "mouse":
            # Handle mouse actions
            if row["event"] == "move":
                if not pd.isna(row["x"]) and not pd.isna(row["y"]):
                    ms.position = (row["x"], row["y"])
            elif "left_press" in row["event"]:
                ms.press(mouse.Button.left)
            elif "left_release" in row["event"]:
                ms.release(mouse.Button.left)
            elif "right_press" in row["event"]:
                ms.press(mouse.Button.right)
            elif "right_release" in row["event"]:
                ms.release(mouse.Button.right)
            elif row["event"] == "scroll":
                # Parse scroll deltas if available
                try:
                    parts = row["detail"].split(",")
                    dx = int(parts[0].split("=")[1])
                    dy = int(parts[1].split("=")[1])
                    ms.scroll(dx, dy)
                except Exception:
                    pass
        elif row["device"] == "keyboard":
            # Handle keyboard actions
            key_str = row["detail"]
            try:
                # Try normal printable character
                k = key_str if len(key_str) == 1 else getattr(keyboard.Key, key_str.split(".")[-1], None)
                if k is not None:
                    if row["event"] == "press":
                        kb.press(k)
                    elif row["event"] == "release":
                        kb.release(k)
            except Exception:
                pass
    print("Replay finished.")