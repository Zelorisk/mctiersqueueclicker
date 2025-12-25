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
    def __init__(self, check_interval=0.5, confidence=0.7):
        self.check_interval = check_interval
        self.confidence = confidence
        self.running = False

        self.lower_blue = np.array([100, 100, 100])
        self.upper_blue = np.array([130, 255, 255])

        logging.info("Discord Queue Clicker initialized")
        logging.info(f"Check interval: {check_interval}s, Confidence: {confidence}")

    def detect_blue_button(self, screenshot):
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        buttons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 1000 < area < 100000:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                if 1.5 < aspect_ratio < 10:
                    buttons.append((x, y, w, h))

        return buttons

    def check_for_text_near_button(self, screenshot, button_region, keywords):
        try:
            import pytesseract

            x, y, w, h = button_region
            margin = 20
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(screenshot.shape[1], x + w + margin)
            y2 = min(screenshot.shape[0], y + h + margin)

            region = screenshot[y1:y2, x1:x2]
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            text = pytesseract.image_to_string(thresh).lower()

            for keyword in keywords:
                if keyword.lower() in text:
                    return True

        except ImportError:
            logging.warning("pytesseract not available, skipping OCR verification")
        except Exception as e:
            logging.debug(f"OCR error: {e}")

        return False

    def click_button(self, x, y, w, h):
        center_x = x + w // 2
        center_y = y + h // 2

        logging.info(f"Clicking button at ({center_x}, {center_y})")
        pyautogui.click(center_x, center_y)
        logging.info("Button clicked successfully!")

    def take_screenshot(self):
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
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

    clicker = DiscordQueueClicker(check_interval=0.5, confidence=0.7)
    clicker.start_monitoring(
        keywords=["join queue", "queue", "join", "enter queue"], use_ocr=True
    )


if __name__ == "__main__":
    main()
