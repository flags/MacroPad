# MacroPad Configuration
## Introduction

This document will teach you everything you need to know about building your
ideal MacroPad configuration file.

## Concepts
### The Single Action Approach

MacroPad encourages a "single action" approach to building macros, i.e., instead
of assigning a single button to open a text editor, spawn a terminal, then
navigate to a certain directory in that terminal, you should instead break these
actions down into individual macros. By doing this, you'll create "building
blocks" for crafting macros on the fly.

### Layers

Here's an obvious example:

If you press `q` on your keyboard, it will print a `q`. If you hold `Shift` and
hit `q`, it will print a `Q`. This is better than having both a key for `q` and
`Q`. MacroPad does something similar to help build more complex sets of macros
with fewer keys.

Unless specified, all macros are entered into the "default" layer. This means if
`1` is bound to open my text editor, pressing `1` will open my text editor.
Simple enough. It may not be immediately obvious why you would ever need
anything other than the default layer, so let's use some examples:

* Open a text editor and edit a specific file
* Open a specific website in your browser
* Navigate to a certain directory in your terminal

All of these ask the question of "which?": Which file? Which website? Which
directory?

#### Smarter Program Launching

Instead of just launching a text editor, `1` can open up a layer of macros
dedicated to altering the launch parameters of the text editor.

When `1` is held, the `2` and `3` keys will become bound to `open
daily_planner.txt` and `open monthly_planner.txt`. Not pressing any of these and
simply releasing the `1` key will launch the editor with an empty document.

```
BINDS {
	KEY_KP1 {
		ON_PRESS {
			LAYER text-editor
		}
	}

	LAYER text-editor {
		KEY_KP1 {
			ON_RELEASE {
				RUN geany
			}
		}

		KEY_KP2 {
			ON_PRESS {
				RUN geany ~/docs/daily_planner.txt
			}
		}

		KEY_KP3 {
			ON_PRESS {
				RUN geany ~/docs/monthly_planner.txt
			}
		}
	}
}

```

#### Timed Layers

The previous example detailed holding a key to reveal a layer. However, it's
also possible to switch to a layer and have it remain after releasing the button
that triggered it. This is a timed layer.

In this example, the `/` key activates a layer containing a number of text
snippits that I commonly use while in the terminal. Since there is no command
bound to the release of the `/` key, MacroPad gives the user around 2 seconds to
enter a followup keypress on the layer before returning to the default one.

After hitting my macro for going to my project directory (`/` followed by `4`),
MacroPad automatically switches back to the default layer and waits for input.

```
BINDS {
	KEY_KPSLASH {
		ON_PRESS {
			LAYER snippits
		}
	}

	LAYER snippits {
		KEY_KP4 {
			ON_PRESS {
				TYPE "cd ~/code/MacroPad"
				KEY KEY_ENTER
			}
		}
	}
}
```

#### Hot Layers

This layer type is similar to a timed layer, except MacroPad doesn't return to
the default layer after a keypress, allowing multiple macros to be fired on the
same layer in succession. MacroPad resets to the default layer roughly 2 seconds
after the last keypress is made.

```
BINDS {
	KEY_KPPLUS {
		ON_PRESS {
			KEY KEY_F
			HOTLAYER browser-nav
		}
	}

	LAYER browser-nav {
		KEY_KP0 {
			BIND KEY_0
		}

		KEY_KP1 {
			BIND KEY_1
		}

		KEY_KP2 {
			BIND KEY_2
		}

		<snip: other keypad keys here>
	}
}
```

#### Mode Layers

Triggering a macro within a layer automatically sends control back to the
default layer.

However, the default layer MacroPad returns to can be defined by establishing a
"mode layer." This is useful if you'd like to set up keybinds for gaming,
browsing the web, or using a particular program (image editor, etc.)

`qutebrowser` is a web browser that has the majority of its controls bound to
the keyboard. This includes changing tabs, selecting links, and scrolling, all
good targets for MacroPad.

In my personal MacroPad config, I have a `browser` mode layer that sets up the
aforementioned functions, then provides timed layers and hot layers for things
like link selection and choosing bookmarks.

```
BINDS {
	KEY_KPASTERISK {
		ON_PRESS {
			MODELAYER browser
		}
	}

	LAYER browser {
		KEY_KP1 {
			BIND KEY_LEFTCTRL+KEY_U
		}

		KEY_KP2 {
			BIND KEY_J
		}

		KEY_KP3 {
			BIND KEY_LEFTCTRL+KEY_D
		}

		KEY_KP4 {
			BIND KEY_LEFTSHIFT+KEY_H
		}

		KEY_KP6 {
			BIND KEY_LEFTSHIFT+KEY_L
		}

		KEY_KP7 {
			BIND KEY_LEFTSHIFT+KEY_K
		}

		KEY_KP8 {
			BIND KEY_K
		}

		KEY_KP9 {
			BIND KEY_LEFTSHIFT+KEY_J
		}
	}
}
```

