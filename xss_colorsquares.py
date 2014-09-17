#!/usr/bin/python
#lovingly ripped off of <www.thok.org/intranet/python/exif/xss_colorsquares.py>

import Xlib.display
import random
import time
import os


CELL_SIZE = 10   #in pixels


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
    self.store = set()

    self.main()

  def render(self, x, y):
    self.store.remove((x,y))
    self.window.fill_arc(self.gc,
        x*CELL_SIZE, y*CELL_SIZE),  #x, y
        CELL_SIZE, CELL_SIZE,       #width, height
        0, 360*64)                  #rotation, 1/64ths of degrees to draw
    self.display.flush()

  def main(self):
    while True:
      # random color
      new_pixel = random.randint(0, 2**24)
      self.gc.change(foreground=new_pixel)
      self.window.fill_arc(self.gc,
               random.randint(0, self.rootscreen.width_in_pixels), # x
               random.randint(0, self.rootscreen.height_in_pixels), # y
               100, # width
               100, # height,
               0, 360*64
               )
      
      if random.randint(0, 500) < 1:
        self.window.clear_area(0, 0, 0, 0) # clear_window
  #    5. Flush the output (make drawing visible).
      self.display.flush()
      time.sleep(0.1) # not 10us...


if __name__ == "__main__":
  ScreenSaver(os.getenv('XSCREENSAVER_WINDOW'))
  # see http://www.dis.uniroma1.it/~liberato/screensaver/install.html
  # for how to configure your .xscreensaver entry
