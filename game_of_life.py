BOARD_X=40
BOARD_Y=40
FULLSCREEN=True   #overrides BOARD_X and BOARD_Y
CHANCE=.5
STEP=0.05
PAUSE=False
STATES={'off': ' ', 'on': 'o'}

import curses, time, sys
from random import random

class GameWindow:
  def __init__(self, screen):
    self.screen = screen
    curses.mousemask(1)
    screen.nodelay(1)

    self.step = STEP
    self.pause = PAUSE

    if FULLSCREEN:
      self.BOARD_Y, self.BOARD_X = screen.getmaxyx()
      self.BOARD_X /= 2
    else:
      self.BOARD_Y, self.BOARD_X = BOARD_Y, BOARD_X
  
    self.main()

  def render(self, board):
    for i,l in enumerate(board.to_full()):
      self.screen.addstr(i, 0, ' '.join(STATES['on'] if c else STATES['off'] for c in l))
  
    self.screen.refresh()
  
  def main(self):
    game = game_of_life(self.BOARD_X, self.BOARD_Y)
    if self.pause:
      self.screen.nodelay(0)
      self.step = 0

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
              board[x,y] = not board[x,y]
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

def game_of_life(xmax, ymax, chance=.2, start_board=None, neighbors=None):
  '''Generator that yields successive generations of Conway's Game of Game of Life
  
  xmax, ymax: dimensions of the board
  board: an iterable of x,y pairs to start the board with
  chance: if board==None, the starting chance for a cell to be "alive" (flat distribution)
  '''
  if start_board is None:
    start_board = set((x,y) for x in range(xmax) for y in range(ymax) if random()<chance)
  
  board = Board(xmax, ymax, initial=start_board)

  if neighbors is None:
    neighbors = neighbors_torroidal
  
  while True:
    newboard = Board(xmax, ymax)

    for x,y in board:
      nbrs = neighbors(x, y, xmax, ymax)

      #check this cell for over/undercrowding
      newboard[x,y] = 2<=sum(board[i,j] for i,j in nbrs)<=3

      #check its neighbors for spawning
      for i,j in nbrs:
        if not board[i,j]:
          newboard[i,j] = sum(board[k,l] for k,l in neighbors(i, j, xmax, ymax)) == 3

    yield newboard
    board = newboard


class Board(object):
  '''Sparse representation of a board.

  Usage: myboard[x, y] -> boolean

  xmax, ymax are the number of cells in each direction
  (i.e. if it were zero-indexed, the highest-index cell would be xmax-1, ymax-1)

  You can optionally specify a starting board with `initial`,
  an iterable of x-y pairs of live cells.
  '''
  #Internal representation: set of x-y pairs of live cells
  def __init__(self, xmax, ymax, initial=None):
    self.xmax, self.ymax = xmax, ymax
    self.store = set() if initial is None else set(initial)
    if any(x>=xmax or x<0 or y>=ymax or y<0 for x,y in self.store):
      raise ValueError("Out-of-bound initial coordinate")

  def __getitem__(self, k):
    self._verify(k)
    return k in self.store

  def __setitem__(self, k, v):
    self._verify(k)
    if v:
      self.store.add(k)
    else:
      self.store.discard(k)

  def __iter__(self):
    '''Returns an iterator over each cell (x1,y1, x2,y1, ..., x1,y2, ...)'''
    return iter(self.store)

  def _verify(self, k):
    if k[0]>=self.xmax or k[0]<0 or k[1]>=self.ymax or k[1]<0:
      raise KeyError(k)
    elif not isinstance(k, tuple) or len(k)!=2:
      raise ValueError('Keys must be of the form (x,y)')  

  def to_full(self):
    '''Returns a nested iterator over the board in non-sparse form [[x1,y1, x2,y1, ...], [x1,y2, ...]]'''
    return ((self.__getitem__((x,y)) for x in range(self.xmax)) for y in range(self.ymax))


glidergun = [(1,5), (2,5), (1,6), (2,6), (11,5), (11,6), (11,7), (12,4), (13,3), (14,3),
            (12,8), (13,9), (14,9), (15,6), (17,6), (18,6), (17,5), (17,7), (16,4), (16,8),
            (21,5), (21,4), (21,3), (22,3), (22,4), (22,5), (23,2), (23,6), (25,2), (25,1),
            (25,6), (25,7), (35,3), (35,4), (36,3), (36,4)]


if __name__ == '__main__':
  try:
    curses.wrapper(GameWindow)
  except KeyboardInterrupt:
    sys.exit()
  #print '\n'.join(' '.join(i) for i in board)
