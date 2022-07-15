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
    def __init__(self, sprite, c, r, hp=5, atk=1):
        self.sprite = sprite
        self.c = c
        self.r = r
        self.hp = hp
        self.maxHP = hp
        self.atk = atk

    # only update non-player entities (for now)
    def update(self, neighbors):
        if self.sprite is not player:
            if neighbors['isPlayer']: # player is adjacent - don't care which direction at the moment TBD
                return {'c': None, 'r': None, 'attack': self.atk}
            else:
                if random.random() > 0.8:
                    next_pos = random.choice(neighbors['positions'])
                    return {'c': next_pos['c'], 'r': next_pos['r'], 'attack':None}
        return None

class Player(MoveableEntity):
    def __init__(self, c, r, hp=5):
        super().__init__(player, c, r, hp)

    def update(self, which):
        if which == ACTIONS.WAIT:
            self.hp += 1
            if (self.hp >= self.maxHP): self.hp = self.maxHP
        return ""


def cb():
    print("WHOA NELLY")

class RLGame():
    def __init__(self, ft, gamepad, pixels):
        self.ft = ft
        self.gamepad = gamepad
        self.pixels = pixels

        self.debounce_delay = 10/1000

        #self.game_map = self.generateMap()
        self.mapGen = MapGenerator(width=MAP_COLS, height=MAP_ROWS)
        self.game_map, p_c, p_r = self.mapGen.generateBSP()
        print(self.game_map)
        #p_c, p_r = self.getValidPos()
        self.player = Player(p_c,p_r)#int(MAP_COLS/2), int(MAP_ROWS/2))#3, 3)

        self.entities = []
        for _ in range(ENEMIES_PER_CHUNK):
            e_c, e_r = self.getValidPos()
            self.entities.append(MoveableEntity(orc, e_c, e_r, hp=3, atk=1))

        self.KEYCODES = {
          'L': {'key': 294,'callback': self.player.update, 'param': (ACTIONS.WAIT)},
          'R': {'key': 295,'callback': None},
          'A': {'key': 288,'callback': None},
          'B': {'key': 289,'callback': None},
          'X': {'key': 291,'callback': None},
          'Y': {'key': 292,'callback': None},
          'START':{'key': 299, 'callback': None},
          'SELECT':{'key': 298, 'callback': None},
        }


    def debounce(self):
        keys = self.gamepad.active_keys()
        sleep(self.debounce_delay)
        return list(set(keys).intersection(self.gamepad.active_keys()))

    """
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
    """

    def getValidPos(self):
        r = random.randint(1,MAP_ROWS-1)
        c = random.randint(1,MAP_COLS-1)
        while not self.isValid(c, r):
            r = random.randint(1,MAP_ROWS-1)
            c = random.randint(1,MAP_COLS-1)
        return c,r

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

    def getNeighbors(self, e):
        valid_positions = []
        isPlayer = False
        for d in directions:
            next_c = e.c + d[0]
            next_r = e.r + d[1]

            if self.isValid(next_c, next_r):
                if self.player.c == next_c and self.player.r == next_r:
                    isPlayer = True
                valid_positions.append({'c':next_c, 'r': next_r, 'isPlayer': isPlayer})
        return {'positions': valid_positions, 'isPlayer': isPlayer}



    def execute(self):
        print("Running Roguelike game.")

        self.clearScreen()
        self.ft.send()
        done = False 
        dirty = True
        while not done:
            # headless play
            if self.gamepad is None:
                dirty = True
                # sleep(0.5)

            #keys = self.gamepad.active_keys()
            if self.gamepad is not None:
                keys = self.debounce()

                # keyboard events
                for k,v in self.KEYCODES.items():
                    if v["key"] in keys:
                        dirty = True
                        if v["callback"] is not None:

                            if 'param' in v.keys():
                                r = v["callback"](v["param"])
                            else:
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


            if dirty:
                for e in self.entities:
                    if e.sprite is not dead:
                        neighbors = self.getNeighbors(e)
                        action = e.update(neighbors)
                        if action is not None:
                            if action['attack'] is not None: # prefer attack
                                self.player.hp -= action['attack']
                                if self.player.hp <= 0:
                                    self.player.hp = 0
                                    self.player.sprite = dead
                                    done = True

                            elif self.isValid(action['c'], action['r']): # otherwise move
                                e.c = action['c']
                                e.r = action['r']
            
                self.drawMap()
                #self.drawCell(self.player['c'], self.player['r'], player)
                self.ft.send()
                dirty = False




            if done:
                break

            sleep(0.10)

        self.ft.send()
        print("Done")
        return
