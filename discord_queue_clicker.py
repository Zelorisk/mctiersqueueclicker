#!/usr/bin/env python3
"""
Discord Queue Auto-Clicker
Monitors the screen for a blue "join queue" button and clicks it automatically.
"""

import pyautogui
import cv2
import numpy as np
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_clicker.log'),
        logging.StreamHandler()
    ]
)

class DiscordQueueClicker:
    def __init__(self, check_interval=0.5, confidence=0.7):
        """
        Initialize the Discord Queue Clicker.

        Args:
            check_interval: Time in seconds between screen checks (lower = faster detection)
            confidence: Confidence level for button detection (0.0-1.0)
        """
        self.check_interval = check_interval
        self.confidence = confidence
        self.running = False

        # Define blue color range for button detection (in HSV)
        # Discord's blurple/blue buttons
        self.lower_blue = np.array([100, 100, 100])
        self.upper_blue = np.array([130, 255, 255])

        logging.info("Discord Queue Clicker initialized")
        logging.info(f"Check interval: {check_interval}s, Confidence: {confidence}")

    def detect_blue_button(self, screenshot):
        """
        Detect blue colored regions in the screenshot.

        Args:
            screenshot: Screenshot as numpy array (BGR format)

        Returns:
            List of bounding boxes [(x, y, w, h), ...] for blue regions
        """
        # Convert BGR to HSV
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)

        # Create mask for blue colors
        mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        buttons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            # Filter by size - Discord buttons are reasonably sized
            if 1000 < area < 100000:
                x, y, w, h = cv2.boundingRect(contour)
                # Check aspect ratio - buttons are wider than tall
                aspect_ratio = w / h if h > 0 else 0
                if 1.5 < aspect_ratio < 10:
                    buttons.append((x, y, w, h))

        return buttons

    def check_for_text_near_button(self, screenshot, button_region, keywords):
        """
        Check if any keywords appear near the button region using OCR.

        Args:
            screenshot: Full screenshot
            button_region: (x, y, w, h) tuple
            keywords: List of keywords to search for

        Returns:
            Boolean indicating if keywords were found
        """
        try:
            import pytesseract

            x, y, w, h = button_region
            # Expand the region to capture text
            margin = 20
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(screenshot.shape[1], x + w + margin)
            y2 = min(screenshot.shape[0], y + h + margin)

            region = screenshot[y1:y2, x1:x2]

            # Convert to grayscale and enhance contrast
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

            # OCR
            text = pytesseract.image_to_string(thresh).lower()

            # Check for keywords
            for keyword in keywords:
                if keyword.lower() in text:
                    return True

        except ImportError:
            logging.warning("pytesseract not available, skipping OCR verification")
        except Exception as e:
            logging.debug(f"OCR error: {e}")

        return False

    def click_button(self, x, y, w, h):
        """
        Click the center of the button.

        Args:
            x, y, w, h: Button bounding box coordinates
        """
        center_x = x + w // 2
        center_y = y + h // 2

        logging.info(f"Clicking button at ({center_x}, {center_y})")
        pyautogui.click(center_x, center_y)
        logging.info("Button clicked successfully!")

    def take_screenshot(self):
        """Take a screenshot and convert to OpenCV format."""
        screenshot = pyautogui.screenshot()
        # Convert PIL image to numpy array (BGR format for OpenCV)
        screenshot_np = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        return screenshot_bgr

    def start_monitoring(self, keywords=None, use_ocr=True):
        """
        Start monitoring for the queue button.

        Args:
            keywords: List of keywords to look for (e.g., ["join queue", "queue", "join"])
            use_ocr: Whether to use OCR to verify button text (slower but more accurate)
        """
        if keywords is None:
            keywords = ["join queue", "queue", "join"]

        self.running = True
        logging.info("Starting to monitor for queue button...")
        logging.info(f"Looking for keywords: {keywords}")
        logging.info("Press Ctrl+C to stop")

        try:
            while self.running:
                # Take screenshot
                screenshot = self.take_screenshot()

                # Detect blue buttons
                buttons = self.detect_blue_button(screenshot)

                if buttons:
                    logging.debug(f"Found {len(buttons)} potential button(s)")

                    for button in buttons:
                        x, y, w, h = button

                        # If OCR is enabled, verify the button has the right text
                        if use_ocr:
                            if self.check_for_text_near_button(screenshot, button, keywords):
                                self.click_button(x, y, w, h)
                                logging.info("Queue button found and clicked!")
                                # Return after successful click
                                return True
                        else:
                            # Click the first blue button found (faster but less accurate)
                            self.click_button(x, y, w, h)
                            logging.info("Blue button clicked (OCR disabled)")
                            return True

                # Wait before next check
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logging.info("\nMonitoring stopped by user")
            self.running = False
        except Exception as e:
            logging.error(f"Error during monitoring: {e}")
            raise

    def stop(self):
        """Stop monitoring."""
        self.running = False
        logging.info("Monitoring stopped")


def main():
    """Main function to run the Discord queue clicker."""
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

    # Wait a few seconds for user to position Discord window
    print("Starting in 5 seconds... Position your Discord window now!")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    print()

    # Create clicker instance with fast check interval
    clicker = DiscordQueueClicker(check_interval=0.5, confidence=0.7)

    # Start monitoring with OCR verification
    # Set use_ocr=False for faster clicking without text verification
    clicker.start_monitoring(
        keywords=["join queue", "queue", "join", "enter queue"],
        use_ocr=True  # Change to False for faster but less accurate clicking
    )


if __name__ == "__main__":
    main()
