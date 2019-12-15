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

def loadConfig(filePath):
    if not os.path.isfile(filePath):
        print("Can't find file: %s" % filePath)

        return

    configFile = open(filePath, 'r')
    selectedDevice = None
    selectedKey = None
    selectedLayer = "default"
    lineNum = 0
    bindCount = 0

    for line in configFile.readlines():
        lineNum += 1
        line = line.rstrip() # remove newlines

        # obey formatting rules:
        #   if we're currently configuring a key and the line doesn't start with
        #   either a tab or a space, assume we're done with the current key and
        #   are moving to a new one.
        #   if the above criteria is met a second time, we reset the layer.
        if not len(line) or not (line[0] in [' ', '\t']):
            if selectedKey:
                selectedKey = None
            elif not selectedLayer == "default":
                selectedLayer = "default"

        # strip all jargon from the front of the string
        line = line.lstrip()

        if not len(line):
            continue

        # let the user comment their config
        if line.startswith('#'):
            continue

        if line.lower().startswith("layer"):
            layerInfo = line.split(' ')

            if not len(layerInfo) >= 2:
                print("Config error on line %i:\n\tMissing layer name" %
                        (lineNum))

                return

            selectedLayer = ' '.join(layerInfo[1:])

            continue
        
        # if we havn't gotten the device yet, assume the first line is the path
        # to it.
        if not selectedDevice:
            selectedDevice = line

            if DEBUG:
                break
        elif not selectedKey:
            # define the key we're configuring
            selectedKey = line
        else:
            # get the event and the bind
            event, _, bind = line.partition(' ')

            # if the event isn't one we support, tell the user
            if not event in KEYEVENT_REMAP:
                print("Config error on line %i:\n\tUnknown event for key '%s': %s" %
                        (lineNum, selectedKey, event))

                return

            # bind parsing:
            #   split the string and check if the first argument is an action we
            #   support.
            bindArgs = bind.split(' ')
            action = bindArgs[0].lower()

            if action == "key":
                #TODO: Check for keyup/keydown
                keyCode = bindArgs[1]

                # make sure the keycode is valid
                if not keyCode in KEY_CODES:
                    print("Config error on line %i:\n\tUnknown keycode for key '%s': %s" %
                            (lineNum, selectedKey, keyCode))
                    
                    return

                assignKey(selectedLayer, selectedKey, KEYEVENT_REMAP[event],
                        lambda keyCode=keyCode: keyInput("key", keyCode))

                bindCount += 1
            elif action == "run":
                command = ' '.join(bindArgs[1:])
                assignKey(selectedLayer, selectedKey, KEYEVENT_REMAP[event],
                        lambda command=command: runCommand(command))

                bindCount += 1
            elif action == "layer":
                layer = ' '.join(bindArgs[1:])

                assignKey(selectedLayer, selectedKey, KEYEVENT_REMAP[event],
                        lambda layer=layer: setLayer(layer))

    configFile.close()

    if not DEBUG:
        print("Loaded %i bind%s." % (bindCount, 's' * (bindCount != 1)))

    main(selectedDevice)

def handleKey(event, debug=False):
    now = time.time()
    last_hit = now

    if not event.keycode in KEY_MAP:
        KEY_MAP[event.keycode] = {"state": event.keystate,
                "last_hit": now}

    else:
        last_hit = KEY_MAP[event.keycode]["last_hit"]

        KEY_MAP[event.keycode]["state"] = event.keystate
        KEY_MAP[event.keycode]["last_hit"] = now

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
                KEY_CALLBACK_MAP[CURRENT_LAYER][event.keycode][event.keystate]()

def assignKey(layer, keycode, state, callback):
    if not layer in KEY_CALLBACK_MAP:
        KEY_CALLBACK_MAP[layer] = {}

    if keycode in KEY_CALLBACK_MAP[layer]:
        if state in KEY_CALLBACK_MAP[layer][keycode]:
            raise Exception("Key already bound for state %s: %s" % (state, keycode))
    else:
        KEY_CALLBACK_MAP[layer][keycode] = {}

    KEY_CALLBACK_MAP[layer][keycode][state] = callback

def setLayer(layer):
    global CURRENT_LAYER

    CURRENT_LAYER = layer

    print("debug: layer = %s" % layer)

# the following function wasn't written by me.
# it can found in full at: https://stackoverflow.com/a/6011298
def runCommand(command):
    setLayer("default")

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
    subprocess.call(command, shell=True, stdout=subprocess.PIPE)

    # all done
    os._exit(os.EX_OK)

def keyInput(event, keycode):
    with evdev.uinput.UInput() as ui:
        ui.write(evdev.ecodes.EV_KEY, evdev.ecodes.ecodes[keycode], 1)
        ui.syn()

def main(devicePath):
    # open the device via evdev
    device = evdev.InputDevice(devicePath)

    # start consuming all inputs from the device
    device.grab()

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
        else:
            loadConfig(arg)
    elif len(sys.argv) == 3:
        command, file = sys.argv[1:]

        if command == "--detect":
            detectDevice(file)
        elif command == "--show":
            DEBUG = True

            loadConfig(file)
    elif len(sys.argv) > 3:
        print("Too many arguments.\n")

        usage()
    else:
        usage()

