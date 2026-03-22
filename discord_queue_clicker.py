#!/usr/bin/env python3

import ctypes
import logging
import platform
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

IS_MAC = platform.system() == "Darwin"
IS_WIN = platform.system() == "Windows"

TEMPLATE_PATH = "button_template.png"
MATCH_THRESHOLD = 0.75


def prevent_sleep():
    if IS_MAC:
        return subprocess.Popen(["caffeinate", "-d"])
    if IS_WIN:
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)
    return None


def allow_sleep(proc):
    if IS_MAC and proc:
        proc.terminate()
    if IS_WIN:
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)


def focus_discord():
    if IS_MAC:
        subprocess.run(
            ["osascript", "-e", 'tell application "Discord" to activate'],
            capture_output=True,
        )
        time.sleep(0.1)


def find_join_queue_button(screenshot, template):
    th, tw = template.shape[:2]
    sh, sw = screenshot.shape[:2]

    best_conf = 0
    best_matches = []
    best_tw = tw
    best_th = th

    for scale in np.linspace(0.4, 2.5, 32):
        rw = int(tw * scale)
        rh = int(th * scale)
        if rw > sw or rh > sh or rw < 10 or rh < 10:
            continue
        resized = cv2.resize(template, (rw, rh))
        result = cv2.matchTemplate(screenshot, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        if max_val < MATCH_THRESHOLD:
            continue

        locations = np.where(result >= MATCH_THRESHOLD)
        matches = list(zip(locations[1].tolist(), locations[0].tolist()))
        if max_val > best_conf:
            best_conf = max_val
            best_matches = [(x, y, result[y, x]) for x, y in matches]
            best_tw, best_th = rw, rh

    if not best_matches:
        return None

    merged = []
    for x, y, conf in sorted(best_matches, key=lambda m: m[1], reverse=True):
        if not any(abs(x - mx) < best_tw and abs(y - my) < best_th for mx, my, _ in merged):
            merged.append((x, y, conf))

    x, y, conf = max(merged, key=lambda m: m[1])
    cx = x + best_tw // 2
    cy = y + best_th // 2
    logging.info(f"{len(merged)} match(es) at scale {best_tw/tw:.2f}x — bottommost ({cx},{cy}) conf={conf:.2f}")
    return cx, cy


def main():
    print("=" * 60)
    print("discord queue auto-clicker")
    print("=" * 60)
    print("starting in 5 seconds... switch to discord now!")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    print()

    template = cv2.imread(TEMPLATE_PATH)
    if template is None:
        raise FileNotFoundError(f"missing {TEMPLATE_PATH} — put it in the same folder as this script")
    logging.info(f"template loaded: {template.shape[1]}x{template.shape[0]}px")

    sct = mss.mss()
    monitor = sct.monitors[1]
    screen_size = pyautogui.size()
    scale = monitor["width"] / screen_size.width
    logging.info(f"screen {screen_size.width}x{screen_size.height}, scale {scale}")

    pyautogui.PAUSE = 0.0
    pyautogui.FAILSAFE = True

    sleep_proc = prevent_sleep()
    logging.info("monitoring for join queue button... ctrl+c to stop")

    last_log = 0
    try:
        while True:
            frame = sct.grab(monitor)
            screenshot = cv2.cvtColor(np.array(frame), cv2.COLOR_BGRA2BGR)

            match = find_join_queue_button(screenshot, template)

            now = time.time()
            if now - last_log > 5 and match is None:
                logging.info("scanning...")
                last_log = now

            if match:
                cx, cy = match
                sx = int(cx * scale)
                sy = int(cy * scale)
                focus_discord()
                pyautogui.moveTo(sx, sy, duration=0.05)
                pyautogui.click()
                logging.info(f"clicked at ({sx}, {sy})")
                time.sleep(2)

            time.sleep(0.1)

    except KeyboardInterrupt:
        logging.info("stopped")
    finally:
        allow_sleep(sleep_proc)


if __name__ == "__main__":
    main()
