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

#### Timed Layers

The previous example detailed holding a key to reveal a layer. However, it's
also possible to switch to a layer and have it remain after releasing the button
that triggered it. This is a timed layer.

In this example, the `/` key activates a layer containing a number of text
snippits that I commonly use while programming. Since there is no command bound
to the release of the `/` key, MacroPad gives the user around 2 seconds to enter
a followup keypress on the layer before returning to the default one.

After hitting my macro for printing out a long function name (`/` followed by
`7`), MacroPad automatically switches back to the default layer and waits for
input.

#### Mode Layers

Triggering a macro within a layer automatically sends control back to the
default layer.

However, the default layer MacroPad returns to can be defined by establishing a
"mode layer." This is useful if you'd like to set up keybinds for gaming,
browsing the web, or using a particular program (image editor, etc.)

#### Hot Layers

This layer type is similar to a timed layer, except MacroPad doesn't return to
the default layer after a keypress, allowing multiple macros to be fired on the
same layer in succession. MacroPad resets to the default layer roughly 2 seconds
after the last keypress is made.

## Creating a Layout (by Example)

The best piece of advice I can give is to define your goals. This may seem
obvious, but a bit of planning can avoid massive reconfiguring and unlearning
bad habits/muscle memory later on.

Here the goals for my main macropad:

* Workspace organization (i.e., window management.)
* Quick launching of dev tools
* "Bash snippits" for quick terminal use
* A mode for browsing the web

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

