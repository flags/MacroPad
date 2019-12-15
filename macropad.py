#!/usr/bin/env python3

import subprocess
import evdev
import time
import sys
import os

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

def loadConfig(filePath):
    if not os.path.isfile(filePath):
        print("Can't find file: %s" % filePath)

        return

    configFile = open(filePath, 'r')
    selectedDevice = None
    selectedKey = None
    lineNum = 0
    bindCount = 0

    for line in configFile.readlines():
        lineNum += 1
        line = line.rstrip() # remove newlines

        if not len(line):
            continue

        # obey formatting rules:
        #   if we're currently configuring a key and the line doesn't start with
        #   either a tab or a space, assume we're done with the current key and
        #   are moving to a new one.
        if selectedKey and not (line[0] in [' ', '\t']):
            selectedKey = None

        # strip all jargon from the front of the string
        line = line.lstrip()

        # let the user comment their config
        if line.startswith('#'):
            continue
        
        # if we havn't gotten the device yet, assume the first line is the path
        # to it.
        if not selectedDevice:
            selectedDevice = line
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

                assignKey(selectedKey, KEYEVENT_REMAP[event],
                        lambda: keyInput("key", keyCode))

                bindCount += 1
            elif action == "run":
                command = ' '.join(bindArgs[1:])
                assignKey(selectedKey, KEYEVENT_REMAP[event],
                        lambda: runProgram(command))

                bindCount += 1

            # print(event, bind)

    configFile.close()

    print("Loaded %i bind%s." % (bindCount, 's' * (bindCount != 1)))

    main(selectedDevice)

def handleKey(event):
    now = time.time()
    last_hit = now

    if not event.keycode in KEY_MAP:
        KEY_MAP[event.keycode] = {"state": event.keystate,
                "last_hit": now}

    else:
        last_hit = KEY_MAP[event.keycode]["last_hit"]

        KEY_MAP[event.keycode]["state"] = event.keystate
        KEY_MAP[event.keycode]["last_hit"] = now

    if KEY_MAP[event.keycode]["state"] == KEY_DOWN:
        print("Pressed: %s" % event.keycode)
    elif KEY_MAP[event.keycode]["state"] == KEY_HOLD:
        print("Hold: %s" % event.keycode)
    elif KEY_MAP[event.keycode]["state"] == KEY_UP:
        print("Released: %s" % event.keycode)

    if event.keycode in KEY_CALLBACK_MAP:
        if event.keystate in KEY_CALLBACK_MAP[event.keycode]:
            KEY_CALLBACK_MAP[event.keycode][event.keystate]()

def assignKey(keycode, state, callback):
    if keycode in KEY_CALLBACK_MAP:
        if state in KEY_CALLBACK_MAP[keycode]:
            raise Exception("Key already bound for state %s: %s" % (state, keycode))
    else:
        KEY_CALLBACK_MAP[keycode] = {}

    KEY_CALLBACK_MAP[keycode][state] = callback

# the following function wasn't written by me.
# it can found in full at: https://stackoverflow.com/a/6011298
def runProgram(command):
    print(command)
    return
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

                handleKey(keyEvent)
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
    elif len(sys.argv) > 3:
        print("Too many arguments.\n")
    else:
        usage()

