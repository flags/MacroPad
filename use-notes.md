# IDEAS

* open browser to current clipboard (`pp` in qutebrowser)

### thu dec 19 2019

Tested briefly in Ubuntu via work laptop. Added a single macro and will be
adding more as I see fit.

Need more test cases. Also need to revisit how stuff like `vim` is launched.

Noticing that it's difficult to visualize a config after not using parts of it
for a while.

### wed dec 18 2019

#### Update 1

Rewrote config parsing to use traditional {} blocks instead of indents.

Working on typing for text snippits, hopefully done tonight.

Next macro will be extending the browser mode to use qutebrowser's hint via
numbers. Looking into a type of layer that resets the layer timeout each time a
button is pressed within it to make this mode possible.

#### Update 2

Above notes re: text snippits and "hot layers" are now implemented.

Browser mode is good, but too specific. More work needs to be done in normal DEs
to get a better idea of how this could benefit regular users. Right now a lot of
funtionality just feels like it's designed around i3.

xdotool is used for typing until I can get a different approach that doesn't
require X11.

### tue dec 17 2019

Established mode layers. Now have web browser binds for scrolling, page up/down,
navigating tabs, and going fw/bk in history.

Should look into snippits more. Also more terminal operations
