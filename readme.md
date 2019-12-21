# MacroPad

This is a tool for turning any key-based input device into a "macropad" for
triggering commands on your PC. Although designed with traditional keyboard
numpads in mind, MacroPad will work with any device that fires keycodes.

MacroPad intercepts keycodes on a per-device basis, meaning multiple keyboards
can be plugged in and configured independently.

MacroPad's most powerful feature is layering, which allows keys to change the
mapping of the device on the fly.

## Setup

First, ensure you have the `python-evdev` module installed via `pip` or your
distro's package manager. In Arch Linux, use `python-evdev`.

Clone this repo to a directory of your choosing, then run:

`./macropad.py --detect`

Follow the on-screen instructions. Note the location of the configuration file,
then open it in the text editor of your choosing.

### Learning / Documentation

Please see [advanced usage](config-documentation.md) after reading the section
below.

### Configuration Workflow (Basic)

Open up a terminal alongside your text editor and run:

`./macropad.py --show /path/to/config/file`

Now press any key on the input device chosen in the last step. You will see
something along the lines of:

```
KEY_KP1 - KEY_DOWN
KEY_KP1 - KEY_HOLD
KEY_KP1 - KEY_HOLD
KEY_KP1 - KEY_HOLD
KEY_KP1 - KEY_UP
```

(output will differ based on key and duration of the key press)

Take note that numpads will often fire KEY_NUMPAD in addition to the key being
pressed. This can be ignored.

To configure a key, follow this format:

```

BINDS {
	<KEYCODE> {
		.. options ..

		<EVENT> {
			.. commands ..
		}
	}
}
```

Formatting and indents matter!

Supported events are:

```
ON_PRESS
ON_RELEASE
```

Where `commands` is:

```
RUN <program/script/etc>
TYPE <string>
KEY <keycode>
LAYER <layer>
HOTLAYER <layer>
MODELAYER <layer>
```

`options` only supports one command at the time of writing:

`BIND <keycode>`

(this is a shortcut to doing `ONPRESS [...] KEY <keycode>`)

Save the config file. Now run:

`./macropad /path/to/config/file`

# Example Config

I've attached my personal config file to this repo: [keypad.conf](keypad.conf).
