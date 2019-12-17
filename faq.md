### Why isn't MacroPad free software?

The equivalent hardware needed to recreate MacroPad's functionality ranges
anywhere from $15 to $100+, the most versatile of which is a USB dongle that
turns a single normal keyboard into a rebindable one for around $50.

MacroPad costs signicantly less and can effectively rebind any number of
devices that output keycodes. It's a better value by a wide margin.

### How is MacroPad different than other macro/hotkey software?

My goal with MacroPad wasn't just to create software to trigger commands, but
to also convince users to try a different way of using their PC. MacroPad
encourages the stringing together of smaller macros to accomplish a larger task,
like opening a number of programs and arranging them on screen. This is done
through "layers" and "modkeys". For example, I use the following string of
inputs to set up my MacroPad development environment:

`1->4, 7, 56, 1->4, 52, 1, 4`

This translates to: Open terminal to project directory, open Vim, open next
window to the right of the current one, open another terminal, open next window
below the current one, open a final terminal, then focus the leftmost window.

A traditional "macro" would execute all these commands at the press of a button,
useful only for that specific situation. By chaining together smaller macros,
the desired outcome can be created on-the-fly. Over time, these inputs become
faster and easier to perform.

MacroPad also specifically rebinds a single device's inputs instead of watching
and reacting to input across any device connected to the PC, allowing multiple
extra input devices to be connected and configured via MacroPad.

Other software works just fine if you only want a button to open a program, and
you should use them if that's your intended use case.

### What are the limitations of the free version?

* One device.
* X NUMBER OF layers.
* No technical support.
