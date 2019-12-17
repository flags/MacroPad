# MacroPad Planning
## Creating a Layout

The best piece of advice I can give is to define your goals. This may seem
obvious, but a bit of planning can avoid massive reconfiguring and unlearning
bad habits/muscle memory later on.

Here the goals for my main macropad:

* Workspace organization (i.e., window management.)
* Quick launching of dev tools
* "Bash snippits" for quick terminal use

The two main layers will be `terminal` and `workspace`.

By default I will mark off the directional keys on the numpad (`2, 4, 6, 8`) for
movement between windows. This is a function I want to work on the default layer
since holding a modkey would require weird hand and finger placement.

### Terminal Layer

`1` will trigger the terminal layer.

Pressing and releasing `1` will spawn a terminal, effectively turning `1` into a
modkey. Holding `1` and hitting `2, 3, 4` will spawn a terminal in a specific
directory depending on key. My current project's folder will be bound to `4`,
for example.

### Workspace Layer

`5` activates the workspace layer.

`6` tells my window manager that the next window will be opened to the right of
the current focused window. `2` does the same, execpt it will open below the
current window.

Pressing `5` makes the current window fullscreen.

### Snippits Layer

`/` opens up the snippits layer. These are terminal commands.

`4` goes to `~/code/MacroPad`.

`.` navigates to the `~/.config` directory. It can also be held, after which
pressing `5` will run `vim ~/.config/i3/config`.

### Common Inputs

Here are commonly-used inputs:

#### 3-Window Layout

`1->4 56 1->4 52 1->4`

## Usage Patterns
### ModKey / Run on Release

```
KEY_KP2
	ON_PRESS LAYER terminal

LAYER terminal
	KEY_KP2
		ON_RELEASE RUN st

	KEY_KP3
		ON_PRESS RUN cd ~/code && st
```

This allows KP2 to work as a modkey and a macro button.

Pressing and releasing it spawns a terminal.

Holding it and pressing KP3 opens a terminal in the mentioned directory.

