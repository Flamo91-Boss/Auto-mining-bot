import pyautogui, cv2, numpy as np, time

# Touches a personnaliser
FORWARD_KEY = "w"  # Touche avancer
BACK_KEY = "s" # Touche reculer
MINE_BUTTON = "left" # Clique pour miner
EAT_SLOT = "9" # Numéro barre item nourriture
TOTEM_SLOT = "8" # Numéro barre item totem
OFFHAND_SWAP_KEY = "f" # Touche 2eme main
INVENTORY_KEY = "e" # Touche inventaire

# Détection écran (1080p approx)
HUNGER_REGION = (800, 980, 300, 80)
HEALTH_REGION = (600, 980, 400, 80)
OFFHAND_REGION = (960, 540, 80, 80)

# Lave (BGR)
LAVA_LOW = np.array([0, 0, 140])
LAVA_HIGH = np.array([90, 90, 255])


# =====================
# OUTILS IMAGE
# =====================
def grab(region=None):
    img = pyautogui.screenshot(region=region)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

# =====================
# DÉTECTIONS
# =====================
def detect_lava():
    img = grab()
    mask = cv2.inRange(img, LAVA_LOW, LAVA_HIGH)
    return cv2.countNonZero(mask) > 600

def hunger_low():
    img = grab(HUNGER_REGION)
    return np.mean(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)) < 85

def health_critical():
    img = grab(HEALTH_REGION)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    r1 = cv2.inRange(hsv, (0,120,70), (10,255,255))
    r2 = cv2.inRange(hsv, (170,120,70), (180,255,255))
    return cv2.countNonZero(r1+r2) < 1300

def taking_damage():
    img = grab(HEALTH_REGION)
    return np.std(img) > 40

def offhand_has_totem():
    img = grab(OFFHAND_REGION)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gold = cv2.inRange(hsv, (15,100,120), (40,255,255))
    return cv2.countNonZero(gold) > 500

# =====================
# ACTIONS
# =====================
def eat():
    print("🍗 Manger")
    pyautogui.press(EAT_SLOT)
    pyautogui.mouseDown(button='right')
    time.sleep(2)
    pyautogui.mouseUp(button='right')

def retreat():
    print("🔥 Danger détecté → Recul")
    pyautogui.keyDown(BACK_KEY)
    time.sleep(1)
    pyautogui.keyUp(BACK_KEY)

def equip_totem():
    print("🛡️ Équipement Totem")
    pyautogui.press(TOTEM_SLOT)
    time.sleep(0.05)
    pyautogui.press(OFFHAND_SWAP_KEY)
    time.sleep(0.2)

def reload_totem_from_inventory():
    print("📦 Recharge Totem inventaire")
    pyautogui.press(INVENTORY_KEY)
    time.sleep(0.4)
    pyautogui.moveTo(960, 540)   # slot inventaire (à ajuster)
    pyautogui.dragTo(1000, 600, 0.2)
    pyautogui.press(INVENTORY_KEY)

# =====================
# BOUCLE PRINCIPALE
# =====================
def bot():
    print("⛏️ Bot prêt – CTRL+C pour arrêter")
    time.sleep(3)
    pyautogui.mouseDown(button=MINE_BUTTON)

    try:
        while True:
            # Auto-Totem prioritaire
            if health_critical() or taking_damage():
                pyautogui.mouseUp(button=MINE_BUTTON)
                if not offhand_has_totem():
                    equip_totem()
                    if not offhand_has_totem():
                        reload_totem_from_inventory()
                pyautogui.mouseDown(button=MINE_BUTTON)

            # Lave
            if detect_lava():
                pyautogui.mouseUp(button=MINE_BUTTON)
                retreat()
                pyautogui.mouseDown(button=MINE_BUTTON)

            # Faim
            if hunger_low():
                pyautogui.mouseUp(button=MINE_BUTTON)
                eat()
                pyautogui.mouseDown(button=MINE_BUTTON)

            # Avancer + miner
            pyautogui.keyDown(FORWARD_KEY)
            time.sleep(0.3)
            pyautogui.keyUp(FORWARD_KEY)
            time.sleep(0.1)

    except KeyboardInterrupt:
        pyautogui.mouseUp(button=MINE_BUTTON)
        pyautogui.keyUp(FORWARD_KEY)
        print("🛑 Bot arrêté proprement")

bot()


