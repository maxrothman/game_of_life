#!/usr/bin/python

import Xlib.display
import random
import time
import os

import Image

# Quoth http://www.dis.uniroma1.it/~liberato/screensaver/simplesquares.html
#
#    1. Open the display: this is used to connect to the X server, and
#       allows the program to draw.

def run_saver(window=None):
    """main loop of a screensaver"""

    # load it
    myface = Image.open(os.path.expanduser("~/.zpix/eichin.jpg"))

    display = Xlib.display.Display()

#    2. Determine the root window: this is the window that is used by
#       xscreensaver modules as a canvas for drawing.
    rootscreen = display.screen()
    if window:
        window = int(window, 16)
        window = display.create_resource_object('window', window)
    else:
        window = rootscreen.root

#    3. Create a graphic context: a graphic context tells how drawing
#       is made (for example, it contains the foreground color).

    gc = window.create_gc(
        foreground = rootscreen.white_pixel,
        )

#    4. Draw something.

    while True:

        if random.randint(0, 10) < 6:
            # random color
            new_pixel = random.randint(0, 2**24)
            gc.change(foreground=new_pixel)
            window.rectangle(gc,
                             random.randint(0, rootscreen.width_in_pixels), # x
                             random.randint(0, rootscreen.height_in_pixels), # y
                             50, # width
                             40, # height
                             )
        else:
            # ideas (but not code) from:
            # http://www.koders.com/python/fidC379BA6783F3A055BA9D24B14438390CE4B70769.aspx
            # Circus, csetroot.py; turns out that code is in Xlib drawable.py now.
            assert myface.mode == "RGB", "wrong PIL mode, only ZPixmap implemented"
            window.put_pil_image(gc,
                                 random.randint(0, rootscreen.width_in_pixels), # x
                                 random.randint(0, rootscreen.height_in_pixels), # y
                                 myface,
                                 )
        if random.randint(0, 500) < 1:
            window.clear_area(0, 0, 0, 0) # clear_window
#    5. Flush the output (make drawing visible).
        display.flush()
        time.sleep(0.01) # not 10us...


    display.flush()

if __name__ == "__main__":
    run_saver(os.getenv('XSCREENSAVER_WINDOW'))
    # see http://www.dis.uniroma1.it/~liberato/screensaver/install.html
    # for how to configure your .xscreensaver entry
