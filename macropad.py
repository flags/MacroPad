#!/usr/bin/env python3

import subprocess
import threading
import evdev
import time
import sys
import grp
import os

try:
    import i3msg as i3

    I3_ENABLED = True
except:
    I3_ENABLED = False

VERSION = 1.1
DEBUG = False
ASSIST_MODE = False
NO_GROUP = False # for skipping `input` group checking
PASSTHROUGH = False
USING_DEVICE_NAME = False

# enums
KEY_UP = 0
KEY_DOWN = 1
KEY_HOLD = 2
EVENT_LAYER_CHANGED = 1

# reference list
KEY_CODES = evdev.ecodes.keys.values()

# maps
KEY_MAP = {}
KEY_CALLBACK_MAP = {}
KEYEVENT_REMAP = {"ON_PRESS": KEY_DOWN,
        "ON_RELEASE": KEY_UP,
        "ON_HOLD": KEY_HOLD}
COMMENT_MAP = {}
LAYER_OPTIONS = {}
EVENT_CALLBACKS = {}

# global
CURRENT_LAYER = "default"
LAYER_LOCK = False
LOCKED_PLAYER = "default"
DEFAULT_LAYER_TIMEOUT = 1.5
LAST_KEY_EVENT_TIME = 0
START_TIMEOUT_ON_KEYPRESS = False
HOT_LAYER = False
UI = None
WAIT_TIME = 0


def detectDevice():
    maxEventCount = 0
    bestDevice = None
    bestDeviceName = None
    loops = 5
    baseDir = "/dev/input/by-id/"

    # check if user is part of `input` group
    groups = [grp.getgrgid(g).gr_name for g in os.getgroups()]

    if not NO_GROUP and not "input" in groups:
        print("WARNING: You are NOT a member of the `input` group!")
        print("MacroPad cannot detect devices.")
        print("\nIf this is a mistake, run with `--nogroup`.")

        return

    print("Welcome to MacroPad-detect")
    print("\nMake sure your device is plugged in or turned on, then press ENTER.")

    input()

    print("Is your device connected via Bluetooth? y/(n)")

    bluetooth = input().lower() == 'y'

    if bluetooth:
        print("\nTake note that non-Bluetooth devices can still be detected in this mode.\n")

        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    else:
        devices = [os.path.join(baseDir, p) for p in os.listdir(baseDir)]

    print("** A total of %i devices were detected. **\n" % len(devices))
    print("MacroPad will now help you select the device you want to config.")
    print("\n1) Press ENTER")
    print("2) Hold down a key on the device you want to select")
    print("3) Make sure no other device is in use (mouse, etc.)")
    print("4) De-focus this window!")
    print("\nPress ENTER to begin.")

    input()

    print("** TEST STARTING IN 5 SECONDS - DE-FOCUS THIS WINDOW! **")

    time.sleep(5)

    print("\nPress and hold a key on your device.")

    while loops:
        loops -= 1

        for _device in devices:
            if bluetooth:
                device = _device
            else:
                try:
                    device = evdev.device.InputDevice(_device)
                except Exception as e:
                    print("Could not open device: %s" % e)

                    continue

            try:
                eventCount = 0

                for event in device.read():
                    eventCount += 1

                if eventCount > maxEventCount:
                    maxEventCount = eventCount
                    bestDevice = device
                    bestDeviceName = device.name
            except BlockingIOError:
                pass

            time.sleep(.01)

    if not bestDevice:
        print("\nNo device found.")

        return

    print("\nDevice found: %s" % bestDeviceName)
    print("\nMacroPad will now generate a config file for this device.")

    fileName = input("Enter file name: ")

    try:
        configFile = open(fileName, 'w')

        if bluetooth:
            configFile.write("DEVICE {\n\tNAME %s\n}\n\n" % bestDeviceName)
        else:
            configFile.write("DEVICE {\n\tPATH %s\n}\n\n" % bestDeviceName)

        configFile.write("BINDS {\n\n}\n")

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
    selectedEvent = None
    mode = "device"
    parseStack = []
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

            if keyword == "device":
                mode = "device"
            elif keyword == "events":
                mode = "events"
            elif keyword == "binds":
                mode = "binds"

            if mode == "binds":
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
            elif mode == "events":
                parseStack.append(keyword)
            else:
                parseStack.append(keyword)

            continue

        parsing = parseStack[len(parseStack) - 1]

        if line.endswith('}'):
            parseStack.pop()

            if parsing == "binds":
                selectedKey = None
            elif parsing == "device":
                pass
            elif parsing == "layer":
                selectedLayer = "default"

            continue

        if not parsing:
            print("Not parsing: %s" % line)

            continue

        if not ' ' in line:
            if parsing == "device":
                line = line.lower()

                if line == "passthrough":
                    global PASSTHROUGH

                    PASSTHROUGH = True
                else:
                    print("Unknown command in section `device`: %s" % line)

                    return
            elif parsing == "layer":
                line = line.lower()

                if line == "start_timeout_on_keypress":
                    setLayerOption(selectedLayer, line, True)
                else:
                    print("Unknown command in section `%s`: %s" % (parsing, line))

                    return

            continue

        key, _, value = line.partition(' ')
        key = key.lower()

        if mode == "device":
            if key == "path":
                selectedDevice = value
            elif key == "name":
                selectedDevice = value

                global USING_DEVICE_NAME

                USING_DEVICE_NAME = True
            else:
                print("Unknown key in section `device`: %s" % key)

                return

            continue
        elif mode == "binds":
            if parsing.upper() in KEYEVENT_REMAP:
                if key == "type":
                    assignKey(selectedLayer, selectedKey, KEY_DOWN,
                            lambda text=value, state=KEY_DOWN: type(text))
                elif key == "key":
                    binds = value.split('+')
                    assignKey(selectedLayer, selectedKey, KEY_DOWN,
                            lambda keyCode=binds, state=KEY_DOWN: keyInput("key",
                                keyCode, state))
                    assignKey(selectedLayer, selectedKey, KEY_DOWN,
                            lambda keyCode=binds, state=KEY_UP: keyInput("key",
                                keyCode, state))
                elif key == "layer":
                    assignKey(selectedLayer, selectedKey,
                            KEYEVENT_REMAP[parsing.upper()],
                            lambda layer=value: setLayer(layer))
                elif key == "modelayer":
                    assignKey(selectedLayer, selectedKey,
                            KEYEVENT_REMAP[parsing.upper()],
                            lambda layer=value: setLayer(layer, lock=True))
                elif key == "hotlayer":
                    assignKey(selectedLayer, selectedKey,
                            KEYEVENT_REMAP[parsing.upper()],
                            lambda layer=value: setLayer(layer, hot=True))
                elif key == "run":
                    assignKey(selectedLayer, selectedKey,
                            KEYEVENT_REMAP[parsing.upper()],
                            lambda value=value: runCommand(value))
                elif key == "wait":
                    assignKey(selectedLayer, selectedKey, KEY_DOWN,
                            lambda text=value, state=KEY_DOWN: wait(float(text)))
                else:
                    print("Unknown: line %i:" % lineNum, key, value)
                    return

                bindCount += 1
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
            elif key == "comment":
                assignComment(selectedLayer, selectedKey, value)
            elif key == "timeout":
                setLayerOption(selectedLayer, "timeout", float(value))
            else:
                print("Unknown key on line %i: %s" % (lineNum, key))
                return
        elif mode == "events":
            if parsing == "layer_changed":
                if key == "run":
                    addEventCallback(EVENT_LAYER_CHANGED, "run", value)
                else:
                    print("Unknown key on line %i: %s" % (lineNum, key))
                    return
            else:
                print("Unknown parsing layer on line %i: %s" % (lineNum, parsing))
                return
        else:
            print("Unknown parsing layer on line %i: %s - %s" % (lineNum, key, value))
            return

    configFile.close()

    if not DEBUG:
        print("Loaded %i bind%s." % (bindCount, 's' * (bindCount != 1)))

    main(selectedDevice)

def handleKey(event, debug=False):
    global START_TIMEOUT_ON_KEYPRESS
    global LAST_KEY_EVENT_TIME
    global HOT_LAYER
    global WAIT_TIME

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
    timeout = getLayerTimeout(CURRENT_LAYER)

    if now - LAST_KEY_EVENT_TIME >= timeout:
        if START_TIMEOUT_ON_KEYPRESS:
            START_TIMEOUT_ON_KEYPRESS = False
            # print("debug: waiting until next keypress")
        else:
            if debug and HOT_LAYER:
                print("Hot layer reset!")

            HOT_LAYER = False
            if LAYER_LOCK:
                if not CURRENT_LAYER == LOCKED_LAYER:
                    setLayer(LOCKED_LAYER)

                    if debug:
                        print("Returning to locked layer: %s" % LOCKED_LAYER)
            elif not CURRENT_LAYER == "default":
                setLayer("default")

    # track whether we fired a macro in case the user specified `PASSTHROUGH`
    fired = False

    if debug:
        if KEY_MAP[event.keycode]["state"] == KEY_DOWN:
            print("%s - KEY_DOWN" % event.keycode)
        elif KEY_MAP[event.keycode]["state"] == KEY_HOLD:
            print("%s - KEY_HOLD" % event.keycode)
        elif KEY_MAP[event.keycode]["state"] == KEY_UP:
            print("%s - KEY_UP" % event.keycode)

        # do this so we don't pass keycodes to the system
        fired = True
    else:
        if event.keycode in KEY_CALLBACK_MAP[CURRENT_LAYER]:
            if event.keystate in KEY_CALLBACK_MAP[CURRENT_LAYER][event.keycode]:
                fired = True
                resetLayer = False

                # pull callbacks out of the dictionary and call them
                for callback in KEY_CALLBACK_MAP[CURRENT_LAYER][event.keycode][event.keystate]:
                    if callback():
                        resetLayer = True

                    if WAIT_TIME:
                        time.sleep(WAIT_TIME)

                        WAIT_TIME = 0
                    else:
                        time.sleep(.01)

                # record the time at which the event was executed. see above
                LAST_KEY_EVENT_TIME = now

                if resetLayer:
                    if not (LAYER_LOCK or HOT_LAYER):
                        setLayer("default")

    return fired

def assignComment(layer, keycode, value):
    if not layer in COMMENT_MAP:
        COMMENT_MAP[layer] = {}

    if not keycode in COMMENT_MAP[layer]:
        COMMENT_MAP[layer][keycode] = value

        return

    print("WARNING: already assigned comment to %s - %s" % (layer, keycode))

def addEventCallback(event, command, value):
    if not event in EVENT_CALLBACKS:
        EVENT_CALLBACKS[event] = []

    EVENT_CALLBACKS[event].append({"command": command, "value": value})

def triggerEventCallback(event):
    if not event in EVENT_CALLBACKS:
        return

    for callback in EVENT_CALLBACKS[event]:
        newValue = callback["value"]
        newValue = newValue.replace("%LAYER%", CURRENT_LAYER)

        if callback["command"] == "run":
            runCommand(newValue)

def setLayerOption(layer, key, value):
    if not layer in LAYER_OPTIONS:
        LAYER_OPTIONS[layer] = {}

    if not key in LAYER_OPTIONS[layer]:
        LAYER_OPTIONS[layer][key] = value

        return

    print("WARNING: already assigned %s to %s - %s" % (key, layer, value))

def applyLayerOptions(layer):
    if not layer in LAYER_OPTIONS:
        return

    for key in LAYER_OPTIONS[layer].keys():
        if key == "start_timeout_on_keypress":
            global START_TIMEOUT_ON_KEYPRESS

            START_TIMEOUT_ON_KEYPRESS = True
        elif key == "timeout":
            pass
        else:
            print("Warning: Unhandled option: %s" % key)

def getLayerTimeout(layer):
    if layer in LAYER_OPTIONS and "timeout" in LAYER_OPTIONS[layer]:
        return LAYER_OPTIONS[layer]["timeout"]

    return DEFAULT_LAYER_TIMEOUT

def assignKey(layer, keycode, state, callback):
    assert(keycode != None)

    if not layer in KEY_CALLBACK_MAP:
        KEY_CALLBACK_MAP[layer] = {}

    if not keycode in KEY_CALLBACK_MAP[layer]:
        KEY_CALLBACK_MAP[layer][keycode] = {}

    if not state in KEY_CALLBACK_MAP[layer][keycode]:
        KEY_CALLBACK_MAP[layer][keycode][state] = []

    KEY_CALLBACK_MAP[layer][keycode][state].append(callback)

def showLayer():
    timeout = getLayerTimeout(CURRENT_LAYER)
    subprocess.Popen("notify-send -t %i \"%s\"" % (timeout * 1000,
        CURRENT_LAYER), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print('\x1b[2J') # clear terminal
    print(CURRENT_LAYER + '\n')

    if not CURRENT_LAYER in COMMENT_MAP:
        print("No comments for this layer.")
        return

    keys = list(COMMENT_MAP[CURRENT_LAYER].keys())
    keys.sort()

    for key in keys:
        print("[ %s ] %s" % (key.split("KEY_")[1], COMMENT_MAP[CURRENT_LAYER][key]))

def setLayer(layer, lock=False, hot=False):
    global CURRENT_LAYER
    global LAYER_LOCK, LOCKED_LAYER, HOT_LAYER

    lastLayer = CURRENT_LAYER

    layerChanged = not CURRENT_LAYER == layer

    CURRENT_LAYER = layer

    if layerChanged:
        triggerEventCallback(EVENT_LAYER_CHANGED)

    applyLayerOptions(layer)

    if lock:
        LOCKED_LAYER = layer
        # print("Locked layer: %s" % LOCKED_LAYER)
        LAYER_LOCK = lock
    elif layer == "default":
        LAYER_LOCK = False
        LOCKED_LAYER = layer

    # or just assign hot_layer to hot value?
    if hot:
        HOT_LAYER = True

    # print("debug: layer = %s" % layer)

    # experimenting with osd for command readout
    if ASSIST_MODE:
        if not lastLayer == CURRENT_LAYER:
            showLayer()

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
            return 1
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

def wait(seconds):
    global WAIT_TIME

    WAIT_TIME = seconds

def getDeviceViaName(name):
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

    for device in devices:
        if device.name == name:
            return device

    print("Device not found: %s" % name)

    return None

def listen(devicePath):
    # open the device via evdev
    if USING_DEVICE_NAME:
        while True:
            device = getDeviceViaName(devicePath)

            if device:
                break
            else:
                print("Waiting")
                time.sleep(1)
    else:
        device = evdev.InputDevice(devicePath)

    if not device:
        return

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

                fired = handleKey(keyEvent, debug=DEBUG)

                if not fired and PASSTHROUGH:
                    UI.write_event(event)
                    UI.syn()
    except KeyboardInterrupt:
        print("Interrupt.")
    except OSError:
        return 1
    except Exception as e:
        print(e)

    try:
        device.ungrab()
    except Exception as e:
        print("Warning: Nothing to ungrab.")

    return 0

    logging.info("Thread %s: starting", name)
    time.sleep(2)
    logging.info("Thread %s: finishing", name)

def focusHandler(event, data):
    if not "container" in data or not "window_properties" in data["container"]:
        return

    window = data["container"]["window_properties"]["instance"]

    if window in KEY_CALLBACK_MAP:
        setLayer(window, lock=True)
    else:
        setLayer("default", lock=True)

def main(devicePath):
    global UI

    if I3_ENABLED:
        i3.subscribe(['window'], focusHandler)

    UI = evdev.uinput.UInput()

    while listen(devicePath):
        print("Reconnecting...")

    print("Done")

def usage():
    print("MacroPad.py - flags (2020) - ver. %.1f" % VERSION)
    print("Usage:")
    print("\t<file>\t\t - run MacroPad with configuration file")
    print("\t--detect\t - select device and output default config file")
    print("\t--show <file>\t - print all key inputs to the terminal (will not fire binds)")
    print("\nExtras:")
    print("\t--assist\t - print out keybinds in the terminal")
    print("\t--nogroup\t - ignore group requirement")


if __name__ == "__main__":
    if "--assist" in sys.argv:
        ASSIST_MODE = True

        sys.argv.remove("--assist")

    if "--nogroup" in sys.argv:
        NO_GROUP = True

        sys.argv.remove("--nogroup")

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

