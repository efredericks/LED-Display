from evdev import InputDevice, categorize, ecodes
from copy import deepcopy
import flaschen
import random
import math
from time import sleep

from select import select

# MAP DEFINES
EMPTY = 0
CROSS = 1
SQUARES = 2

gamepad = InputDevice('/dev/input/event0')

UDP_IP = 'localhost'
UDP_PORT = 1337
ft = flaschen.Flaschen(UDP_IP, UDP_PORT, 64, 64)

fruit = 'f'
wall = 'w'
cell = '.'
end = '!'
unvisited = ' '
player = '@'
WALKABLE = [cell, end]

# user defined restart
triggeredEndGame = False

# AI playing until user presses a button
attractMode = True
maxLength = 0

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
  fruit: (255, 255, 0),
}

# https://medium.com/technology-invention-and-more/how-to-build-a-simple-neural-network-in-9-lines-of-python-code-cc8f23647ca1
# ANN

def generate_maze(num = None):
    maze = []
    # outer walls
    for y in xrange(0,ft.height):
        line = []
        for x in xrange(0,ft.width):
            if x == 0 or y == 0 or y == ft.height-1 or x == ft.height-1:
                line.append(wall)
            else:
                line.append(cell)
        maze.append(line)

    if num is None:
        num = random.randint(0,2)
    assert num >= 0 and num <= 2, "Valid maps are 0, 1, 2"


    # cross
    if num == 1:
        y = 32
        for x in xrange(10, ft.width-10):
            maze[y][x] = wall
            maze[y-1][x] = wall
            maze[y+1][x] = wall

            # since we're square...lets be lazy
            maze[x][y-1] = wall
            maze[x][y] = wall
            maze[x][y+1] = wall

    # squares
    elif num == 2:
        offset = 4
        for y in xrange(0,4):
            for x in xrange(0,4):
                maze[y+offset][x+offset] = wall
                maze[ft.height-1-offset-y][x+offset] = wall
                maze[ft.height-1-offset-y][ft.width-1-offset-x] = wall
                maze[y+offset][ft.width-1-offset-x] = wall

        for y in range(32-4, 32+4):
            for x in range(32-4, 32+4):
                maze[y][x] = wall

    return maze


def get_neighbors(maze, x, y):
    neighbor_list = []
    for d in directions:
        next_x = x + d[0]
        next_y = y + d[0]

        # ignore border
        if next_x > 1 and next_x < len(maze[0])-2 and next_y > 1 and next_y < len(maze)-2:
            neighbor_list.append([next_x, next_y])
    return neighbor_list


def is_valid(maze, x, y):
    if x >= 1 and x <= len(maze[0]) - 2 and y >= 1 and y <= len(maze) - 2:
        return True
    return False


def get_pos(maze):
    done = False
    while not done:
        p_x = random.randint(1,len(maze[0])-1)#int(random.random()*len(maze[0]))
        p_y = random.randint(1,len(maze)-1)#int(random.random()*len(maze))

        if (maze[p_y][p_x] == cell):
            done = True
            break

    return (p_x, p_y)


# key handlers
def Lkey():
    print("L bumper")
    return ""
def Rkey():
    print("R bumper")
    return ""
def test():
    print("whoa")
    return ""
def newMap():
    global triggeredEndGame
    print("New map")
    triggeredEndGame = True
    return ""
def startBtn():
    global attractMode
    attractMode = not attractMode
    print("Attract mode: {0}".format(attractMode))
    return ""
def endGame():
    return "done"

# screen handlers
def clearScreen(ft, col=(0,0,0)):
    for y in xrange(0,ft.height):
        for x in xrange(0,ft.width):
            ft.set(x,y,col)

def drawMap(ft, maze):
    for y in xrange(0, ft.height):
        for x in xrange(0, ft.width):
            ft.set(x, y, maze_colors[maze[y][x]])

KEYCODES = {
  'L': {'key': 294, 'callback': Lkey},
  'R': {'key': 295,'callback': Rkey},
  'A': {'key': 288,'callback': test},
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


maze = generate_maze()

# prim
#cellx = random.randint(1,ft.width-2)
#celly = random.randint(1,ft.height-2)
#maze[celly][cellx] = cell

#neighbors = get_neighbors(maze, cellx, celly)
#print(neighbors)





#p = get_pos(maze)
#player_col = p[0]#random.randint(0,ft.width-1)
#player_row = p[1]#random.randint(0,ft.height-1)
#maze[player_row][player_col] = player

done = False
#while not done:
    # draw player
    #ft.set(0,0,(255,0,255))
    #ft.set(player_col, player_row, COLORS["player"])
    #ft.send()

# handle events

# https://github.com/CodingTrain/website-archive/blob/main/CodingChallenges/CC_115_Snake_Game_Redux/P5/snake.js
class Snake():
    def __init__(self, ft):
        pos = get_pos(maze)
        self.body = []
        self.body.append([pos[0], pos[1]])
        self.xdir = 0
        self.ydir = 0
        self.len = 0
        self.ft = ft
        self.watchdog = []

    def getLength(self):
        return len(self.body)

    def reset(self):
        pos = get_pos(maze)
        self.body = []
        self.body.append([pos[0], pos[1]])
        self.xdir = 0
        self.ydir = 0
        self.len = 0

    def get_head(self):
        return deepcopy(self.body[len(self.body)-1])

    def expertControl(self, maze, fruits):
        # calculate manhattan distance to each fruit
        # this is currently ignoring any obstacles...
        head = self.get_head()
        min_dist = 9999
        target_idx = 0
        for i in xrange(len(fruits)):
            f = fruits[i]
            dist = abs(head[0] - f[0]) + abs(head[1] - f[1])
            if dist < min_dist:
                min_dist = dist
                target_idx = i
            #dists.append(dist)

        # control - prefer x?
        tgt_x = fruits[target_idx][0]
        tgt_y = fruits[target_idx][1]
        if head[0] < tgt_x:
            self.xdir = 1
            self.ydir = 0
        elif head[0] > tgt_x:
            self.xdir = -1
            self.ydir = 0
        elif head[1] < tgt_y:
            self.xdir = 0
            self.ydir = 1
        else:
            self.xdir = 0
            self.ydir = -1

        # collision check
        next_x = head[0] + self.xdir
        next_y = head[1] + self.ydir
        if self.endgame(next_x, next_y):
            random.shuffle(directions)
            for d in directions:
                next_x = head[0] + d[0]
                next_y = head[1] + d[1]
                if not self.endgame(next_x, next_y):
                    self.xdir = d[0]
                    self.ydir = d[1]

        # watchdog to see if "stuck"
        # average distances < 4
        if len(self.watchdog) < 20:
            self.watchdog.append(head)
        else:
            dists = 0
            for w in self.watchdog:
                dists += float(abs(w[0] - head[0]) + abs(w[1] - head[1]))
            dists /= float(len(self.watchdog))
            print(dists)
            if dists < 2.0:
                print("stuck!")
                random.shuffle(directions)
                direction = directions[0]
                self.xdir = direction[0]
                self.ydir = direction[1]
            self.watchdog = []






        

    def setDir(self, x, y):
        self.xdir = x
        self.ydir = y

    def update(self):
        head = self.get_head()#deepcopy(self.body[len(self.body)-1])
        self.body.pop(0)
        head[0] += self.xdir
        head[1] += self.ydir
        self.body.append(head)

    def grow(self):
        head = self.get_head()#deepcopy(self.body[len(self.body)-1])
        self.len += 1
        self.body.append(head)

    def endgame(self, _x = -1, _y = -1):
        head = self.get_head()
        retval = False

        if _x == -1 and _y == -1:
            x = head[0]#self.body[len(self.body)-1][0]
            y = head[1]#self.body[len(self.body)-1][1]
        else:
            x = _x
            y = _y

        # wall collision
        if x > self.ft.width-1 or x < 0 or y > self.ft.height-1 or y < 0:
            retval = True
            #return True

        # self collision
        for i in xrange(0, len(self.body)-1):
            if self.body[i][0] == x and self.body[i][1] == y:
                retval = True
                #return True

        if maze[y][x] == wall:
            retval = True

        return retval

    def eat(self, _fruits):
        head = self.get_head()
        x = head[0]#self.body[len(self.body)-1][0]
        y = head[1]#self.body[len(self.body)-1][1]
        #x = self.body[len(self.body)-1][0]
        #y = self.body[len(self.body)-1][1]

        for i in xrange(len(_fruits)):
            if x == _fruits[i][0] and y == _fruits[i][1]:
                #print(_fruits)
                self.grow()
                return i
        return -1

    def show(self):
        for i in xrange(0,len(self.body)):
            ft.set(self.body[i][0], self.body[i][1], maze_colors[player])

snake = Snake(ft)
fruits = []

## initially draw
drawMap(ft, maze)
#ft.set(player_col, player_row, maze_colors[player])
#ft.set(win_col, win_row, COLORS["win"])
ft.send()
snake.show()

#fruitActive = True
fruits.append(get_pos(maze))#[random.randint(1,ft.width-2), random.randint(1, ft.height-2)]

while not done:
    keys = gamepad.active_keys()
    drawMap(ft, maze)

    # keyboard events
    for k,v in KEYCODES.iteritems():
        if v["key"] in keys:
            r = v["callback"]()
            if r == "done":
                done = True

    # multiple key handler (irrespective of mode)
    if KEYCODES["L"]["key"] in keys and KEYCODES["R"]["key"] in keys:
        done = endGame()

    # player control
    if not attractMode:
        if KEYCODES["A"]["key"] in keys:
            snake.grow()

        # dpad events
        if gamepad.absinfo(ecodes.ABS_X).value < 128:
            snake.setDir(-1,0)
        if gamepad.absinfo(ecodes.ABS_X).value > 128:
            snake.setDir(1,0)
        if gamepad.absinfo(ecodes.ABS_Y).value < 128:
            snake.setDir(0,-1)
        if gamepad.absinfo(ecodes.ABS_Y).value > 128:
            snake.setDir(0,1)
    # AI
    else:
        snake.expertControl(maze, fruits)

    # eat fruit
    fruit_idx = snake.eat(fruits)
    snake.update()
    snake.show()

    # remove fruit from list if it was eaten
    if fruit_idx > -1:
        del fruits[fruit_idx]

    # ensure we have a fruit!
    if len(fruits) > 0:
        for f in fruits:
            ft.set(f[0], f[1], maze_colors[fruit])
    else: # ensure we always have 1
        fruits.append(get_pos(maze))

    # add a random fruit
    if random.random() > 0.8 and len(fruits) < 5:
        fruits.append(get_pos(maze))

    # draw to matrix
    ft.send()

    # reset game
    if snake.endgame() or triggeredEndGame == True:
        if maxLength < snake.getLength():
            maxLength = snake.getLength()
            print("New best: {0}".format(maxLength))
        else:
            print("Prior best: {0}".format(maxLength))


        triggeredEndGame = False
        clearScreen(ft, (180,0,0))
        ft.send()
        sleep(2)
        snake.reset()
        maze = generate_maze()

    if done:
        break

    sleep(0.10)

clearScreen(ft)
ft.send()
print("Done")

