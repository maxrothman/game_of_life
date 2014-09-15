BOARD_X=40
BOARD_Y=40
FULLSCREEN=True   #overrides BOARD_X and BOARD_Y DOESN'T WORK
CHANCE=0
STEP=0.05 #0 for key step
STATES={'off': ' ', 'on': 'o'}

import curses, time, sys
from random import random

class GameWindow:
  def __init__(self, screen):
    self.screen = screen
    curses.mousemask(1)
    screen.nodelay(1)

    if STEP:
      self.step = STEP
      self.pause = False
    else:
      self.pause = True
      self.step = 0

    if FULLSCREEN:
      self.BOARD_Y, self.BOARD_X = screen.getmaxyx()
      self.BOARD_X /= 2
    else:
      self.BOARD_Y, self.BOARD_X = BOARD_Y, BOARD_X
  
    self.main()

  def render(self, board):
    for i,l in enumerate(board):
      self.screen.addstr(i, 0, ' '.join(STATES['on'] if c else STATES['off'] for c in l))
  
    self.screen.refresh()
  
  def main(self):
    game = game_of_life(self.BOARD_Y, self.BOARD_X, board=theboard, neighbors=neighbors_torroidal)

    while True:
      try:
        k = self.screen.getch()
        if k==ord(' '):
          self.pause = not self.pause
          if self.pause:
            self.screen.nodelay(0)
            self.step = 0
          else: 
            self.screen.nodelay(1)
            self.step = STEP
        elif k==curses.KEY_MOUSE:
          _, x, y, _, state = curses.getmouse()
          if x%2==0:    #map from visual with spaces in between each spot to board
            x = x/2
            if state==curses.BUTTON1_RELEASED and 0<=x<self.BOARD_X and 0<=y<self.BOARD_Y:
              board[y][x] = not board[y][x]
              self.render(board)
        else:
          time.sleep(self.step)
          board = next(game)
          self.render(board)
  
      except curses.error:
        pass

def neighbors_hard(x, y, xmax, ymax):
  '''Returns the neighbors of the given cell. 
  Cells beyond xmax and ymax are assumed dead.'''
  return [
    (i, j) for i in range(x-1, x+2) for j in range(y-1, y+2)
    if (i,j)!=(x,y) if i<xmax and i>=0 if j<ymax and j>=0
  ]

def neighbors_torroidal(x, y, xmax, ymax):
  '''Returns the neighbors of the given cell. Loops around xmax and ymax.'''
  return [
    (i-xmax if i>=xmax else xmax+i if i<0 else i,
     j-ymax if j>=ymax else ymax+j if j<0 else j
    )
    for i in range(x-1, x+2) for j in range(y-1, y+2)
    if (i,j)!=(x,y)
  ]

def game_of_life(xmax, ymax, chance=.2, board=None, neighbors=None):
  '''Generator that yields successive generations of Conway's Game of Game of Life
  
  xmax, ymax: dimensions of the board
  board: a starting board (must have dimensions xmax,ymax)
  chance: if board==None, the starting chance for a cell to be "alive"
  '''
  if not board:
    board = [[random()<chance for y in range(ymax)] for x in range(xmax)]
  if not neighbors:
    neighbors = neighbors_torroidal
  
  while True:
    newboard = [[None for _ in range(ymax)] for _ in range(xmax)]

    for x in range(len(board)):
      for y in range(len(board[0])):
        nbrs = sum(board[i][j] for i,j in neighbors(x, y, xmax, ymax))
        if board[x][y]:
          newboard[x][y] = 2<=nbrs<=3
        else:
          newboard[x][y] = nbrs==3

    yield newboard
    board = newboard

class Board(object):
  '''Sparse representation of a board.

  Usage: myboard[x, y] -> boolean

  You can optionally specify a starting board with `initial`,
  an iterable of x-y pairs of live cells.
  '''
  #Internal representation: set of x-y pairs of live cells
  def __init__(self, xmax, ymax, initial=None):
    self.xmax, self.ymax = xmax, ymax
    self.store = set() if init is None else set(init)
    if any(x>=xmax or x<0 or y>=ymax or y<0 for x,y in self.store):
      raise ValueError("Out-of-bound initial coordinate")

  def __len__(self):
    return len(self.store)

  def _verify(self, k):
    if k[0]>=xmax or k[0]<0 or k[1]>=ymax or k[1]<0:
      raise KeyError(k)
    elif not isinstance(k, tuple) or len(k)!=2:
      raise ValueError('Keys must be of the form (x,y)')

  def __getitem__(self, k):
    _verify(k)
    return k in self.store

  def __setitem__(self, k, v):
    _verify(v)
    if v:
      self.store.add(k)
    else:
      self.store.discard(k)

  def __iter__(self):
    return iter(self.store)

  def __repr__(self):
    return [[self.__getitem__(x,y) for x in range(xmax)] for y in range(ymax)]
    

glidergun=[[0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, 
           [0]*10+[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]+[0]*10,
           [0]*10+[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]+[0]*10,
           [0]*10+[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]+[0]*10,
           [0]*10+[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]+[0]*10,
           [0]*10+[1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]+[0]*10,
           [0]*10+[1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]+[0]*10,
           [0]*10+[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]+[0]*10,
           [0]*10+[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]+[0]*10,
           [0]*10+[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]+[0]*10,
           [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56
          ]

if __name__ == '__main__':
  try:
    curses.wrapper(GameWindow)
  except KeyboardInterrupt:
    sys.exit()
  #print '\n'.join(' '.join(i) for i in board)
