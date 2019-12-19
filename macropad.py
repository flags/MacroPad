#!/usr/bin/env python3

import subprocess
import evdev
import time
import sys
import os

DEBUG = False

# enums
KEY_UP = 0
KEY_DOWN = 1
KEY_HOLD = 2

# reference list
KEY_CODES = evdev.ecodes.keys.values()

# maps
KEY_MAP = {}
KEY_CALLBACK_MAP = {}
KEYEVENT_REMAP = {"ON_PRESS": KEY_DOWN,
        "ON_RELEASE": KEY_UP,
        "ON_HOLD": KEY_HOLD}

# global
CURRENT_LAYER = "default"
LAYER_LOCK = False
LOCKED_PLAYER = "default"
LAYER_TIMEOUT_MAX = 1.5
LAST_KEY_EVENT_TIME = 0
HOT_LAYER = False
UI = None


def detectDevice():
    maxEventCount = 0
    bestDevice = None
    bestDevicePath = None
    loops = 5
    baseDir = "/dev/input/by-id/"

    print("Welcome to MacroPad-detect")
    print("\nMake sure your device is plugged in, then press ENTER.")

    input()

    devices = [os.path.join(baseDir, p) for p in os.listdir(baseDir)]

    print("** A total of %i devices were detected. **\n" % len(devices))
    print("MacroPad will now help you select the device you want to config.")
    print("\n1) Press ENTER")
    print("2) Hold down a key on the device you want to select")
    print("3) Make sure no other device is in use (mouse, etc.")
    print("4) De-focus this window!")
    print("\nPress ENTER to begin.")

    input()

    print("** TEST STARTING IN 5 SECONDS - DE-FOCUS THIS WINDOW! **")

    time.sleep(5)

    print("\nPress and hold a key on your device.")

    while loops:
        loops -= 1

        for devicePath in devices:
            try:
                device = evdev.device.InputDevice(devicePath)
            except:
                pass

            try:
                eventCount = 0

                for event in device.read():
                    eventCount += 1

                if eventCount > maxEventCount:
                    maxEventCount = eventCount
                    bestDevice = device
                    bestDevicePath = devicePath
            except BlockingIOError:
                pass

            time.sleep(.01)

    if not bestDevice:
        print("\nNo device found.")

        return

    print("\nDevice found: %s" % bestDevice.name)
    print("\nMacroPad will now generate a config file for this device.")

    fileName = input("Enter file name: ")

    try:
        configFile = open(fileName, 'w')

        configFile.write("%s\n\n# place binds below this line\n\n" % bestDevicePath)
        configFile.close()

        print("\nFile saved.\n")
        print("See `readme.md` for configuration help.")
    except Exception as e:
        print(e)

def loadConfig(filePath):
    if not os.path.isfile(filePath):
        print("Can't find file: %s" % filePath)

        return

    configFile = open(filePath, 'r')
    selectedDevice = None
    selectedKey = None
    selectedEvent = None
    selectedLayer = "default"
    parseStack = []
    # blockNum = 0
    lineNum = 0
    bindCount = 0

    for line in configFile.readlines():
        lineNum += 1
        line = line.lstrip().rstrip() # remove newlines

        if not len(line):
            continue

        if line.startswith('#'):
            continue

        if line.endswith('{'):
            keyword = line.split('{')[0].rstrip().lower()

            # print("Parsing: %s" % keyword)

            if keyword.startswith("key_"):
                selectedKey = keyword.upper()

                # print("Selected key: %s" % selectedKey)

                parseStack.append(keyword)
            elif keyword.startswith("layer"):
                selectedLayer = keyword.split(' ')[1]

                # print("Selected layer: %s" % selectedLayer)

                parseStack.append("layer")
            else:
                parseStack.append(keyword)

            continue

        parsing = parseStack[len(parseStack) - 1]

        if line.endswith('}'):
            parseStack.pop()

            if parsing == "binds":
                pass
            elif parsing == "device":
                pass
            elif parsing == "layer":
                selectedLayer = "default"

            continue

        if not parsing:
            print("Not parsing: %s" % line)

            continue

        if not ' ' in line:
            continue

        key, _, value = line.partition(' ')
        key = key.lower()

        if parsing == "device":
            if key == "path":
                selectedDevice = value

            continue
        elif parsing.upper() in KEYEVENT_REMAP:
            if key == "type":
                assignKey(selectedLayer, selectedKey, KEY_DOWN,
                        lambda text=value, state=KEY_DOWN: type(text))
            elif key == "key":
                assignKey(selectedLayer, selectedKey, KEY_DOWN,
                        lambda keyCode=[value], state=KEY_DOWN: keyInput("key",
                            keyCode, state))
                assignKey(selectedLayer, selectedKey, KEY_DOWN,
                        lambda keyCode=[value], state=KEY_UP: keyInput("key",
                            keyCode, state))
                bindCount += 1
            elif key == "layer":
                assignKey(selectedLayer, selectedKey,
                        KEYEVENT_REMAP[parsing.upper()],
                        lambda layer=value: setLayer(layer))

                bindCount += 1
            elif key == "modelayer":
                assignKey(selectedLayer, selectedKey,
                        KEYEVENT_REMAP[parsing.upper()],
                        lambda layer=value: setLayer(layer, lock=True))

                bindCount += 1
            elif key == "hotlayer":
                assignKey(selectedLayer, selectedKey,
                        KEYEVENT_REMAP[parsing.upper()],
                        lambda layer=value: setLayer(layer, hot=True))

                bindCount += 1
            elif key == "run":
                assignKey(selectedLayer, selectedKey,
                        KEYEVENT_REMAP[parsing.upper()],
                        lambda value=value: runCommand(value))

                bindCount += 1
            else:
                print("Unknown: line %i:" % lineNum, key, value)
                return
        elif key == "bind":
            binds = value.split('+')
            assignKey(selectedLayer, selectedKey, KEY_DOWN,
                    lambda keyCode=binds, state=KEY_DOWN: keyInput("key",
                        keyCode, state))
            assignKey(selectedLayer, selectedKey, KEY_HOLD,
                    lambda keyCode=binds, state=KEY_HOLD: keyInput("key",
                        keyCode, state))
            assignKey(selectedLayer, selectedKey, KEY_UP,
                    lambda keyCode=binds, state=KEY_UP: keyInput("key",
                        keyCode, state))
            bindCount += 1
        else:
            print("Unknown parsing layer on line %i: %s - %s" % (lineNum, key, value))
            return

    configFile.close()

    if not DEBUG:
        print("Loaded %i bind%s." % (bindCount, 's' * (bindCount != 1)))

    main(selectedDevice)

def showKey(key, command):
    subprocess.Popen("notify-send -t %i \"%s - %s\"" % (LAYER_TIMEOUT_MAX * 1000, key, command),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def handleKey(event, debug=False):
    global LAST_KEY_EVENT_TIME
    global HOT_LAYER

    now = time.time()
    last_hit = now

    if not event.keycode in KEY_MAP:
        KEY_MAP[event.keycode] = {"state": event.keystate, "last_hit": now}
    else:
        last_hit = KEY_MAP[event.keycode]["last_hit"]

        KEY_MAP[event.keycode]["state"] = event.keystate
        KEY_MAP[event.keycode]["last_hit"] = now

    # if the amount of time since the last pressed key is
    # greater than some amount, then switch back to the default
    # layer.
    # this prevents lingering inputs from affecting future inputs.
    if now - LAST_KEY_EVENT_TIME >= LAYER_TIMEOUT_MAX:
        if HOT_LAYER:
            print("Hot layer reset!")

        HOT_LAYER = False
        if LAYER_LOCK:
            if not CURRENT_LAYER == LOCKED_LAYER:
                setLayer(LOCKED_LAYER)

                print("Returning to locked layer: %s" % LOCKED_LAYER)
        elif not CURRENT_LAYER == "default":
            setLayer("default")

    if debug:
        if KEY_MAP[event.keycode]["state"] == KEY_DOWN:
            print("%s - KEY_DOWN" % event.keycode)
        elif KEY_MAP[event.keycode]["state"] == KEY_HOLD:
            print("%s - KEY_HOLD" % event.keycode)
        elif KEY_MAP[event.keycode]["state"] == KEY_UP:
            print("%s - KEY_UP" % event.keycode)
    else:
        if event.keycode in KEY_CALLBACK_MAP[CURRENT_LAYER]:
            if event.keystate in KEY_CALLBACK_MAP[CURRENT_LAYER][event.keycode]:
                resetLayer = False

                # pull callbacks out of the dictionary and call them
                for callback in KEY_CALLBACK_MAP[CURRENT_LAYER][event.keycode][event.keystate]:
                    if callback():
                        resetLayer = True

                # record the time at which the event was executed. see above
                LAST_KEY_EVENT_TIME = now

                if resetLayer:
                    if not (LAYER_LOCK or HOT_LAYER):
                        setLayer("default")

def assignKey(layer, keycode, state, callback):
    if not layer in KEY_CALLBACK_MAP:
        KEY_CALLBACK_MAP[layer] = {}

    if not keycode in KEY_CALLBACK_MAP[layer]:
        KEY_CALLBACK_MAP[layer][keycode] = {}

    if not state in KEY_CALLBACK_MAP[layer][keycode]:
        KEY_CALLBACK_MAP[layer][keycode][state] = []

    KEY_CALLBACK_MAP[layer][keycode][state].append(callback)

def showLayer():
    subprocess.Popen("notify-send -t %i \"%s\"" % (LAYER_TIMEOUT_MAX * 1000,
        CURRENT_LAYER), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print('\x1b[2J') 

    # keys = list(KEY_CALLBACK_MAP[CURRENT_LAYER].keys())
    # keys.sort()

    # print(CURRENT_LAYER + '\n')

    # for key in keys:
        # print("%s - %s" % (key, KEY_CALLBACK_MAP[CURRENT_LAYER][key]))

def setLayer(layer, lock=False, hot=False):
    global CURRENT_LAYER
    global LAYER_LOCK, LOCKED_LAYER, HOT_LAYER

    lastLayer = CURRENT_LAYER
    CURRENT_LAYER = layer

    if lock:
        LOCKED_LAYER = layer
        print("Locked layer: %s" % LOCKED_LAYER)
        LAYER_LOCK = lock
    elif layer == "default":
        LAYER_LOCK = False
        LOCKED_LAYER = layer

    # or just assign hot_layer to hot value?
    if hot:
        HOT_LAYER = True

    print("debug: layer = %s" % layer)

    # experimenting with osd for command readout
    if not lastLayer == CURRENT_LAYER:
        showLayer()

    # for keycode in KEY_CALLBACK_MAP[CURRENT_LAYER]:
        # showKey(str(keycode), "duh")

    return 0

# the following function wasn't written by me.
# it can found in full at: https://stackoverflow.com/a/6011298
def runCommand(command, event=None):
    # do the UNIX double-fork magic, see Stevens' "Advanced 
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    try: 
        pid = os.fork() 
        if pid > 0:
            # parent process, return and keep running
            return
    except Exception as e:
        print(e)

        sys.exit(1)

    os.setsid()

    # do second fork
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit from second parent
            sys.exit(0) 
    except Exception as e:
        print(e)

        sys.exit(1)

    # do stuff
    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    # all done
    os._exit(os.EX_OK)

    return 1

def keyInput(event, keycodes, state):
    for keycode in keycodes:
        UI.write(evdev.ecodes.EV_KEY, evdev.ecodes.ecodes[keycode], state)

    UI.syn()

    return 1

def type(text):
    subprocess.call("xdotool type %s" % text, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    return 1

def main(devicePath):
    global UI

    # open the device via evdev
    device = evdev.InputDevice(devicePath)

    UI = evdev.uinput.UInput()
    # start consuming all inputs from the device
    try:
        device.grab()
    except Exception as e:
        print(e)

        return

    # main loop
    #   listen to inputs and react to them.
    #   try..except safely closes the device and exits
    try:
        for event in device.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                keyEvent = evdev.categorize(event)

                handleKey(keyEvent, debug=DEBUG)
    except KeyboardInterrupt:
        print("Interrupt.")
    except Exception as e:
        print(e)

    try:
        device.ungrab()
    except Exception as e:
        print(e)

    print("Done")

def usage():
    print("MacroPad.py - flags (2019)")
    print("Usage:")
    print("\t<file>\t\t - run MacroPad with configuration file")
    print("\t--detect <file>\t - select device and output default config file")
    print("\t--show <file>\t - print all key inputs to the terminal (will not fire binds)")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        arg = sys.argv[1]

        if arg == "--help":
            usage()
        elif arg == "--detect":
            detectDevice()
        else:
            loadConfig(arg)
    elif len(sys.argv) == 3:
        command, file = sys.argv[1:]

        if command == "--show":
            DEBUG = True

            loadConfig(file)
        else:
            print("Unknown command.")

            usage()
    elif len(sys.argv) > 3:
        print("Too many arguments.\n")

        usage()
    else:
        usage()

