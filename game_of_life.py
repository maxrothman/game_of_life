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
    theboard=[[0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, [0]*56, 
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
    self.BOARD_Y = len(theboard)
    self.BOARD_X = len(theboard[0])

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



if __name__ == '__main__':
  try:
    curses.wrapper(GameWindow)
  except KeyboardInterrupt:
    sys.exit()
  #print '\n'.join(' '.join(i) for i in board)
