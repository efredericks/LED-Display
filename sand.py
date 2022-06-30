from evdev import InputDevice, categorize, ecodes
from copy import deepcopy
import flaschen
import random
import math
from time import sleep
from select import select
import datetime, json, os

# MAP DEFINES
EMPTY = 0
SAND = 1
WATER = 2
WALL = 3
EMITTER = 4
SAND2 = 5
SAND3 = 6
SAND4 = 7

maze_colors = {
  EMPTY: (0, 0, 0),
  SAND: (255, 255, 0),
  SAND2: (255, 0, 0),
  SAND3: (0, 255, 0),
  SAND4: (0, 0, 255),
  WATER: (0, 0, 255),
  WALL: (255, 0, 255),
  EMITTER: (0,255,0),
}


class FallingSand():
    def __init__(self, ft, gamepad):
        self.paused = False
        self.emitterColor = SAND
        self.currSand = 0
        self.currCol = 32
        self.ft = ft
        self.gamepad = gamepad
        self.isDraining = False
        self.gamemap = self.setupMap()

        self.debounce_delay = 10/1000

        self.KEYCODES = {
          'L': {'key': 294, 'callback': self.drain},
          'R': {'key': 295,'callback': None},
          'A': {'key': 288,'callback': self.dropSand},
          'B': {'key': 289,'callback': None},
          'X': {'key': 291,'callback': None},
          'Y': {'key': 292,'callback': None},
          'START':{'key': 299, 'callback': self.pauseGame},
          'SELECT':{'key': 298, 'callback': self.newMap},
        }

    # direction -> false is less than
    def debounce_dpad(self):
        # COULD MERGE WITH DEBOUNCE?

        # horiz first, then vert
        xval = self.gamepad.absinfo(ecodes.ABS_X).value
        yval = self.gamepad.absinfo(ecodes.ABS_Y).value

        sleep(self.debounce_delay)
        xval2 = self.gamepad.absinfo(ecodes.ABS_X).value
        yval2 = self.gamepad.absinfo(ecodes.ABS_Y).value

        retval = {}
        if xval < 128 and xval2 < 128:
            retval['direction'] = 'x'
            retval['value'] = False
        elif xval > 128 and xval2 > 128:
            retval['direction'] = 'x'
            retval['value'] = True
        elif yval < 128 and yval2 < 128:
            retval['direction'] = 'y'
            retval['value'] = False
        elif yval > 128 and yval2 > 128:
            retval['direction'] = 'y'
            retval['value'] = True
        else:
            retval = None
        return retval

    def debounce(self):
        keys = self.gamepad.active_keys()
        sleep(self.debounce_delay)
        return list(set(keys).intersection(self.gamepad.active_keys()))

    # pause game
    def pauseGame(self):
        self.paused = not self.paused

    # save map
    def saveMap(self):
        # get timestamp as filename
        fname = str(datetime.datetime.now()).replace(' ', '-')
        while (os.path.exists(fname)):
            fname = str(datetime.datetime.now()).replace(' ', '-')
        with open(fname, 'w') as f:
            json.dump(self.gamemap, f)


    # trigger new map
    def newMap(self):
        self.gamemap = self.setupMap()

    # create an empty map
    def setupMap(self):
        gamemap = []
        for y in range(self.ft.height):
            line = []
            for x in range(self.ft.width):
                line.append([EMPTY,maze_colors[EMPTY]])
            gamemap.append(line)
        return gamemap

    # drain from the bottom
    def drain(self):
        self.isDraining = not self.isDraining

    # screen handlers
    def clearScreen(self, col=(0,0,0)):
        for y in range(self.ft.height):
            for x in range(self.ft.width):
                self.ft.set(x,y,col)

    def drawMap(self):
        for y in range(self.ft.height):
            for x in range(self.ft.width):
                self.ft.set(x, y, self.gamemap[y][x][1])

    # drop sand from a column in the first row
    def dropSand(self):
        col = random.randint(0,220)

        if self.currSand == 0:
            sandcol = maze_colors[SAND]
        elif self.currSand == 1:
            sandcol = maze_colors[SAND2]
        elif self.currSand == 2:
            sandcol = maze_colors[SAND3]
        else:
            sandcol = maze_colors[SAND4]

        r = sandcol[0]
        g = sandcol[1]
        b = sandcol[2]

        if r > col:
            r -= col
        if g > col:
            g -= col
        if b > col:
            b -= col

        scol = (r, g, b)
        self.gamemap[0][self.currCol] = [SAND, scol]


    # get cell value
    def getCell(self, x, y):
        if y < 0 or y > len(self.gamemap)-1 or x < 0 or x > len(self.gamemap[0])-1:
            return None
        return self.gamemap[y][x]

    # main loop
    def execute(self):
        print("Running falling sand")

        done = False

        ## initially draw
        self.drawMap()
        self.ft.set(self.currCol, 0, maze_colors[self.emitterColor])
        self.ft.send()

        while not done:
            self.drawMap()

            #keys = self.gamepad.active_keys()
            keys = self.debounce()

            # draw emitter
            if self.currSand == 0: self.emitterColor = SAND
            elif self.currSand == 1: self.emitterColor = SAND2
            elif self.currSand == 2: self.emitterColor = SAND3
            else: self.emitterColor = SAND4

            self.ft.set(self.currCol, 0, maze_colors[self.emitterColor])


            # keyboard events
            for k,v in self.KEYCODES.items():
                if v["key"] in keys:
                    if v["callback"] is not None:
                        r = v["callback"]()
                        if r == "done":
                            done = True

            # debounced single key presses
            # --- DOESNT WORK WELL, can't seem to distinguish axes
            #event = self.gamepad.read_one()
            #if event is not None:
            #    if event.code == ecodes.ABS_Y and event.value == 128: #up
            #        self.currSand += 1
            #        if self.currSand > 3:
            #            self.currSand = 0

            # multiple key handler (irrespective of mode)
            if self.KEYCODES["L"]["key"] in keys and self.KEYCODES["R"]["key"] in keys:
                done = True
                break

            #if self.KEYCODES["START"]["key"] in keys and self.KEYCODES["R"]["key"] in keys:
            #    print("Saving map")
            #    self.saveMap()

            # dpad events
            dpad = self.debounce_dpad()
            if dpad is not None:
                if dpad['direction'] == 'x':
                    if dpad['value']:
                        self.currCol += 1
                    else:
                        self.currCol -= 1
                else:
                    self.currSand += 1
                    if self.currSand > 3:
                        self.currSand = 0
#            if self.gamepad.absinfo(ecodes.ABS_X).value < 128:
#                self.currCol -= 1
#            if self.gamepad.absinfo(ecodes.ABS_X).value > 128:
#                self.currCol += 1
#
#            if self.gamepad.absinfo(ecodes.ABS_Y).value < 128:
#                self.currSand += 1
#                if self.currSand > 3:
#                    self.currSand = 0


            #if self.gamepad.absinfo(ecodes.ABS_Y).value > 128:
            #    pass

            if self.currCol < 0: self.currCol = 0
            if self.currCol > self.ft.width-1: self.currCol = self.ft.width-1

            # sand updates
            for y in range(self.ft.height-1, -1, -1):
                for x in range(self.ft.width):
                    direction = random.choice([-1, 1])
                    if self.gamemap[y][x][0] == SAND:
                        if self.getCell(x, y+1) is not None and \
                           self.getCell(x, y+1)[0] == EMPTY:
                            col = self.gamemap[y][x][1]
                            self.gamemap[y][x] = [EMPTY,maze_colors[EMPTY]]
                            self.gamemap[y+1][x] = [SAND,col]
                        elif self.getCell(x+direction, y+1) is not None and \
                             self.getCell(x+direction, y+1)[0] == EMPTY:
                            col = self.gamemap[y][x][1]
                            self.gamemap[y][x] = [EMPTY,maze_colors[EMPTY]]
                            self.gamemap[y+1][x+direction] = [SAND,col]




            if self.isDraining:
                for i in range(self.ft.width):
                    self.gamemap[self.ft.height-1][i] = [EMPTY,maze_colors[EMPTY]]


            # draw to matrix
            self.ft.send()

            # reset game
            if done:
                break

        self.clearScreen()
        self.ft.send()
        print("Done")
        return
