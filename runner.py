from evdev import InputDevice, categorize, ecodes
from copy import deepcopy
import flaschen
import random
import math
from time import sleep
from select import select

# https://medium.com/technology-invention-and-more/how-to-build-a-simple-neural-network-in-9-lines-of-python-code-cc8f23647ca1
# ANN

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

# https://github.com/CodingTrain/website-archive/blob/main/CodingChallenges/CC_115_Snake_Game_Redux/P5/snake.js
class Snake():
    def __init__(self, ft, pos, maze):
        self.pos = pos
        self.maze = maze
        self.body = []
        self.body.append([pos[0], pos[1]])
        self.xdir = 0
        self.ydir = 0
        self.len = 0
        self.ft = ft
        self.watchdog = []

    def getLength(self):
        return len(self.body)

    def reset(self, pos):
        pos = pos
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
        if self.endgame(self.maze, next_x, next_y):
            random.shuffle(directions)
            for d in directions:
                next_x = head[0] + d[0]
                next_y = head[1] + d[1]
                if not self.endgame(self.maze, next_x, next_y):
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

    def endgame(self, maze, _x = -1, _y = -1):
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

    def show(self, attractMode):
        for i in xrange(0,len(self.body)):
            if (attractMode):
                self.ft.set(self.body[i][0], self.body[i][1], maze_colors[attract])
            else:
                self.ft.set(self.body[i][0], self.body[i][1], maze_colors[player])


class SnakeGame():
    def __init__(self, ft, gamepad):
        self.paused = False
        self.ft = ft
        self.gamepad = gamepad
        self.maze = self.generate_maze()

        # user defined restart
        self.triggeredEndGame = False

        # AI playing until user presses a button
        self.attractMode = True
        self.maxLength = 0

        self.KEYCODES = {
          'L': {'key': 294, 'callback': None},
          'R': {'key': 295,'callback': None},
          'A': {'key': 288,'callback': None},
          'B': {'key': 289,'callback': None},
          'X': {'key': 291,'callback': None},
          'Y': {'key': 292,'callback': None},
          'START':{'key': 299, 'callback': self.startBtn},
          'SELECT':{'key': 298, 'callback': self.newMap},
        }


    # key handlers
    def newMap(self):
        print("New map")
        self.triggeredEndGame = True
        return ""
    def startBtn(self):
        self.attractMode = not self.attractMode
        print("Attract mode: {0}".format(self.attractMode))
        return ""
    def endGame(self):
        return "done"


    # screen handlers
    def clearScreen(self, col=(0,0,0)):
        for y in xrange(self.ft.height):
            for x in xrange(self.ft.width):
                self.ft.set(x,y,col)

    def drawMap(self):
        for y in xrange(self.ft.height):
            for x in xrange(self.ft.width):
                self.ft.set(x, y, maze_colors[self.maze[y][x]])


    def generate_maze(self, num = None):
        maze = []
        # outer walls
        for y in xrange(self.ft.height):
            line = []
            for x in xrange(self.ft.width):
                if x == 0 or y == 0 or y == self.ft.height-1 or x == self.ft.height-1:
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
            for x in xrange(10, self.ft.width-10):
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
                    maze[self.ft.height-1-offset-y][x+offset] = wall
                    maze[self.ft.height-1-offset-y][self.ft.width-1-offset-x] = wall
                    maze[y+offset][self.ft.width-1-offset-x] = wall

            for y in range(32-4, 32+4):
                for x in range(32-4, 32+4):
                    maze[y][x] = wall

        return maze

    def get_neighbors(self, x, y):
        neighbor_list = []
        for d in directions:
            next_x = x + d[0]
            next_y = y + d[0]

            # ignore border
            if next_x > 1 and next_x < len(self.maze[0])-2 and next_y > 1 and next_y < len(self.maze)-2:
                neighbor_list.append([next_x, next_y])
        return neighbor_list


    def is_valid(self, x, y):
        if x >= 1 and x <= len(self.maze[0]) - 2 and y >= 1 and y <= len(self.maze) - 2:
            return True
        return False


    def get_pos(self):
        done = False
        while not done:
            p_x = random.randint(1,len(self.maze[0])-1)#int(random.random()*len(maze[0]))
            p_y = random.randint(1,len(self.maze)-1)#int(random.random()*len(maze))

            if (self.maze[p_y][p_x] == cell):
                done = True
                break

        return (p_x, p_y)


    def execute(self):
        print("Running Snake game.")

        done = False
        snake = Snake(self.ft, self.get_pos(), self.maze)
        fruits = []

        ## initially draw
        self.drawMap()
        self.ft.send()
        snake.show(self.attractMode)

        #fruitActive = True
        fruits.append(self.get_pos())#[random.randint(1,ft.width-2), random.randint(1, ft.height-2)]

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
            # debounced single key presses
            # --- DOESNT WORK WELL, can't seem to distinguish axes
            #event = self.gamepad.read_one()
            #if event is not None:
            #    if event.code == ecodes.ABS_Y and event.value == 128: #up
            #        self.currSand += 1
            #        if self.currSand > 3:
            #            self.currSand = 0

            # player control
            if not self.attractMode:
                if self.KEYCODES["A"]["key"] in keys:
                    snake.grow()

                # dpad events
                if self.gamepad.absinfo(ecodes.ABS_X).value < 128:
                    snake.setDir(-1,0)
                if self.gamepad.absinfo(ecodes.ABS_X).value > 128:
                    snake.setDir(1,0)
                if self.gamepad.absinfo(ecodes.ABS_Y).value < 128:
                    snake.setDir(0,-1)
                if self.gamepad.absinfo(ecodes.ABS_Y).value > 128:
                    snake.setDir(0,1)
            # AI
            else:
                snake.expertControl(self.maze, fruits)

            # eat fruit
            fruit_idx = snake.eat(fruits)
            snake.update()
            snake.show(self.attractMode)

            # remove fruit from list if it was eaten
            if fruit_idx > -1:
                del fruits[fruit_idx]

            # ensure we have a fruit!
            if len(fruits) > 0:
                for f in fruits:
                    self.ft.set(f[0], f[1], maze_colors[fruit])
            else: # ensure we always have 1
                fruits.append(self.get_pos())

            # add a random fruit
            if random.random() > 0.8 and len(fruits) < 5:
                fruits.append(self.get_pos())

            # draw to matrix
            self.ft.send()

            # reset game
            if snake.endgame(self.maze) or self.triggeredEndGame == True:
                if self.maxLength < snake.getLength():
                    self.maxLength = snake.getLength()
                    print("New best: {0}".format(self.maxLength))
                else:
                    print("Prior best: {0}".format(self.maxLength))


                self.triggeredEndGame = False
                self.clearScreen((180,0,0))
                self.ft.send()
                sleep(2)
                snake.reset(self.get_pos())
                self.maze = self.generate_maze()

            if done:
                break

            sleep(0.10)

        self.clearScreen()
        self.ft.send()
        print("Done")
        return
