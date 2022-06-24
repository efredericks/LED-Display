from evdev import InputDevice, categorize, ecodes
from copy import deepcopy
import flaschen
import random
import math
from time import sleep

from select import select

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

currSand = 0

gamepad = InputDevice('/dev/input/event0')

UDP_IP = 'localhost'
UDP_PORT = 1337
ft = flaschen.Flaschen(UDP_IP, UDP_PORT, 64, 64)





# key handlers
drain = False
def Lkey():
    global drain
    drain = not drain
    print("L bumper")
    return ""
def Rkey():
    print("R bumper")
    return ""
def test():
    print("whoa")
    return ""
def newMap():
    #global triggeredEndGame
    global maze

    for y in xrange(len(maze)):
        for x in xrange(len(maze[0])):
            maze[y][x] = [EMPTY,maze_colors[EMPTY]]
    #print("New map")
    #triggeredEndGame = True
    return ""
def startBtn():
    #global attractMode
    #attractMode = not attractMode
    #print("Attract mode: {0}".format(attractMode))
    return ""
def endGame():
    return "done"

def Akey():
    global maze, currCol
    col = random.randint(0,220)

    if currSand == 0:
        sandcol = maze_colors[SAND]
    elif currSand == 1:
        sandcol = maze_colors[SAND2]
    elif currSand == 2:
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
    maze[0][currCol] = [SAND, scol]
    return ""

# screen handlers
def clearScreen(ft, col=(0,0,0)):
    for y in xrange(0,ft.height):
        for x in xrange(0,ft.width):
            ft.set(x,y,col)

def drawMap(ft, maze):
    for y in xrange(0, ft.height):
        for x in xrange(0, ft.width):
            ft.set(x, y, maze[y][x][1])#maze_colors[maze[y][x]])

# get cell value
def getCell(maze, x, y):
    if y < 0 or y > len(maze)-1 or x < 0 or x > len(maze[0])-1:
        return None
    return maze[y][x]

KEYCODES = {
  'L': {'key': 294, 'callback': Lkey},
  'R': {'key': 295,'callback': Rkey},
  'A': {'key': 288,'callback': Akey},
  'B': {'key': 289,'callback': test},
  'X': {'key': 291,'callback': test},
  'Y': {'key': 292,'callback': test},
  'START':{'key': 299, 'callback': startBtn},#endGame},
  'SELECT':{'key': 298, 'callback': newMap},
}

# are these constants somewhere?
KEYDOWN = 1
KEYUP = 0
KEYHOLD = 2

currCol = 32


done = False

# initialize maze
maze = []
for y in xrange(0,ft.height):
    line = []
    for x in xrange(0,ft.width):
        line.append([EMPTY, maze_colors[EMPTY]])
    maze.append(line)

#maze[5][2] = WALL
#maze[5][3] = WALL
#maze[5][4] = WALL
#maze[5][5] = WALL
#maze[5][6] = WALL
#maze[5][7] = WALL
#maze[5][8] = WALL


## initially draw

emitterColor = SAND

drawMap(ft, maze)
ft.set(currCol, 0, maze_colors[emitterColor])
#ft.set(currCol, 0, maze_colors[EMITTER])
ft.send()

while not done:
    keys = gamepad.active_keys()
    drawMap(ft, maze)

    # draw emitter
    #ft.set(currCol, 0, maze_colors[EMITTER])
    if currSand == 0: emitterColor = SAND
    elif currSand == 1: emitterColor = SAND2
    elif currSand == 2: emitterColor = SAND3
    else: emitterColor = SAND4

    ft.set(currCol, 0, maze_colors[emitterColor])


    # keyboard events
    for k,v in KEYCODES.iteritems():
        if v["key"] in keys:
            r = v["callback"]()
            if r == "done":
                done = True

    # handle single key presses?
#    event = gamepad.read_one()
##    if event.type == ecodes.EV_KEY:
#    if event is not None:
#        print(categorize(event))
##        print(categorize(event))


    # multiple key handler (irrespective of mode)
    #if KEYCODES["L"]["key"] in keys and KEYCODES["R"]["key"] in keys:
    #    done = endGame()

    # dpad events
    if gamepad.absinfo(ecodes.ABS_X).value < 128:
        currCol -= 1
    if gamepad.absinfo(ecodes.ABS_X).value > 128:
        currCol += 1
    if gamepad.absinfo(ecodes.ABS_Y).value < 128:
        currSand += 1
        if currSand > 3:
            currSand = 0
    if gamepad.absinfo(ecodes.ABS_Y).value > 128:
        pass

    if currCol < 0: currCol = 0
    if currCol > ft.width-1: currCol = ft.width-1

    # sand updates
    for y in xrange(ft.height-1, -1, -1):
        for x in xrange(0, ft.width):
            direction = random.choice([-1, 1])
            if maze[y][x][0] == SAND:
                if getCell(maze, x, y+1) is not None and getCell(maze, x, y+1)[0] == EMPTY:
                    col = maze[y][x][1]
                    maze[y][x] = [EMPTY,maze_colors[EMPTY]]
                    maze[y+1][x] = [SAND,col]#maze_colors[SAND]]
                elif getCell(maze, x+direction, y+1) is not None and getCell(maze, x+direction, y+1)[0] == EMPTY:
                    col = maze[y][x][1]
                    maze[y][x] = [EMPTY,maze_colors[EMPTY]]
                    maze[y+1][x+direction] = [SAND,col]#maze_colors[SAND]]




    #maze[0][random.randint(0,ft.width-1)] = SAND

    #maze[ft.height-1][5] = EMPTY
    #maze[ft.height-1][6] = EMPTY
    #maze[ft.height-1][7] = EMPTY
    #maze[ft.height-1][8] = EMPTY

    if drain:
        for i in xrange(0,ft.width):
            maze[ft.height-1][i] = [EMPTY,maze_colors[EMPTY]]


    # draw to matrix
    ft.send()

    # reset game
    if done:
        break

    #sleep(0.10)

clearScreen(ft)
ft.send()
print("Done")

