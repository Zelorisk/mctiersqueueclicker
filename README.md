# discord queue auto-clicker

monitors your screen for the join queue button inside of discord and clicks it automatically when it appears.

## setup

### install python

if you don't have python installed:

**macos:**
```bash
brew install python3
```
or just download it from the python website
(www.python.org/downloads)

**windows:**
download from https://www.python.org/downloads/ (make sure to check "add python to PATH")

**linux:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

### install tesseract (optional, for better accuracy)

**macos:**
```bash
brew install tesseract
```

**windows:**
download from https://github.com/UB-Mannheim/tesseract/wiki

**linux:**
```bash
sudo apt-get install tesseract-ocr
```

skip this if you want maximum speed. without tesseract the script will just click any blue button it finds.

### setup the script

```bash
# navigate to the project folder
cd /path/to/python3

# create virtual environment
python3 -m venv venv

# activate virtual environment
# on macos/linux:
source venv/bin/activate
# on windows:
venv\Scripts\activate

# install dependencies
pip install -r requirements.txt
```

## usage

```bash
# make sure venv is activated
source venv/bin/activate  # or venv\Scripts\activate on windows

# run the script
python discord_queue_clicker.py
```

open discord and keep the channel visible on screen. the script gives you 5 seconds to get ready, then starts monitoring. it will click the button when it appears.

press ctrl+c to stop.

## making it faster

if you need maximum speed and don't care about accuracy, edit line 222 in discord_queue_clicker.py:

change `use_ocr=True` to `use_ocr=False`

this makes it click any blue button immediately without checking the text.

## how it works

the script constantly screenshots your screen looking for that blue "join queue" button in discord. when it finds it, it instantly clicks it for you.

**the libraries:**

- **pyautogui** - takes screenshots and controls your mouse/keyboard. handles the actual clicking
- **opencv-python (cv2)** - computer vision library that processes screenshots to detect that specific blue color
- **numpy** - math library that works with opencv to handle image arrays
- **pytesseract** - ocr (text reading) that double-checks the button actually says "join queue" and isn't just some random blue rectangle
- **pillow** - image processing library (pyautogui depends on it)

**color detection**: converts screenshots to hsv color space and looks for a very specific shade of blue (hue 110-130). hsv is better than rgb for finding colors because it separates color from brightness.

**shape filtering**: once it finds blue regions, it filters them by:
- size (2000-50000 pixels, so not tiny icons or huge backgrounds)
- aspect ratio (2.0-8.0, meaning wider than tall like a button)
- minimum dimensions (at least 100px wide, 25px tall)
- position (ignores top 20% and bottom 10% of screen)

**ocr verification** (optional): uses tesseract to read text from the detected button region. if it contains keywords like "join queue" or "queue", it's confirmed. you can disable this for raw speed.

**the click**: uses pyautogui to move the cursor and click the center of the button. there's a scale factor calculation because screenshot resolution might differ from screen resolution (happens on retina displays).

**sleep prevention**: on macos, it runs the `caffeinate` command to prevent your computer from sleeping while monitoring.

**debug mode**: saves images showing what it detected (those .png files) so you can see what's happening under the hood.

the whole thing runs in a loop every 0.5 seconds, which is pretty aggressive for detection speed. basically optimized for being the fastest person to click that button when it appears.
