from evdev import InputDevice, categorize, ecodes
from copy import deepcopy
import flaschen
import random
import math
from time import sleep
from select import select
from roguelike_sprites import *
from roguelike_map_gen import *

directions = [
  [0,-1],
  [1,0],
  [0,1],
  [-1,0],
  [-1,-1],
  [-1,1],
  [1,-1],
  [1,1]
]

class MoveableEntity():
    def __init__(self, sprite, c, r, hp=5):
        self.sprite = sprite
        self.c = c
        self.r = r
        self.hp = hp
        self.maxHP = hp

    # only update non-player entities (for now)
    def update(self):
        if self.sprite is not player:
            if random.random() > 0.8:
                d = random.choice(directions)
                return {'c': self.c + d[0], 'r': self.r + d[1]}
        return None

class Player(MoveableEntity):
    def __init__(self, c, r, hp=5):
        super().__init__(player, c, r, hp)

    def update(self, which):
        if which == ACTIONS.WAIT:
            print("waiting")


class RLGame():
    def __init__(self, ft, gamepad):
        self.ft = ft
        self.gamepad = gamepad
        self.player = Player(int(MAP_COLS/2), int(MAP_ROWS/2))#3, 3)
        self.entities = []
        self.debounce_delay = 10/1000

        self.KEYCODES = {
          'L': {'key': 294,'callback': self.player.update(ACTIONS.WAIT)},
          'R': {'key': 295,'callback': None},
          'A': {'key': 288,'callback': None},
          'B': {'key': 289,'callback': None},
          'X': {'key': 291,'callback': None},
          'Y': {'key': 292,'callback': None},
          'START':{'key': 299, 'callback': None},
          'SELECT':{'key': 298, 'callback': None},
        }

        self.game_map = self.generateMap()
        for _ in range(ENEMIES_PER_CHUNK):
            self.entities.append(MoveableEntity(orc, random.randint(1,MAP_COLS-2), random.randint(1,MAP_ROWS-2)))

    def debounce(self):
        keys = self.gamepad.active_keys()
        sleep(self.debounce_delay)
        return list(set(keys).intersection(self.gamepad.active_keys()))

    def generateMap(self):
        game_map = [[wall]*MAP_COLS for _ in range(MAP_ROWS)]

        # random walk
        center_c = int(MAP_COLS / 2)
        center_r = int(MAP_ROWS / 2)
        for _ in range(50): # iterations
            curr_c = center_c
            curr_r = center_r
            for _ in range(500): # life
                d = random.choice(directions)
                next_c = curr_c + d[0]
                next_r = curr_r + d[1]
                if next_c > 0 and next_c < len(game_map[0])-2 and \
                   next_r > 0 and next_r < len(game_map)-2:
                    game_map[next_r][next_c] = random.choice(DIRT)
                    curr_c = next_c
                    curr_r = next_c


        # ensure walled edges
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                if r == 0 or c == 0 or r == MAP_ROWS-1 or c == MAP_COLS-1:
                    game_map[r][c] = wall
                #else:
                #    if (random.random() > 0.7):
                #        game_map[r][c] = random.choice(DIRT)


        return game_map

    def isValid(self, c, r):
        if c < 0 or c > len(self.game_map[0])-1 or r < 0 or r > len(self.game_map)-1:
            return False
        if self.game_map[r][c] not in WALKABLE:
            return False
        return True

    # screen handlers
    def clearScreen(self, col=(0,0,0)):
        for y in range(self.ft.height):
            for x in range(self.ft.width):
                self.ft.set(x,y,col)

    def drawCell(self, c, r, char, hp_perc=None):
        #if char is None:
        #    char = self.game_map[r][c]

        # actual position
        startx = c * CELLSIZE
        starty = r * CELLSIZE


        numgreen = 0
        if hp_perc is not None:
            numgreen = int(CELLSIZE * hp_perc)
            if numgreen == 0: # make the last pip visible if we're at like 1hp
                numgreen = 1

        for y in range(CELLSIZE):
            for x in range(CELLSIZE):
                if hp_perc is not None and char is not dead and y == CELLSIZE-1:
                    if x < numgreen:
                        self.ft.set(startx+x, starty+y, COLORS['currHealth'])
                    else:
                        self.ft.set(startx+x, starty+y, COLORS['maxHealth'])

                elif SPRITES[char][y][x] == "0":
                    self.ft.set(startx+x, starty+y, COLORS[char])
                else:
                    self.ft.set(startx+x, starty+y, COLORS[clear])



    def drawMap(self):
        startr = 0
        startc = 0

        # sliding window around player
        if self.player.c < HALF_CAM_C: 
            startc = 0
        elif self.player.c >= MAP_COLS - HALF_CAM_C:
            startc = MAP_COLS - NUMCELLS
        else:
            startc = self.player.c - HALF_CAM_C

        if self.player.r < HALF_CAM_R: 
            startr = 0
        elif self.player.r >= MAP_ROWS - HALF_CAM_R:
            startr = MAP_ROWS - NUMCELLS
        else:
            startr = self.player.r - HALF_CAM_R


        # draw map
        _r = 0 # screen coords
        _c = 0
        endr = startr + NUMCELLS
        endc = startc + NUMCELLS
        for r in range(startr, endr):
            for c in range(startc, endc):
                self.drawCell(_c, _r, self.game_map[r][c])

                for e in self.entities:
                    if e.r >= startr and e.r < endr and e.c >= startc and e.c < endc:
                        if r == e.r and c == e.c:
                            self.drawCell(_c, _r, e.sprite, e.hp / e.maxHP)

                if r == self.player.r and c == self.player.c:
                  self.drawCell(_c, _r, self.player.sprite, self.player.hp / self.player.maxHP)

                _c += 1
            _c = 0
            _r += 1

        
#        for r in range(NUMCELLS):#len(self.game_map)):
#            for c in range(NUMCELLS):#len(self.game_map[0])):
#                self.drawCell(c, r)

        #for y in xrange(self.ft.height):
        #    for x in xrange(self.ft.width):
                #self.ft.set(x, y, COLORS[self.maze[y][x]])


    def execute(self):
        print("Running Roguelike game.")

        self.clearScreen()
        self.ft.send()
        done = False 
        dirty = True
        while not done:
            if dirty:
                for e in self.entities:
                    if e.sprite is not dead:
                        new_pos = e.update()
                        if new_pos is not None and self.isValid(new_pos['c'], new_pos['r']):
                            e.c = new_pos['c']
                            e.r = new_pos['r']
            
                self.drawMap()
                #self.drawCell(self.player['c'], self.player['r'], player)
                self.ft.send()
                dirty = False

            #keys = self.gamepad.active_keys()
            keys = self.debounce()

            # keyboard events
            for k,v in self.KEYCODES.items():
                if v["key"] in keys:
                    dirty = True
                    if v["callback"] is not None:
                        r = v["callback"]()
                        if r == "done":
                            done = True

            # multiple key handler (irrespective of mode)
            if self.KEYCODES["L"]["key"] in keys and self.KEYCODES["R"]["key"] in keys:
                done = True

            # dpad events
            next_r = self.player.r
            next_c = self.player.c
            if self.gamepad.absinfo(ecodes.ABS_X).value < 128:
                dirty = True
                next_c -= 1
            if self.gamepad.absinfo(ecodes.ABS_X).value > 128:
                dirty = True
                next_c += 1
            if self.gamepad.absinfo(ecodes.ABS_Y).value < 128:
                dirty = True
                next_r -= 1
            if self.gamepad.absinfo(ecodes.ABS_Y).value > 128:
                dirty = True
                next_r += 1

            if self.isValid(next_c, next_r):
                enemyThere = False
                deadEntity = False
                for e in self.entities:
                    if next_c == e.c and next_r == e.r:
                        enemyThere = True
                        e.hp -= 1
                        if e.hp < 0: 
                            e.hp = 0
                            e.sprite = dead
                            deadEntity = True

                # blank spot or there is a corpse but it is dead
                if not enemyThere or (enemyThere and deadEntity):
                    self.player.c = next_c
                    self.player.r = next_r




            if done:
                break

            sleep(0.10)

        self.ft.send()
        print("Done")
        return
