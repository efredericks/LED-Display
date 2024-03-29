from enum import Enum
from bdfparser import Font
import numpy as np

## DEFINING A SPRITE
# 1) give it a 'tile' (char)
# 2) give it a color
# 3) create the sprite (8x8)

# setup BDF font
font = Font("assets/Pixuf-8.bdf")
#font = Font("assets/ucs-fonts/4x6.bdf")
assert font is not None

# lookup code
player = "@"
orc = "O"
troll = "T"
dirt1 = 'd1'
dirt2 = 'd2'
dirt3 = 'd3'
wall = "#"
floor = "."
clear = ' '
dead = '%'
exit = 'e'

# lookup tables
WALKABLE = [floor, dirt1, dirt2, dirt3, dead, exit]
DIRT = [dirt1, dirt2, dirt3]
ENTITY_SPRITES = [player, orc]

# defines
ENEMIES_PER_CHUNK = 50

TEXTWIDTH = 5
CELLSIZE = 8
TEXTOFFSET = int((CELLSIZE - TEXTWIDTH) / 2)


NUMCELLS = int(64/8) # 64 = # of pixels on LED array (ft.width)

# the whole map
MAP_ROWS = 64#100
MAP_COLS = 64#100

# the screen
HALF_CAM_R = int(NUMCELLS / 2)
HALF_CAM_C = int(NUMCELLS / 2)

# player action states
class ACTIONS(Enum):
    WAIT = 0

COLORS = {
  clear: (0,0,0),
  player: (0,220,0),
  wall: (220,0,220),
  floor: (10, 10, 10),
  dirt1: (87,65,47),
  dirt2: (87,65,47),
  dirt3: (87,65,47),
  orc: (255,0,0),
  dead: (20,20,20),
  exit: (255,120,0),
  'currHealth': (0,255,0),
  'maxHealth': (120,0,0),
}

SPRITES = {
    wall: {'sprite': np.array(font.draw(wall).todata(2), dtype=np.bool_), 'color': (255,0,255)},
    floor: {'sprite':np.array(font.draw(floor).todata(2), dtype=np.bool_), 'color': (20,20,20)},
    player: {'sprite':np.array(font.draw(player).todata(2), dtype=np.bool_), 'color': (0,220,0)},
    orc: {'sprite':np.array(font.draw(orc).todata(2), dtype=np.bool_), 'color': (220,0,0)},
    troll: {'sprite':np.array(font.draw(troll).todata(2), dtype=np.bool_), 'color': (220,0,0)},
    dead: {'sprite':np.array(font.draw(dead).todata(2), dtype=np.bool_), 'color': (220,0,0)},
    exit: {'sprite':np.array(font.draw(exit).todata(2), dtype=np.bool_), 'color': (220,0,0)},
}

# 8x8
"""
SPRITES = {
  player: [
    "..0000..",
    ".0....0.",
    "0.0..0.0",
    "0......0",
    "0.0..0.0",
    ".0.00.0.",
    "..0000..",
    "........",
  ],
  orc: [
    "..0000..",
    ".0....0.",
    "0.0..0.0",
    "0......0",
    "0.0000.0",
    ".0....0.",
    "..0000..",
    "........",
  ],
  dead: [
    "........",
    ".0....0.",
    "..0..0..",
    "...00...",
    "...00...",
    "..0..0..",
    ".0....0.",
    "........",
  ],
  wall: [
    "........",
    "..0..0..",
    ".000000.",
    "..0..0..",
    "..0..0..",
    ".000000.",
    "..0..0..",
    "........",
  ],
  exit: [
    "........",
    "..0000..",
    ".0....0.",
    ".0....0.",
    ".0..0.0.",
    ".0....0.",
    ".000000.",
    "........",
  ],
  floor: [
    "........",
    "........",
    "........",
    "........",
    "........",
    "....0...",
    "........",
    "........",
  ],
  dirt1: [
    "........",
    "........",
    "........",
    "........",
    "........",
    "....0...",
    "........",
    "........",
  ],
  dirt2: [
    "........",
    "........",
    "..0.....",
    "......0.",
    "........",
    "........",
    "...0....",
    "........",
  ],
  dirt3: [
    "........",
    "........",
    "..0..0..",
    "........",
    ".....0..",
    "..0.....",
    "....0...",
    "........",
  ],
}
"""

## functions

#https://stackoverflow.com/questions/44338698/p5-js-map-function-in-python
def p5Map(n, start1, stop1, start2, stop2):
  return ((n - start1) / (stop1 - start1)) * (stop2 - start2) + start2
