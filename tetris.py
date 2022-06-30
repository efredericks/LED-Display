#https://www.techwithtim.net/tutorials/game-development-with-python/tetris-pygame/tutorial-1/
from evdev import InputDevice, categorize, ecodes
from copy import deepcopy
import flaschen
import random
import math
from time import sleep
from select import select

# each pixel will be 2px wide
screen = [\
  "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",\
  "w                                                              w",\
  "w                                                              w",\
  "w  wwwwwwwwwwww  wwwwwwwwwwwwwwwwwwwwwwww                      w",\
  "w  w          w  w                      w                      w",\
  "w  w          w  w                      w                      w",\
  "w  w          w  w                      w                      w",\
  "w  w          w  w                      w                      w",\
  "w  w          w  w                      w                      w",\
  "w  w          w  w                      w                      w",\
  "w  w          w  w                      w                      w",\
  "w  w          w  w                      w                      w",\
  "w  w          w  w                      w                      w",\
  "w  w          w  w                      w                      w",\
  "w  wwwwwwwwwwww  w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                w                      w                      w",\
  "w                wwwwwwwwwwwwwwwwwwwwwwww                      w",\
  "w                                                              w",\
  "w                                                              w",\
  "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",\
]


# MAP DEFINES
wall = 'w'
cell = '.'
S = 's'
Z = 'z'
I = 'i'
O = 'o'
J = 'j'
L = 'l'
T = 't'

COLORS = {
  ' ': (0,0,0),
  'R': (255,0,0),
  'G': (0,255,0),
  'B': (0,0,255),
  'P': (255,0,255),
}

maze_colors = {
  ' ': (0,0,0),
  wall: (255,0,255),
  cell: (0,0,0),
  S: (0,255,0),
  Z: (255,0,0),
  I: (0,255,255),
  O: (255,255,0),
  J: (255,165,0),
  L: (0,0,255),
  T: (128,0,128),
}

shapes = {
  S: [[
      ".....",
      ".....",
      "..00.",
      ".00..",
      ".....",
      ],
      [
      ".....",
      "..0..",
      "..00.",
      "...0.",
      ".....",
      ]],
  Z: [[
      ".....",
      ".....",
      ".00..",
      "..00.",
      ".....",
      ],
      [
      ".....",
      "..0..",
      ".00..",
      ".0...",
      ".....",
      ]],
  I: [[
      "..0..",
      "..0..",
      "..0..",
      "..0..",
      ".....",
      ],
      [
      ".....",
      "0000.",
      ".....",
      ".....",
      ".....",
      ]],
  O: [[
      ".....",
      ".....",
      ".00..",
      ".00..",
      ".....",
      ]],
  J: [[
      ".....",
      ".0...",
      ".000.",
      ".....",
      ".....",
      ],
      [
      ".....",
      "..00.",
      "..0..",
      "..0..",
      ".....",
      ],
      [
      ".....",
      ".000.",
      "...0.",
      ".....",
      ".....",
      ],
      [
      ".....",
      "..0..",
      "..0..",
      ".00..",
      ".....",
      ]],
  L: [[
      ".....",
      "...0.",
      ".000.",
      ".....",
      ".....",
      ],
      [
      ".....",
      "..0..",
      "..0..",
      "..00.",
      ".....",
      ],
      [
      ".....",
      ".....",
      ".000.",
      ".0...",
      ".....",
      ],
      [
      ".....",
      ".00..",
      "..0..",
      "..0..",
      ".....",
      ]],
  T: [[
      ".....",
      "..0..",
      ".000.",
      ".....",
      ".....",
      ],
      [
      ".....",
      "..0..",
      "..00.",
      "..0..",
      ".....",
      ],
      [
      ".....",
      ".000.",
      "..0..",
      ".....",
      ".....",
      ],
      [
      ".....",
      "..0..",
      ".00..",
      "..0..",
      ".....",
      ]]
}

class Piece():
    def __init__(self, which):
        self.which = which
        self.x = 5
        self.y = 0

class TetrisGame():
    def __init__(self, ft, gamepad):
        self.paused = False
        self.ft = ft
        self.gamepad = gamepad

        self.KEYCODES = {
          'L': {'key': 294, 'callback': None},
          'R': {'key': 295,'callback': None},
          'A': {'key': 288,'callback': None},
          'B': {'key': 289,'callback': None},
          'X': {'key': 291,'callback': None},
          'Y': {'key': 292,'callback': None},
          'START':{'key': 299, 'callback': self.startBtn},
          'SELECT':{'key': 298, 'callback': None},
        }


    def startBtn(self):
        return ""
    def endGame(self):
        return "done"


    # screen handlers
    def clearScreen(self, col=(0,0,0)):
        for y in xrange(self.ft.height):
            for x in xrange(self.ft.width):
                self.ft.set(x,y,col)

    def drawBaseScreen(self):
        for y in xrange(self.ft.height):
            for x in xrange(self.ft.width):
                self.ft.set(x, y, maze_colors[screen[y][x]])

    def drawMap(self):
        pass
        #for y in xrange(self.ft.height):
        #    for x in xrange(self.ft.width):
        #        self.ft.set(x, y, maze_colors[self.maze[y][x]])

    def execute(self):
        print("Running Tetris.")

        done = False

        ## initially draw
        self.drawBaseScreen()
        #self.drawMap()
        self.ft.send()

        while not done:
            keys = self.gamepad.active_keys()
            self.drawMap()

            # keyboard events
            for k,v in self.KEYCODES.iteritems():
                if v["key"] in keys:
                    if v["callback"] is not None:
                        r = v["callback"]()
                        if r == "done":
                            done = True

            # multiple key handler (irrespective of mode)
            if self.KEYCODES["L"]["key"] in keys and self.KEYCODES["R"]["key"] in keys:
                done = self.endGame()

            # dpad events
            #if self.gamepad.absinfo(ecodes.ABS_X).value < 128:
                #snake.setDir(-1,0)
            #if self.gamepad.absinfo(ecodes.ABS_X).value > 128:
                #snake.setDir(1,0)
            #if self.gamepad.absinfo(ecodes.ABS_Y).value < 128:
                #snake.setDir(0,-1)
            #if self.gamepad.absinfo(ecodes.ABS_Y).value > 128:
                #snake.setDir(0,1)

            # draw to matrix
            self.ft.send()

            if done:
                break

            sleep(0.10)

        self.clearScreen()
        self.ft.send()
        print("Done")
        return
