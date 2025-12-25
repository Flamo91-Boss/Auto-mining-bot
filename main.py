import pyautogui
import cv2
import numpy as np
import time

# =========================
# CONFIGURATION
# =========================
EAT_KEY = "9"        # slot nourriture
FORWARD_KEY = "w"
BACK_KEY = "s"
MINE_BUTTON = "left"

LAVA_COLOR_LOW = np.array([0, 0, 150])
LAVA_COLOR_HIGH = np.array([80, 80, 255])

HUNGER_CHECK_REGION = (800, 980, 300, 80)  # à ajuster

# =========================
# UTILITAIRES
# =========================
def screenshot_np(region=None):
    img = pyautogui.screenshot(region=region)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def detect_lava():
    img = screenshot_np()
    mask = cv2.inRange(img, LAVA_COLOR_LOW, LAVA_COLOR_HIGH)
    lava_pixels = cv2.countNonZero(mask)
    return lava_pixels > 500  # seuil

def hunger_low():
    img = screenshot_np(HUNGER_CHECK_REGION)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    return brightness < 80  # très approximatif mais fonctionnel

def eat():
    print("🍗 Faim détectée → manger")
    pyautogui.press(EAT_KEY)
    pyautogui.mouseDown(button='right')
    time.sleep(2)
    pyautogui.mouseUp(button='right')

def panic_back():
    print("🔥 LAVE ! Recul immédiat")
    pyautogui.keyDown(BACK_KEY)
    time.sleep(1)
    pyautogui.keyUp(BACK_KEY)

# =========================
# BOUCLE PRINCIPALE
# =========================
def mine_loop():
    print("⛏️ Bot actif – CTRL+C pour arrêter")
    time.sleep(3)

    pyautogui.mouseDown(button=MINE_BUTTON)

    try:
        while True:
            if detect_lava():
                pyautogui.mouseUp(button=MINE_BUTTON)
                panic_back()
                time.sleep(1)
                pyautogui.mouseDown(button=MINE_BUTTON)

            if hunger_low():
                pyautogui.mouseUp(button=MINE_BUTTON)
                eat()
                pyautogui.mouseDown(button=MINE_BUTTON)

            pyautogui.keyDown(FORWARD_KEY)
            time.sleep(0.3)
            pyautogui.keyUp(FORWARD_KEY)

            time.sleep(0.1)

    except KeyboardInterrupt:
        pyautogui.mouseUp(button=MINE_BUTTON)
        pyautogui.keyUp(FORWARD_KEY)
        print("🛑 Bot arrêté")

# =========================
mine_loop()
