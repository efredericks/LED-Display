#from __future__ import annotations
from roguelike_sprites import *
from typing import Tuple, Iterator
import numpy as np
import tcod
import random
from roguelike_sprites import *

# Room types
class RectangularRoom:
  def __init__(self, x: int, y: int, width: int, height: int):
    self.x1 = x
    self.x2 = x + width
    self.y1 = y
    self.y2 = y + height

  def intersects(self, other) -> bool:
    return (
      self.x1 <= other.x2
      and self.x2 >= other.x1
      and self.y1 <= other.y2
      and self.y2 >= other.y1
    )

  @property
  def center(self) -> Tuple[int, int]:
    center_x = int((self.x1 + self.x2) / 2)
    center_y = int((self.y1 + self.y2) / 2)
    return center_x, center_y

  @property
  def inner(self) -> Tuple[slice, slice]:
    return slice(self.y1 + 1, self.y2), slice(self.x1 + 1, self.x2)

  @property
  def randomPos(self) -> Tuple[int, int]:
      c = random.randint(self.x1+1, self.x2-1)
      r = random.randint(self.y1+1, self.y2-1)
      return c, r

def tunnel_between(
  start: Tuple[int,int], end: Tuple[int,int]
) -> Iterator[Tuple[int, int]]:
  x1, y1 = start
  x2, y2 = end
  if random.random() < 0.5: # move horizontally, then vertically
    corner_x, corner_y = x2, y1
  else:
    corner_x, corner_y = x1, y2

  # tunnel coords
  for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
    yield x, y
  for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
    yield x, y


# Returns a map
class MapGenerator:
  def __init__(self, width: int=64, height: int=64):
    self.width = width
    self.height = height

    # BSP info
    self.room_max_size = 10
    self.room_min_size = 6
    self.max_rooms = 30



  # Returns a map filled with walls to be dug
  def initMap(self):
    return np.full((self.height,self.width), fill_value=wall)

  def generateCA(self):
    pass

  def generateBSP(self):
    gameMap = self.initMap()
    exitPlaced = False

    retobj = {}

    rooms: List[RectangularRoom] = []

    player_start_x: int = 0
    player_start_y: int = 0

    exit_x: int = 0
    exit_y: int = 0

    # generate rooms
    for r in range(self.max_rooms):
      room_w = random.randint(self.room_min_size, self.room_max_size)
      room_h = random.randint(self.room_min_size, self.room_max_size)
      x = random.randint(0, self.width - room_w - 1)
      y = random.randint(0, self.height - room_h - 1)

      new_room = RectangularRoom(x, y, room_w, room_h)

      # check for intersections and dig
      if any(new_room.intersects(other_room) for other_room in rooms):
        continue

      gameMap[new_room.inner] = floor



      if len(rooms) == 0:
        player_start_x, player_start_y = new_room.center
      else:
        for x, y in tunnel_between(rooms[-1].center, new_room.center):
          gameMap[y,x] = floor


      rooms.append(new_room)


    #r1 = RectangularRoom(x=20, y=15, width=10, height=15)
    #r2 = RectangularRoom(x=35, y=15, width=10, height=15)

    #gameMap[r1.inner] = floor
    #gameMap[r2.inner] = floor

    #for x, y in tunnel_between(room_2.center, room_1.center):
    #  gameMap[y, x] = floor

    # return the *singular* exit (for now)
    exit_room = random.choice(rooms)
    if not exitPlaced:
        exitPlaced = True
        exit_x, exit_y = exit_room.randomPos
        gameMap[exit_y,exit_x] = exit
        print(exit_x, exit_y)

    retobj['map'] = gameMap
    retobj['player_start'] = {'r': player_start_y, 'c': player_start_x}
    retobj['exit'] = {'r': exit_y, 'c': exit_x}

    return retobj#gameMap, player_start_x, player_start_y

