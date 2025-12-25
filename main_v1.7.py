import pyautogui, cv2, numpy as np, time, random
from collections import deque

# =====================
# CONFIG
# =====================
FORWARD, BACK, LEFT, RIGHT = "w", "s", "a", "d"
MINE_BTN = "left"
EAT_SLOT = "9"
TOTEM_SLOT = "8"
SWAP = "f"
INV = "e"

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.02

# Zones écran (1080p)
CENTER_VIEW = (760, 360, 400, 300)
HEALTH = (600, 980, 400, 80)
HUNGER = (800, 980, 300, 80)
OFFHAND = (960, 540, 80, 80)

# Couleurs
LAVA_LOW = np.array([0, 0, 140])
LAVA_HIGH = np.array([90, 90, 255])

DIAMOND = ((90,180,180),(130,255,255))
IRON = ((0,0,100),(180,40,200))
GOLD = ((15,150,150),(40,255,255))

# Cooldowns
CD = {
    "eat": 8,
    "totem": 3,
    "retreat": 2,
    "turn": 5
}

last = {k:0 for k in CD}
memory_turns = deque(maxlen=10)
health_hist = deque(maxlen=5)
hunger_hist = deque(maxlen=5)

# =====================
# IMAGE
# =====================
def grab(region=None):
    img = pyautogui.screenshot(region=region)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

# =====================
# DETECTIONS
# =====================
def lava(frame):
    return cv2.countNonZero(cv2.inRange(frame,LAVA_LOW,LAVA_HIGH)) > 700

def critical_health(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    r1 = cv2.inRange(hsv,(0,120,70),(10,255,255))
    r2 = cv2.inRange(hsv,(170,120,70),(180,255,255))
    val = cv2.countNonZero(r1+r2)
    health_hist.append(val)
    return np.mean(health_hist) < 1300

def hungry(frame):
    val = np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    hunger_hist.append(val)
    return np.mean(hunger_hist) < 85

def damage(frame):
    return np.std(frame) > 45

def mob_detect(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,150)
    return cv2.countNonZero(edges) > 12000

def detect_ore(frame, color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color[0], color[1])
    return cv2.countNonZero(mask) > 300

def offhand_totem():
    hsv = cv2.cvtColor(grab(OFFHAND), cv2.COLOR_BGR2HSV)
    gold = cv2.inRange(hsv,(15,100,120),(40,255,255))
    return cv2.countNonZero(gold) > 500

# =====================
# ACTIONS
# =====================
def stop(): pyautogui.mouseUp(button=MINE_BTN)

def mine():
    pyautogui.mouseDown(button=MINE_BTN)
    pyautogui.keyDown(FORWARD)
    time.sleep(0.3)
    pyautogui.keyUp(FORWARD)

def eat():
    last["eat"]=time.time()
    pyautogui.press(EAT_SLOT)
    pyautogui.mouseDown(button="right")
    time.sleep(2)
    pyautogui.mouseUp(button="right")

def retreat():
    last["retreat"]=time.time()
    pyautogui.keyDown(BACK); time.sleep(1); pyautogui.keyUp(BACK)

def equip_totem():
    last["totem"]=time.time()
    pyautogui.press(TOTEM_SLOT); time.sleep(0.05); pyautogui.press(SWAP)

def reload_totem():
    pyautogui.press(INV); time.sleep(0.4)
    pyautogui.moveTo(960,540); pyautogui.dragTo(1000,600,0.2)
    pyautogui.press(INV)

def turn_random():
    if time.time()-last["turn"]<CD["turn"]: return
    last["turn"]=time.time()
    key = random.choice([LEFT,RIGHT])
    pyautogui.keyDown(key); time.sleep(random.uniform(0.4,0.7)); pyautogui.keyUp(key)
    memory_turns.append(key)

# =====================
# MAIN LOOP
# =====================
print("🤖 BOT ULTIME DÉMARRAGE 5s")
time.sleep(5)

try:
    while True:
        view = grab(CENTER_VIEW)
        health = grab(HEALTH)
        hunger = grab(HUNGER)

        # SURVIE ABSOLUE
        if critical_health(health) or damage(health):
            stop()
            if not offhand_totem():
                equip_totem(); time.sleep(0.2)
                if not offhand_totem(): reload_totem()
            continue

        # MENACE
        if mob_detect(view):
            stop(); retreat(); turn_random(); continue

        # LAVE
        if lava(view):
            if time.time()-last["retreat"]>CD["retreat"]:
                stop(); retreat(); turn_random()
            continue

        # FAIM
        if hungry(hunger):
            if time.time()-last["eat"]>CD["eat"]:
                stop(); eat()
            continue

        # MINERAIS PRIORITAIRES
        if detect_ore(view, DIAMOND) or detect_ore(view, GOLD) or detect_ore(view, IRON):
            mine(); continue

        # STRIP MINING
        mine()
        if random.random()<0.02: turn_random()

        time.sleep(0.1)

except KeyboardInterrupt:
    stop()
    print("🛑 BOT ARRÊTÉ PROPREMENT")
