from evdev import InputDevice, categorize, ecodes
from copy import deepcopy
import flaschen
import random
from datetime import datetime
import math
from time import sleep
from select import select
import noise

# game imports
import sand, snake, tetris, roguelike, runner

gamepad = InputDevice('/dev/input/event0')

# setup flaschen-taschen connection (i.e., the reason Py2.7 is used)
UDP_IP = 'localhost'
UDP_PORT = 1337
ft = flaschen.Flaschen(UDP_IP, UDP_PORT, 64, 64)

# noise
octaves = 8
frequency = 16.0 * octaves

# drawing colors
COLORS = {
  ' ': (0,0,0),
  'R': (255,0,0),
  'G': (0,255,0),
  'B': (0,0,255),
  'P': (255,0,255),
}

# menu options
SNAKE = 0
SAND = 1
RUNNER = 2
TETRIS = 3
RL = 4
QUIT = 5
indicator_pos = [[2,2], [2,9], [2,16], [2,23], [2,30], [2,37]]
indicator = 2#4
  
# key handlers
def startBtn():
    print("Starting {0}".format(indicator))

    if indicator == SAND:
        sandGame = sand.FallingSand(ft, gamepad)
        sandGame.execute()
    elif indicator == SNAKE:
        snakeGame = snake.SnakeGame(ft, gamepad)
        snakeGame.execute()
    elif indicator == RUNNER:
        runnerGame = runner.RunnerGame(ft, gamepad)
        runnerGame.execute()
    elif indicator == TETRIS:
        tetrisGame = tetris.TetrisGame(ft, gamepad)
        tetrisGame.execute()
    elif indicator == RL:
        rlGame = roguelike.RLGame(ft, gamepad)
        rlGame.execute()


    if indicator == len(indicator_pos)-1:
        return "done"
    else:
        return ""
def endGame():
    return "done"

KEYCODES = {
  #'L': {'key': 294, 'callback': startBtn},
  #'R': {'key': 295,'callback': startBtn},
  'A': {'key': 288,'callback': startBtn},
  #'B': {'key': 289,'callback': startBtn},
  #'X': {'key': 291,'callback': startBtn},
  #'Y': {'key': 292,'callback': startBtn},
  'START':{'key': 299, 'callback': startBtn},
  'SELECT':{'key': 298, 'callback': endGame},
}

# option 1 - snake
# option 2 - sand
# option 3 - done
# start empty
screen = [\
  "                                                                ",\
  "                                                                ",\
  "     PPPP P   P   P   P  P PPPP                                 ",\
  "    P     PP  P  P P  P P  P                                    ",\
  "     PPP  P P P  PPP  PP   PPP                                  ",\
  "        P P  PP P   P P P  P                                    ",\
  "    PPPP  P   P P   P P  P PPPP                                 ",\
  "                                                                ",\
  "                                                                ",\
  "     PPPP   P   P   P PPP                                       ",\
  "    P      P P  PP  P P  P                                      ",\
  "     PPP   PPP  P P P P   P                                     ",\
  "        P P   P P  PP P  P                                      ",\
  "    PPPP  P   P P   P PPP                                       ",\
  "                                                                ",\
  "                                                                ",\
  "    PPPP P   P P   P P   P PPPP PPPP                            ",\
  "    P  P P   P PP  P PP  P P    P  P                            ",\
  "    PPP  P   P P P P P P P PPP  PPP                             ",\
  "    P P  P   P P  PP P  PP P    P P                             ",\
  "    P  P  PPP  P   P P   P PPPP P  P                            ",\
  "                                                                ",\
  "                                                                ",\
  "    PPPPP PPPP PPPPP PPPP P  PPPP                               ",\
  "      P   P      P   P  P P P                                   ",\
  "      P   PPP    P   PPP  P  PPP                                ",\
  "      P   P      P   P P  P     P                               ",\
  "      P   PPPP   P   P  P P PPPP                                ",\
  "                                                                ",\
  "                                                                ",\
  "    PPPP  PP   PPP  P   P PPPP P    P P  P PPPP                 ",\
  "    P  P P  P P     P   P P    P    P P P  P                    ",\
  "    PPP  P  P P  PP P   P PPP  P    P PP   PPP                  ",\
  "    P P  P  P P   P P   P P    P    P P P  P                    ",\
  "    P  P  PP   PPP   PPP  PPPP PPPP P P  P PPPP                 ",\
  "                                                                ",\
  "                                                                ",\
  "    PPPPP P   P P PPPPP                                         ",\
  "    P   P P   P P   P                                           ",\
  "    P P P P   P P   P                                           ",\
  "    P  PP P   P P   P                                           ",\
  "    PPPPP  PPP  P   P                                           ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
  "                                                                ",\
]

# screen handlers
def drawScreen(ft, indicator, z, clear=False):
    if not clear:
        for y in range(0,ft.height):
            for x in range(0,ft.width):
                if screen[y][x] == ' ':
                    n = noise.snoise3(x / frequency, y/frequency, z/frequency, octaves=octaves,persistence=0.25)
                    col = (0,0,0)
                    if n < 0.25:
                        col = (20,0,0)
                    elif n < 0.5:
                        col = (0,20,0)
                    elif n < 0.75:
                        col = (0,0,20)
                    ft.set(x,y,col)
                else:
                    ft.set(x,y,COLORS[screen[y][x]])

        for y in range(indicator_pos[indicator][1], indicator_pos[indicator][1]+5):
            ft.set(indicator_pos[indicator][0], y, (0,255,0))
    else:
        for y in range(0,ft.height):
            for x in range(0,ft.width):
                ft.set(x,y,COLORS[' '])

if __name__ == "__main__":
    random.seed(datetime.now())
    z = 0
    drawScreen(ft, indicator, z)
    ft.send()


    done = False
    while not done:
        drawScreen(ft, indicator, z)
        keys = gamepad.active_keys()

        # keypad events
        for k,v in KEYCODES.items():
            if v["key"] in keys:
                r = v["callback"]()
                if r == "done":
                    done = True

        # dpad events
        next_i = indicator
        if gamepad.absinfo(ecodes.ABS_Y).value < 128: #up
            next_i -= 1
        if gamepad.absinfo(ecodes.ABS_Y).value > 128: #down
            next_i += 1
        if next_i < 0: next_i = len(indicator_pos)-1
        if next_i > len(indicator_pos)-1: next_i = 0

        indicator = next_i
        z += 1
        if z > 5000:
            z = 0



        ft.send()
        # reset game
        if done:
            break

        sleep(0.10)

    drawScreen(ft, indicator, z, True)
    ft.send()
    print("Done")

