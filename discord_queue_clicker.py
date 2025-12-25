#!/usr/bin/env python3

import logging
import time
from datetime import datetime

import cv2
import numpy as np
import pyautogui

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("discord_clicker.log"), logging.StreamHandler()],
)


class DiscordQueueClicker:
    def __init__(self, check_interval=0.5, confidence=0.7, debug=False):
        self.check_interval = check_interval
        self.confidence = confidence
        self.running = False
        self.debug = debug
        self.scale_factor = 1.0

        self.lower_blue = np.array([110, 150, 150])
        self.upper_blue = np.array([130, 255, 255])

        pyautogui.PAUSE = 0.05
        pyautogui.FAILSAFE = True

        logging.info("Discord Queue Clicker initialized")
        logging.info(f"Check interval: {check_interval}s, Confidence: {confidence}")
        logging.info(f"Screen size: {pyautogui.size()}")
        logging.info(f"Debug mode: {debug}")

    def detect_blue_button(self, screenshot):
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        buttons = []
        screen_height = screenshot.shape[0]
        screen_width = screenshot.shape[1]

        for contour in contours:
            area = cv2.contourArea(contour)
            if 2000 < area < 50000:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0

                if y < screen_height * 0.2:
                    continue

                if y > screen_height * 0.9:
                    continue

                if 2.0 < aspect_ratio < 8.0 and h > 25 and w > 100:
                    buttons.append((x, y, w, h))

        return buttons

    def check_for_text_near_button(self, screenshot, button_region, keywords):
        try:
            import pytesseract

            x, y, w, h = button_region
            margin = 5
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(screenshot.shape[1], x + w + margin)
            y2 = min(screenshot.shape[0], y + h + margin)

            region = screenshot[y1:y2, x1:x2]

            if self.debug:
                cv2.imwrite("debug_ocr_region.png", region)
                logging.info(f"OCR region saved: {x1},{y1} to {x2},{y2}")

            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            text = pytesseract.image_to_string(thresh).lower()

            logging.info(f"OCR detected text: '{text.strip()}'")

            for keyword in keywords:
                if keyword.lower() in text:
                    logging.info(f"Keyword '{keyword}' matched!")
                    return True

        except ImportError:
            logging.warning("pytesseract not available, skipping OCR verification")
        except Exception as e:
            logging.debug(f"OCR error: {e}")

        return False

    def click_button(self, x, y, w, h):
        center_x = int((x + w // 2) * self.scale_factor)
        center_y = int((y + h // 2) * self.scale_factor)

        logging.info(f"Button region: x={x}, y={y}, w={w}, h={h}")
        logging.info(f"Scale factor: {self.scale_factor}")
        logging.info(f"Scaled click position: ({center_x}, {center_y})")

        current_pos = pyautogui.position()
        logging.info(f"Current mouse position: {current_pos}")

        current_x, current_y = pyautogui.position()
        pyautogui.moveTo(center_x, center_y, duration=0.1)
        time.sleep(0.05)

        pyautogui.click(center_x, center_y, duration=0.2)
        time.sleep(0.1)

        pyautogui.mouseDown(center_x, center_y)
        time.sleep(0.05)
        pyautogui.mouseUp(center_x, center_y)

        logging.info("Button clicked successfully!")

    def take_screenshot(self):
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

        screen_size = pyautogui.size()
        screenshot_height, screenshot_width = screenshot_bgr.shape[:2]

        if screenshot_width != screen_size.width:
            self.scale_factor = screen_size.width / screenshot_width
            if self.debug:
                logging.info(f"Screenshot size: {screenshot_width}x{screenshot_height}")
                logging.info(
                    f"PyAutoGUI screen size: {screen_size.width}x{screen_size.height}"
                )
                logging.info(f"Scale factor detected: {self.scale_factor}")

        return screenshot_bgr

    def start_monitoring(self, keywords=None, use_ocr=True):
        if keywords is None:
            keywords = ["join queue", "queue", "join"]

        self.running = True
        logging.info("Starting to monitor for queue button...")
        logging.info(f"Looking for keywords: {keywords}")
        logging.info("Press Ctrl+C to stop")

        try:
            while self.running:
                screenshot = self.take_screenshot()
                buttons = self.detect_blue_button(screenshot)

                if buttons:
                    logging.debug(f"Found {len(buttons)} potential button(s)")

                    if self.debug:
                        debug_img = screenshot.copy()
                        for button in buttons:
                            x, y, w, h = button
                            cv2.rectangle(
                                debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2
                            )
                            cv2.circle(
                                debug_img, (x + w // 2, y + h // 2), 5, (0, 0, 255), -1
                            )
                        cv2.imwrite("debug_detection.png", debug_img)
                        logging.info("Debug image saved to debug_detection.png")

                    for button in buttons:
                        x, y, w, h = button

                        if use_ocr:
                            if self.check_for_text_near_button(
                                screenshot, button, keywords
                            ):
                                self.click_button(x, y, w, h)
                                logging.info("Queue button found and clicked!")
                                return True
                        else:
                            self.click_button(x, y, w, h)
                            logging.info("Blue button clicked (OCR disabled)")
                            return True

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logging.info("\nMonitoring stopped by user")
            self.running = False
        except Exception as e:
            logging.error(f"Error during monitoring: {e}")
            raise

    def stop(self):
        self.running = False
        logging.info("Monitoring stopped")


def main():
    print("=" * 60)
    print("Discord Queue Auto-Clicker")
    print("=" * 60)
    print()
    print("Instructions:")
    print("1. Open Discord and navigate to the desired channel")
    print("2. Make sure the channel is visible on screen")
    print("3. Run this script")
    print("4. The script will monitor for a blue 'join queue' button")
    print("5. When found, it will automatically click it")
    print()
    print("Configuration:")
    print("- Check interval: 0.5 seconds (faster detection)")
    print("- OCR verification: Enabled (more accurate)")
    print()
    print("Press Ctrl+C to stop at any time")
    print("=" * 60)
    print()

    print("Starting in 5 seconds... Position your Discord window now!")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    print()

    clicker = DiscordQueueClicker(check_interval=0.5, confidence=0.7, debug=True)
    clicker.start_monitoring(
        keywords=["join queue", "queue", "join", "enter queue"], use_ocr=True
    )


if __name__ == "__main__":
    main()
