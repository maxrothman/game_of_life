#!/usr/bin/python
#lovingly ripped off of <www.thok.org/intranet/python/exif/xss_colorsquares.py>

import Xlib.display
import random
import time
import os


CELL_SIZE = 70   #in pixels


class ScreenSaver(object):
  def __init__(self, window):
  # Quoth http://www.dis.uniroma1.it/~liberato/screensaver/simplesquares.html
  #
  #    1. Open the display: this is used to connect to the X server, and
  #       allows the program to draw.
    self.display = Xlib.display.Display()

  #    2. Determine the root window: this is the window that is used by
  #       xscreensaver modules as a canvas for drawing.
    self.rootscreen = self.display.screen()
    if window:
      window = int(window, 16)
      self.window = self.display.create_resource_object('window', window)
    else:
      self.window = rootscreen.root

  #    3. Create a graphic context: a graphic context tells how drawing
  #       is made (for example, it contains the foreground color).
    self.gc = self.window.create_gc()

    # initialize grid-to-pizel map
    self.xmax = self.rootscreen.width_in_pixels / CELL_SIZE
    self.ymax = self.rootscreen.height_in_pixels / CELL_SIZE
    self.store = []

    self.main()

  def render(self, x, y):
    # random color
    new_pixel = random.randint(0, 2**24)
    self.gc.change(foreground=new_pixel)

    self.window.fill_arc(self.gc,
        x*CELL_SIZE, y*CELL_SIZE,   #x, y
        CELL_SIZE, CELL_SIZE,       #width, height
        0, 360*64)                  #rotation, 1/64ths of degrees to draw

  def main(self):
    while True:
      if self.store:
        self.render(*self.store.pop())
      else:
        self.window.clear_area(0, 0, 0, 0) # clear_window
        self.store = [(x,y) for x in range(0, self.xmax) for y in range(0, self.ymax)]
        random.shuffle(self.store)

  #    5. Flush the output (make drawing visible).
      self.display.flush()
      time.sleep(0.05)


if __name__ == "__main__":
  ScreenSaver(os.getenv('XSCREENSAVER_WINDOW'))
  # see http://www.dis.uniroma1.it/~liberato/screensaver/install.html
  # for how to configure your .xscreensaver entry
