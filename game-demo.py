""" steps:
1) start ft server (flaschen-taschen/server) $ ./ft-server
2) separate terminal (vs doesn't like it), set env variable: export FT_DISPLAY=localhost (or whatev server)

-- maybe upgrade everything to py3 someday...
"""

import flaschen
import random
import math
from opensimplex import OpenSimplex
from time import sleep

noise = OpenSimplex(seed=random.randint(0,10000))

two_pi = math.pi * 2.0

#flaschen things
UDP_IP = 'localhost'
UDP_PORT = 1337
ft = flaschen.Flaschen(UDP_IP, UDP_PORT, 64, 64)#45, 35)

# https://medium.com/swlh/fun-with-python-1-maze-generator-931639b4fb7e
cell = 'c'
wall = 'w'
unvisited = 'u'
player = '@'
end = 'e'
maze_colors = {
  wall: (255,0,255),
  cell: (0,0,0),
  end: (255,0,0),
  unvisited: (20,20,20),
  player: (0,255,0)
}
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

  attempts = 20
  while attempts > 0:
    # maze[start_y][start_x] = player
    timeout = 150
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

# falling sand?

def p5map(n, start1, stop1, start2, stop2):
  return ((n-start1)/(stop1-start1))*(stop2-start2)+start2

def generateFlow(width, height, z):
  ff = []
  for y in xrange(0,height):
    line = []
    for x in xrange(0,width):
      n = noise.noise3d(x*0.1, y*0.1, z*0.1)
      line.append(p5map(n, -1.0, 1.0, 0.0, two_pi))
      #line.append(math.ceil(
      #  (p5map(n, -1.0, 1.0, 0.0, two_pi) * (math.pi / 4.0)) / (math.pi / 4.0)
      #))
    ff.append(line)
  return ff

if __name__ == '__main__':
  z = 0
  while True:
    # FLOW FIELD STUFF
    ff = generateFlow(ft.width, ft.height, random.randint(0,50000))#z)
    maze = []
    for y in xrange(0,ft.height):
      line = []
      for x in xrange(0,ft.width):
        line.append((0,0,0))
      maze.append(line)

    z += 1
    particles = []

    for i in xrange(0,200):
      life = int(random.random() * 100)
      p = {
        "x": int(random.random() * ft.width-1),
        "y": int(random.random() * ft.height-1),
        "life": life,
        "isAlive": True,
        "color": (int(random.random() * 255), int(random.random() * 255), int(random.random() * 255)),
      }
      particles.append(p)

    
    alive = len(particles)
    while alive > 0:
      alive = 0
      for p in particles:
        if p["isAlive"] == True:
          angle = ff[p["y"]][p["x"]]
          xstep = math.cos(angle)
          ystep = math.sin(angle)

          p["x"] = int(xstep + p["x"])
          p["y"] = int(ystep + p["y"])
          p["life"] -= 1

          if p["life"] <= 0 or p["x"] < 0 or p["x"] > ft.width-1 or p["y"] < 0 or p["y"] > ft.height-1:
            p["isAlive"] = False
          else:
            alive += 1
            maze[p["y"]][p["x"]] = p["color"]#(0,255,0)

      for y in xrange(0,ft.height):
        for x in xrange(0,ft.width):
          ft.set(x, y, maze[y][x])
      ft.send()

    # pure noise
    # for y in xrange(0, ft.height):
    #   for x in xrange(0, ft.width):
    #     col = player
    #     if (ff[y][x] < 0.0): col = wall
    #     elif (ff[y][x] < 0.25): col = cell
    #     elif (ff[y][x] < 0.5): col = end
    #     elif (ff[y][x] < 0.75): col = unvisited
    #     else: col = player
    #     # r = p5map(ff[y][x], 0.0, two_pi, 0, 255)
    #     ft.set(x, y, maze_colors[col])

      ft.send()
      # sleep(0.15)
      sleep(0.05)
      print(alive)

    print("all dead")





    # MAZE STUFF
    # # maze = generate_maze(ft.width, ft.height)
    # maze = random_walk(ft.width, ft.height)
    # pos = get_pos(maze)
    # player_x = pos[0]
    # player_y = pos[1]
    # print('maze generated')

    # not_solved = True
    # while not_solved:
    #   for y in xrange(0, ft.height):
    #     for x in xrange(0, ft.width):
    #       # ft.set(x, y, maze_colors[maze[y][x]])

    #   ft.set(player_x, player_y, maze_colors[player])

    #   d = random.choice(directions)
    #   next_x = player_x + d[0]
    #   next_y = player_y + d[1]
    #   if (next_x >= 0 and next_x < ft.width and next_y >= 0 and next_y < ft.height):
    #     if (maze[next_y][next_x] == cell):
    #       player_x = next_x
    #       player_y = next_y
    #     elif (maze[next_y][next_x] == end):
    #       not_solved = False

    #   ft.send()
    #   sleep(0.05)
