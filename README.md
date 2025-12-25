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
