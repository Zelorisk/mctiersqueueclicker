#!/usr/bin/env python3

import logging
import subprocess
import time

import cv2
import mss
import numpy as np
import pyautogui

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

TEMPLATE_PATH = "button_template.png"
MATCH_THRESHOLD = 0.75


def load_template():
    t = cv2.imread(TEMPLATE_PATH)
    if t is None:
        raise FileNotFoundError(f"template not found: {TEMPLATE_PATH}")
    return t


def find_button(screenshot, template):
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= MATCH_THRESHOLD:
        th, tw = template.shape[:2]
        cx = max_loc[0] + tw // 2
        cy = max_loc[1] + th // 2
        return cx, cy, max_val
    return None


def main():
    print("=" * 60)
    print("discord queue auto-clicker")
    print("=" * 60)
    print("starting in 5 seconds... switch to discord now!")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    print()

    template = load_template()
    logging.info(f"template loaded: {template.shape[1]}x{template.shape[0]}px")

    sct = mss.mss()
    monitor = sct.monitors[1]
    screen_size = pyautogui.size()
    scale = monitor["width"] / screen_size.width
    logging.info(f"screen {screen_size.width}x{screen_size.height}, scale {scale}")

    pyautogui.PAUSE = 0.0
    pyautogui.FAILSAFE = True

    caffeinate = subprocess.Popen(["caffeinate", "-d"])
    logging.info("monitoring for join queue button... ctrl+c to stop")

    last_log = 0
    try:
        while True:
            frame = sct.grab(monitor)
            screenshot = cv2.cvtColor(np.array(frame), cv2.COLOR_BGRA2BGR)

            match = find_button(screenshot, template)

            now = time.time()
            if now - last_log > 5:
                if match:
                    logging.info(f"button visible at ({match[0]}, {match[1]}) confidence={match[2]:.2f}")
                else:
                    logging.info("scanning... button not found")
                last_log = now

            if match:
                cx, cy, conf = match
                sx = int(cx * scale)
                sy = int(cy * scale)
                logging.info(f"clicking join queue at ({sx}, {sy}) conf={conf:.2f}")
                subprocess.run(["osascript", "-e", 'tell application "Discord" to activate'], capture_output=True)
                time.sleep(0.1)
                pyautogui.moveTo(sx, sy, duration=0.05)
                pyautogui.click()
                logging.info("clicked!")
                time.sleep(2)

            time.sleep(0.1)

    except KeyboardInterrupt:
        logging.info("stopped")
    finally:
        caffeinate.terminate()


if __name__ == "__main__":
    main()
