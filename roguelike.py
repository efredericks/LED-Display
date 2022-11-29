# todo!
# - minimap
# - multiple levels
# - different generation methods
# - text
# - enemies via config
# - add type hinting to all functions

# - maybe use the text lib now?

from evdev import InputDevice, categorize, ecodes
from dev_gui import GUIController

from copy import deepcopy
import flaschen
import random
import math
from time import sleep
from select import select
from roguelike_sprites import *
from roguelike_map_gen import *
from typing import *
from threading import Thread
from queue import Queue

from bdfparser import Font

# 8-way direction table
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
    def __init__(self, sprite, c, r, dlvl, hp=5, atk=1):
        self.sprite = sprite
        self.c = c
        self.r = r
        self.hp = hp
        self.maxHP = hp
        self.atk = atk
        self.cooldown = 2 # avoid attacking the instant that a player sidles up next to them
        self.dlvl = dlvl

    # only update non-player entities (for now)
    def update(self, neighbors):
        if self.sprite is not player:
            if neighbors['isPlayer']: # player is adjacent - don't care which direction at the moment TBD
                self.cooldown -= 1
                if self.cooldown == 0:
                    self.cooldown = 2
                    return {'c': None, 'r': None, 'attack': self.atk}
                else:
                    return {'c': None, 'r': None, 'attack': None}
            else:
                if random.random() > 0.8:
                    next_pos = random.choice(neighbors['positions'])
                    return {'c': next_pos['c'], 'r': next_pos['r'], 'attack':None}
        return None

class Player(MoveableEntity):
    def __init__(self, c, r, hp=5):
        super().__init__(player, c, r, 0, hp)

    def update(self, which):
        if which == ACTIONS.WAIT:
            self.hp += 1
            if (self.hp >= self.maxHP): self.hp = self.maxHP
        return ""


# thread out GUI controller to avoid locking up main loop
# Queue object passed in for messaging
def guiThread(q):
    guicontroller = GUIController(q)

# Main game class
class RLGame():
    def __init__(self, ft, gamepad, pixels):
        self.ft = ft
        self.gamepad = gamepad
        self.pixels = pixels

        self.miniMapActive = False

        if self.gamepad is None:
            self.queue = Queue()
            self.gui_thread = Thread(target=guiThread, args=(self.queue,))
            self.gui_thread.daemon = True
            self.gui_thread.start()


        self.debounce_delay = 100/1000

        self.mapGen = MapGenerator(width=MAP_COLS, height=MAP_ROWS)

        # get map info
        self.game_map = []
        for i in range(5):
          bsp = self.mapGen.generateBSP()
          self.game_map.append(bsp['map'])

          if i == 0:
            p_c = bsp['player_start']['c']
            p_r = bsp['player_start']['r']
            self.exit_c = bsp['exit']['c']
            self.exit_r = bsp['exit']['r']

        self.wonR = -1 # drawing animation

        # player creation/location
        self.player = Player(p_c,p_r)

        self.entities = []
        for _ in range(ENEMIES_PER_CHUNK):
            e_c, e_r = self.getValidPos()
            self.entities.append(MoveableEntity(orc, e_c, e_r, dlvl=0, hp=3, atk=1))

        self.KEYCODES = {
          'K_L': {'key': 294,'callback': self.player.update, 'param': (ACTIONS.WAIT)},
          'K_R': {'key': 295,'callback': self.debug, 'param': 'win'},
          'K_A': {'key': 288,'callback': None},
          'K_B': {'key': 289,'callback': self.debug, 'param': 'inc'},
          'K_X': {'key': 291,'callback': None},
          'K_Y': {'key': 292,'callback': None},
          'START':{'key': 299, 'callback': None},
          'SELECT':{'key': 298, 'callback': self.showMiniMap},
        }




    def showMiniMap(self):
        self.miniMapActive = not self.miniMapActive

    def debug(self, param) -> str:
        if param == 'win':
            self.wonR = 0
            return "done"
        elif param == 'inc':
            self.player.dlvl += 1

    def debounce(self) -> List[int]:
        keys = self.gamepad.active_keys()
        sleep(self.debounce_delay)
        return list(set(keys).intersection(self.gamepad.active_keys()))

    # get a random valid position
    def getValidPos(self) -> Tuple[int,int]:
        r = random.randint(1,MAP_ROWS-1)
        c = random.randint(1,MAP_COLS-1)
        while not self.isValid(c, r):
            r = random.randint(1,MAP_ROWS-1)
            c = random.randint(1,MAP_COLS-1)
        return c,r

    # check if a cell is valid and walkable
    def isValid(self, c, r) -> bool:
        if c < 0 or c > len(self.game_map[self.player.dlvl][0])-1 or r < 0 or r > len(self.game_map[self.player.dlvl])-1:
            return False
        if self.game_map[self.player.dlvl][r][c] not in WALKABLE:
            return False
        return True

    # screen handlers
    def clearScreen(self, col=(0,0,0)):
        for y in range(self.ft.height):
            for x in range(self.ft.width):
                self.ft.set(x,y,col)

    # set pixels per cell
    def drawCell(self, c, r, char, hp_perc=None):
        # actual position
        # startx = c * CELLSIZE
        # starty = r * CELLSIZE
        _c = c * CELLSIZE
        _r = r * CELLSIZE

        numgreen = 0
        if hp_perc is not None:
            numgreen = int(CELLSIZE * hp_perc)
            if numgreen == 0: # make the last pip visible if we're at like 1hp
                numgreen = 1

        out_pixels = self.pixels[_r:_r+SPRITES[char]['sprite'].shape[0], _c:_c+SPRITES[char]['sprite'].shape[1]]
        out_pixels[SPRITES[char]['sprite']] = SPRITES[char]['color']
        if hp_perc is not None and char is not dead: # render HP bar
            _y = _r + CELLSIZE-1
            for _x in range(TEXTWIDTH):#CELLSIZE):
              if _x < numgreen:
                self.pixels[_y,TEXTOFFSET+_c+_x] = COLORS['currHealth']
                #self.pixels[_y,TEXTOFFSET+_c+_x] = COLORS['currHealth']
              else:
                self.pixels[_y,TEXTOFFSET+_c+_x] = COLORS['maxHealth']
                #self.pixels[_y,TEXTOFFSET+_c+_x] = COLORS['maxHealth']



        # for y in range(CELLSIZE):
        #     for x in range(CELLSIZE):
        #         if hp_perc is not None and char is not dead and y == CELLSIZE-1:
        #             if x < numgreen:
        #                 self.pixels[starty+y, startx+x] = COLORS['currHealth']
        #                 #self.ft.set(startx+x, starty+y, COLORS['currHealth'])
        #             else:
        #                 self.pixels[starty+y, startx+x] = COLORS['maxHealth']
        #                 #self.ft.set(startx+x, starty+y, COLORS['maxHealth'])

        #         elif SPRITES[char][y][x] == "0":
        #             self.pixels[starty+y, startx+x] = COLORS[char]
        #             #self.ft.set(startx+x, starty+y, COLORS[char])
        #         else:
        #             self.pixels[starty+y, startx+x] = COLORS[clear]
        #             #self.ft.set(startx+x, starty+y, COLORS[clear])



    def drawMap(self) -> None:
        self.pixels[:,:] = (0,0,0)
        # sliding window around player
        if not self.miniMapActive:
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
                    self.drawCell(_c, _r, self.game_map[self.player.dlvl][r][c])
    
                    for e in self.entities:
                        if e.r >= startr and e.r < endr and e.c >= startc and e.c < endc:
                            if r == e.r and c == e.c:
                                self.drawCell(_c, _r, e.sprite, e.hp / e.maxHP)
    
                    if r == self.player.r and c == self.player.c:
                      self.drawCell(_c, _r, self.player.sprite, self.player.hp / self.player.maxHP)
    
                    _c += 1
                _c = 0
                _r += 1

        else: # draw minimap
            for r in range(len(self.game_map[self.player.dlvl])):
                for c in range(len(self.game_map[self.player.dlvl][0])):
                    self.pixels[r,c] = COLORS[self.game_map[self.player.dlvl][r][c]]
            self.pixels[self.player.r, self.player.c] = COLORS[player]

        # testing drawing - remove later
        #testText = self.font.draw("Hello there!")
        #testTextArr = np.array(testText.todata(2))

        #for _r in range(len(testTextArr)):
        #    for _c in range(len(testTextArr[0])):
        #        if testTextArr[_r,_c] == 1:
        #            self.pixels[_r,_c] = (0,255,0)




        

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


    def GUIkeys(self):
        data = self.queue.get()
        button_keys = ["K_A", "K_B", "K_X", "K_Y", "K_L", "K_R", "START", "SELECT"]
        arrow_keys = ["Y", "K", "U", "H", ".", "L", "B", "J", "N"]

        if data in button_keys:
            return "button", [self.KEYCODES[data]['key']]
        elif data in arrow_keys:
            return "arrow", [data]
        elif data == "L+R":
            return "button", [self.KEYCODES["K_L"]['key'], self.KEYCODES["K_R"]['key']]
        else:
            return None, None

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

            #keys = self.gamepad.active_keys()
            if self.gamepad is not None:
                keys = self.debounce()
                gui_action = None
            else:
                gui_action, keys = self.GUIkeys()

            # keyboard events
            if len(keys) == 1:
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
            if self.KEYCODES["K_L"]["key"] in keys and self.KEYCODES["K_R"]["key"] in keys:
                done = True

            # dpad events
            next_r = self.player.r
            next_c = self.player.c
            if self.gamepad is not None:
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
            else:
                if gui_action == "arrow":
                    #arrow_keys = ["Y", "K", "U", "H", ".", "L", "B", "J", "N"]
                    k = keys[0]
                    dirty = True
                    if k == "Y":
                        next_r -= 1
                        next_c -= 1
                    elif k == "K":
                        next_r -= 1
                    elif k == "U":
                        next_r -= 1
                        next_c += 1
                    elif k == "H":
                        next_c -= 1
                    elif k == ".": 
                        self.player.update(ACTIONS.WAIT)
                    elif k == "L":
                        next_c += 1
                    elif k == "B":
                        next_r += 1
                        next_c -= 1
                    elif k == "J":
                        next_r += 1
                    elif k == "N":
                        next_r += 1
                        next_c += 1
                    



                #if (random.random() > 0.8):
                #    d = random.choice(directions)
                #    next_r += d[1]
                #    next_c += d[0]
                #    dirty = True

            if dirty and self.isValid(next_c, next_r):
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

                # did we ascend?
                if self.player.c == self.exit_c and self.player.r == self.exit_r:
                    print("Winner winner.")
                    done = True
                    self.wonR = 0
                    break



            if dirty:
                #print(self.player.c, self.player.r, self.exit_c, self.exit_r)
                if not self.miniMapActive:
                    level_entities = [e for e in self.entities if e.dlvl == self.player.dlvl]
                    for e in level_entities: #self.entities:
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
    
                                elif action['c'] is not None and action['r'] is not None:
                                    if self.isValid(action['c'], action['r']): # otherwise move
                                        e.c = action['c']
                                        e.r = action['r']
    
            
                self.drawMap()
                self.ft.send()
                dirty = False


            # need to flag out our win condition better
            if done:
                if self.wonR >= 0:
                    while self.wonR < self.ft.height:
                        self.pixels[self.wonR,:] = (0,255,0)
                        self.ft.send()
                        sleep(0.05)
                        self.wonR += 1

                if self.gamepad is None:
                    self.gui_thread.join()
    
                break

        sleep(0.10)

        self.ft.send()
        print("Done")
        return
