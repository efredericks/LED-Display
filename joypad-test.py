from evdev import InputDevice, categorize, ecodes
import flaschen
import random
import math
from time import sleep

gamepad = InputDevice('/dev/input/event0')

UDP_IP = 'localhost'
UDP_PORT = 1337
ft = flaschen.Flaschen(UDP_IP, UDP_PORT, 64, 64)
COLORS = {
  'wall': (255,0,255),
  'player': (0,255,0),
  'win': (255,0,0),
}


wall = 'w'
cell = '.'
end = '!'
unvisited = ' '
player = '@'
WALKABLE = [cell, end]
directions = [
  [-1,-1],
  [0,-1],
  [1,-1],
  [1,0],
  [1,1],
  [0,1],
  [-1,1],
  [-1,0]
]
maze_colors = {
  wall: (255,0,255),
  cell: (0,0,0),
  end: (255,0,0),
  unvisited: (20,20,20),
  player: (0,255,0)
}

def get_pos(maze):
  done = False
  while not done:
    p_x = int(random.random()*len(maze[0]))
    p_y = int(random.random()*len(maze))

    if (maze[p_y][p_x] == cell):
      return (p_x, p_y)

def random_walk(width, height):
  maze = []
  for y in xrange(0,height):
    line = []
    for x in xrange(0,width):
      line.append(unvisited)
    maze.append(line)

  start_x = int(random.random()*width)
  start_y = int(random.random()*height)

  attempts = 120
  while attempts > 0:
    # maze[start_y][start_x] = player
    timeout = 250
    while timeout > 0:
      d = random.choice(directions)

      next_x = start_x + d[0]
      next_y = start_y + d[1]

      maze[start_y][start_x] = cell

      # boundary 
      if (next_x < 0 or next_x >= width or next_y < 0 or next_y >= height):
        break
      else:
        start_x = next_x
        start_y = next_y
        timeout-=1

    attempts-=1


  end_p = get_pos(maze)
  maze[end_p[1]][end_p[0]] = end

  return maze
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
  'SELECT':{'key': 298, 'callback': test},
}

# are these constants somewhere?
KEYDOWN = 1
KEYUP = 0
KEYHOLD = 2


maze = random_walk(ft.width, ft.height)
p = get_pos(maze)
player_col = p[0]#random.randint(0,ft.width-1)
player_row = p[1]#random.randint(0,ft.height-1)
#maze[player_row][player_col] = player

#p = get_pos(maze)
#win_col = p[0]#random.randint(0,ft.width-1)
#win_row = p[1]#random.randint(0,ft.height-1)
#maze[win_row][win_col] = end

done = False
#while not done:
    # draw player
    #ft.set(0,0,(255,0,255))
    #ft.set(player_col, player_row, COLORS["player"])
    #ft.send()

# handle events

## initially draw
drawMap(ft, maze)
ft.set(player_col, player_row, COLORS["player"])
#ft.set(win_col, win_row, COLORS["win"])
ft.send()

for event in gamepad.read_loop():
    #clearScreen(ft)
    drawMap(ft, maze)
    ft.set(player_col, player_row, COLORS["player"])
    #ft.set(win_col, win_row, COLORS["win"])
    ft.send()

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
    if done:
        break

clearScreen(ft)
ft.send()
print("Done")

