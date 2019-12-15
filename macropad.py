#!/usr/bin/python3

import subprocess
import evdev
import time

# enums
KEY_UP = 0
KEY_DOWN = 1
KEY_HOLD = 2

KEY_MAP = {}
KEY_CALLBACK_MAP = {}

PAD = "/dev/input/by-id/usb-099a_USB_Keypad-event-kbd"


def handleKey(event):
    now = time.time()
    # last_state = 0
    last_hit = now

    if not event.keycode in KEY_MAP:
        KEY_MAP[event.keycode] = {"state": event.keystate,
                "last_hit": now}

    else:
        last_hit = KEY_MAP[event.keycode]["last_hit"]
        # last_state = KEY_MAP[event.keycode]["state"]

        KEY_MAP[event.keycode]["state"] = event.keystate
        KEY_MAP[event.keycode]["last_hit"] = now

    # if now - last_hit < 
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

def runProgram(command):
    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

def main():
    device = evdev.InputDevice(PAD)
    i = 0

    assignKey("KEY_KP1", KEY_DOWN, lambda: runProgram("qutebrowser"))
    assignKey("KEY_KP2", KEY_DOWN, lambda: runProgram("st"))

    device.grab()
    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            keyEvent = evdev.categorize(event)
            # print(keyEvent.event)
            handleKey(keyEvent)
            # print("\tkey: %s" % keyEvent.keycode)
            # print("\tstate: %s" % keyEvent.keystate)
            # print("\thold: %s" % keyEvent.key_hold)
            i += 1

            if i == 25:
                break

    device.ungrab()


if __name__ == "__main__":
    main()
