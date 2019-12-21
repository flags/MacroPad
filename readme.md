# MacroPad

This is a tool for turning any key-based input device into a "macropad" for
triggering commands on your PC. Although designed with traditional keyboard
numpads in mind, MacroPad will work with any device that fires keycodes.

MacroPad intercepts keycodes on a per-device basis, meaning multiple keyboards
can be plugged in and configured independently.

MacroPad's most powerful feature is layering, which allows keys to change the
mapping of the device on the fly. See `Layering` below.


## Use

First, ensure you have the `pytho-evdev` module installed via `pip` or your
distro's package manager. In Arch Linux, use `python-evdev`.

Clone this repo to a directory of your choosing, then run:

`./macropad.py --detect`

Follow the on-screen instructions. Note the location of the configuration file,
then open it in the text editor of your choosing.

### Configuration Workflow

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

## Layering

Layers are MacroPad's way to managing multiple different binds per key. It works
as follows:

```
Numpad 1: switch to "web" layer
Numpad 2: switch to "terminal" layer

Layer: web
	Numpad 1: open web browser to github.com
	Numpad 2: open web browser to geekhack.org

Layer: terminal
	Numpad 1: open terminal to code directory
	Numper 2: open terminal to site directory
```

To open my web brower to geekhack.org, I'd type `12` into the configred keypad.
A similar keypress is performed for opening a terminal to my code directory:
`21`.

Layers are defined in the `BINDS` section of the config file:

```
BINDS {
	KEY_KP1 {
		ON_PRESS {
			LAYER test-layer
		}
	}

	LAYER test-layer {
		KEY_KP1 {
			ON_PRESS {
				RUN foo bar
			}
		}
	}
}
