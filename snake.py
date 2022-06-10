from evdev import InputDevice, categorize, ecodes
import flaschen
import random
import math
from time import sleep

from select import select

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

# remove diag
directions = [
#  [-1,-1],
  [0,-1],
#  [1,-1],
  [1,0],
#  [1,1],
  [0,1],
#  [-1,1],
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



def get_pos(maze):
  done = False
  while not done:
    p_x = int(random.random()*len(maze[0]))
    p_y = int(random.random()*len(maze))

    if (maze[p_y][p_x] == cell):
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
  'START':{'key': 299, 'callback': endGame},
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
from copy import deepcopy
class Snake():
    def __init__(self, ft):
        pos = get_pos(maze)
        self.body = []
        self.body.append([pos[0], pos[1]])
        self.xdir = 0
        self.ydir = 0
        self.len = 0
        self.ft = ft

    def reset(self):
        pos = get_pos(maze)
        self.body = []
        self.body.append([pos[0], pos[1]])
        self.xdir = 0
        self.ydir = 0
        self.len = 0
        

    def setDir(self, x, y):
        self.xdir = x
        self.ydir = y

    def update(self):
        head = deepcopy(self.body[len(self.body)-1])
        self.body.pop(0)
        head[0] += self.xdir
        head[1] += self.ydir
        self.body.append(head)

    def grow(self):
        head = deepcopy(self.body[len(self.body)-1])
        self.len += 1
        self.body.append(head)

    def endgame(self):
        x = self.body[len(self.body)-1][0]
        y = self.body[len(self.body)-1][1]

        # wall collision
        if x > self.ft.width-1 or x < 0 or y > self.ft.height-1 or y < 0:
            return True

        # self collision
        for i in xrange(0, len(self.body)-1):
            if self.body[i][0] == x and self.body[i][1] == y:
                return True

        if maze[y][x] == wall:
            return True

        return False

    def eat(self, _fruits):
        x = self.body[len(self.body)-1][0]
        y = self.body[len(self.body)-1][1]

        for i in xrange(len(_fruits)):
            if x == _fruits[i][0] and y == _fruits[i][1]:
                print(_fruits)
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
        if KEYCODES["A"]["key"] in keys:
            snake.grow()
        if v["key"] in keys:
            r = v["callback"]()
            if r == "done":
                done = True

    # dpad events
    if gamepad.absinfo(ecodes.ABS_X).value < 128:
        snake.setDir(-1,0)
    if gamepad.absinfo(ecodes.ABS_X).value > 128:
        snake.setDir(1,0)
    if gamepad.absinfo(ecodes.ABS_Y).value < 128:
        snake.setDir(0,-1)
    if gamepad.absinfo(ecodes.ABS_Y).value > 128:
        snake.setDir(0,1)
#        elif event.type == ecodes.EV_ABS:
#            if event.code == ecodes.ABS_X:
#                if event.value == 0:
#    #            print('left')
#                    snake.setDir(-1,0)
#                elif event.value == 255:
#    #            print('right')
#                    snake.setDir(1,0)
#            elif event.code == ecodes.ABS_Y:
#                if event.value == 0:
#    #            print('up')
#                    snake.setDir(0,-1)
#                elif event.value == 255:
#    #            print('down')
#                    snake.setDir(0,1)


    fruit_idx = snake.eat(fruits)
    snake.update()
    snake.show()

    if fruit_idx > -1:
        del fruits[fruit_idx]

    #if (ret_eat): fruitActive = False

    if len(fruits) > 0:#fruitActive:
        for f in fruits:
            ft.set(f[0], f[1], maze_colors[fruit])
    else: # ensure we always have 1
        fruits.append(get_pos(maze))

    # add a random fruit
    if random.random() > 0.8 and len(fruits) < 5:
        fruits.append(get_pos(maze))

    ft.send()


    if snake.endgame() or triggeredEndGame == True:
        triggeredEndGame = False
        clearScreen(ft, (180,0,0))
        ft.send()
        sleep(2)
        snake.reset()
        maze = generate_maze()


    


    """

    #print(categorize(event))
    # keyboard events
    if event.type == ecodes.EV_KEY:
        if event.value == KEYDOWN:
            for k,v in KEYCODES.iteritems():
                if event.code == v["key"]:
                    r = v["callback"]()
                    if r == "done":
                        done = True


    # dpad events
    elif event.type == ecodes.EV_ABS:
        next_r = player_row
        next_c = player_col
        if event.code == ecodes.ABS_X:
            if event.value == 0:
    #            print('left')
                next_c -= 1
            elif event.value == 255:
    #            print('right')
                next_c += 1
        elif event.code == ecodes.ABS_Y:
            if event.value == 0:
    #            print('up')
                next_r -= 1
            elif event.value == 255:
    #            print('down')
                next_r += 1

        #print(player_col, player_row)
        if next_r >= 0 and next_r <= 63 and next_c >= 0 and next_c <= 63:
            if maze[next_r][next_c] in WALKABLE:
                player_col = next_c
                player_row = next_r
        #if player_col == win_col and player_row == win_row:
        if maze[player_row][player_col] == end:
            clearScreen(ft, (0,180,0))
            ft.send()
            sleep(2)

            maze = random_walk(ft.width, ft.height)
            p = get_pos(maze)
            player_col = p[0]#random.randint(0,ft.width-1)
            player_row = p[1]#random.randint(0,ft.height-1)

            #player_col = random.randint(0,ft.width-1)
            #player_row = random.randint(0,ft.height-1)
            #win_col = random.randint(0,ft.width-1)
            #win_row = random.randint(0,ft.height-1)
    """
    if done:
        break

    sleep(0.10)

clearScreen(ft)
ft.send()
print("Done")

