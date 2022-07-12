from evdev import InputDevice, categorize, ecodes
from copy import deepcopy
import flaschen
import random
import math
from time import sleep
from select import select
import numpy as np
import noise
from roguelike_sprites import p5Map

# noise
octaves = 4
frequency = 8.0 * octaves

# MAP DEFINES
EMPTY = 0
CROSS = 1
SQUARES = 2

fruit = 'f'
wall = 'w'
cell = '.'
end = '!'
unvisited = ' '
player = '@'
attract = "A"
WALKABLE = [cell, end]

directions = [
  [0,-1],
  [1,0],
  [0,1],
  [-1,0]
]

maze_colors = {
  wall: (255,0,255),
  cell: (0,0,0),
  end: (255,0,0),
  unvisited: (20,20,20),
  player: (0,255,0),
  attract: (0, 100, 0),
  fruit: (255, 255, 0),
}

class RunnerGame():
    def __init__(self, ft, gamepad):
        self.paused = False
        self.ft = ft
        self.gamepad = gamepad

        self.YNOISE = random.randint(0,100000)

        self.pixels = np.asarray(self.ft)

        # noise
        self.startx = self.ft.width
        self.basey = (self.ft.height-1) - 2

        # user defined restart
        self.triggeredEndGame = False

        self.KEYCODES = {
          'L': {'key': 294, 'callback': None},
          'R': {'key': 295,'callback': None},
          'A': {'key': 288,'callback': None},
          'B': {'key': 289,'callback': self.triggerJump},
          'X': {'key': 291,'callback': None},
          'Y': {'key': 292,'callback': None},
          'START':{'key': 299, 'callback': self.startBtn},
          'SELECT':{'key': 298, 'callback': None},
        }

        self.player = {
          'x': 2,
          'y': 32,
          'vy': 1,
          'vx': 0
        }
        self.active = False
        self.jumpTimer = 0

    def triggerJump(self):
        if self.active and self.jumpTimer == 0 and self.player['vy'] > 0:
            self.jumpTimer = 5
            self.player['vy'] = -1

    def startBtn(self):
        pass

    def getHeight(self, x):
        n = noise.snoise2(x / frequency, self.YNOISE / frequency, octaves=octaves,persistence=0.25)
        numY = int(p5Map(n, -1.0, 1.0, 0, 10))
        return self.basey - numY


    # screen handlers
    def colorScreen(self, col=(0,0,0)): # this should be clearScreen after a refactor
        self.pixels[:,:] = col

    def clearScreen(self, col=(0,0,0)):
        self.pixels[:,:] = (0,0,0)
        self.pixels[self.basey:,:] = (255,0,255)

        # ramp up

        startx = int(self.ft.width/2)
        for x in range(startx):
            self.pixels[self.getHeight(x):,x] = (80,80,80)
        
        # start generating
        for x in range(startx,self.ft.width):
            self.pixels[self.getHeight(x):,x] = (255,0,255)

        self.startx = self.ft.width

    def drawMap(self):
        #self.pixels = np.roll(self.pixels, -1, axis=1)
        #self.pixels[-5:,self.ft.width-1] = (0,0,0)
        #self.pixels[:,random.randint(0,63)] = (255,0,255)

        # clear player
        #self.pixels[self.player['y'], self.player['x']] = (0,0,0)
        #self.pixels[self.player['y']-1, self.player['x']] = (0,0,0)

        if self.active:
          # shift left
          for x in range(1,self.ft.width):
              self.pixels[:,x-1] = self.pixels[:,x]
          self.pixels[:,self.ft.width-1] = (0,0,0)

          # generate next noise val
          self.pixels[self.getHeight(self.startx):,self.ft.width-1] = (255,0,255)
          self.startx += 1





#       print(numY)

#        self.pixels = np.concatenate((self.pixels, newcol), axis=1)



        #for y in xrange(self.ft.height):
        #    for x in xrange(self.ft.width):
        #        self.ft.set(x, y, maze_colors[self.maze[y][x]])

    def execute(self):
        print("Running Runner game.")

        done = False
        self.clearScreen()
        while not done:
            keys = self.gamepad.active_keys()

            # draw player
            self.pixels[self.player['y'], self.player['x']] = (0,0,0)
            self.pixels[self.player['y']-1, self.player['x']] = (0,0,0)

            self.drawMap()

            next_y = self.player['y'] + self.player['vy']

            if not self.active: # dropping player
                if self.pixels[next_y,self.player['x']][0] == 80 and \
                   self.pixels[next_y,self.player['x']][1] == 80 and \
                   self.pixels[next_y,self.player['x']][2] == 80: 
                    self.active = True
                    #self.player['vy'] = 0
                else:
                    self.player['y'] = next_y
            else:
                # falling into a spot
                if self.pixels[next_y,self.player['x']][0] == 0 and \
                   self.pixels[next_y,self.player['x']][1] == 0 and \
                   self.pixels[next_y,self.player['x']][2] == 0: 
                    self.player['y'] = next_y

                # game over
                if self.pixels[self.player['y'],self.player['x']+1][0] == 255 and \
                   self.pixels[self.player['y'],self.player['x']+1][1] == 0 and \
                   self.pixels[self.player['y'],self.player['x']+1][2] == 255: 
                    done = True


            if self.jumpTimer > 0:
                self.jumpTimer -= 1
            else:
                self.player['vy'] = 1
                self.jumpTimer = 0



            # draw player
            if not done:
                self.pixels[self.player['y'], self.player['x']] = (0,0,255)
                self.pixels[self.player['y']-1, self.player['x']] = (255,255,0)



            # keyboard events
            for k,v in self.KEYCODES.items():
                if v["key"] in keys:
                    if v["callback"] is not None:
                        r = v["callback"]()
                        if r == "done":
                            done = True

            # multiple key handler (irrespective of mode)
            if self.KEYCODES["L"]["key"] in keys and self.KEYCODES["R"]["key"] in keys:
                done = True
            """
                # dpad events
                if self.gamepad.absinfo(ecodes.ABS_X).value < 128:
                    snake.setDir(-1,0)
                if self.gamepad.absinfo(ecodes.ABS_X).value > 128:
                    snake.setDir(1,0)
                if self.gamepad.absinfo(ecodes.ABS_Y).value < 128:
                    snake.setDir(0,-1)
                if self.gamepad.absinfo(ecodes.ABS_Y).value > 128:
                    snake.setDir(0,1)

            """
            if done:
                break


            self.ft.send()
            sleep(0.10)

        #self.clearScreen()
        self.colorScreen((255,0,0))
        self.ft.send()
        print("Done")
        sleep(2)
        return
