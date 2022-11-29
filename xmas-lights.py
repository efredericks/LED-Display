# snowflakes falling?
# cottage

from bdfparser import Font

import flaschen
import numpy as np
import noise
import time
import random

def p5Map(n, start1, stop1, start2, stop2):
  return ((n - start1) / (stop1 - start1)) * (stop2 - start2) + start2

UDP_IP = 'localhost'
UDP_PORT = 1337
ft = flaschen.Flaschen(UDP_IP, UDP_PORT, 64, 64)
pixels = np.asarray(ft)
#pixels[1, :] = (255, 0, 0)
#pixels[:, 1] = (0,255,0)
#pixels[(pixels == (0,0,0)).all(axis=-1)] = (255,0,255)
#ft.send()

font = Font("assets/Pixuf-8.bdf")
snowflake_spr = np.array(font.draw("*").todata(2), dtype=np.bool_)

# noise
octaves = 8
frequency = 16.0 * octaves
z = 0

WHITE = (255, 255, 255)
BLUISH = (0, 80, 220)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

drips = []
snowflakes = []
while True:
  if random.random() > 0.8:
    drips.append({'x': random.randint(0, ft.width-1), 'len': 0, 'life': random.randint(int(ft.height/3), ft.height-1)})
  if random.random() > 0.6:
      snowflakes.append({'x': random.randint(0, ft.width-1), 'y': 0, 'life': random.randint(int(ft.height/3), ft.height-1)})

  for y in range(0,ft.height):
    for x in range(0,ft.width):
      n = noise.snoise3(x / frequency, y/frequency, z/frequency, octaves=octaves,persistence=0.25)

      blk = p5Map(n, -1.0, 1.0, 0, 80)
      #if n < 0.5:
      #  col = BLACK
      #elif n < 0.5:
      #  col = (0,255,0)
      #elif n < 0.75:
      #  col = (0,0,255)
      pixels[y,x] = (blk, blk, blk)

  for d in drips:
    for l in range(d['len']):
      pixels[l, d['x']] = WHITE
      if d['x'] > 0: pixels[l,d['x']-1] = BLUISH
      if d['x'] < ft.width-2: pixels[l,d['x']+1] = BLUISH
    d['len'] += 1
    d['life'] -= 1
  drips = [d for d in drips if d['len'] < ft.height-1 and d['life'] > 0]

  testText = font.draw("*")
  testTextArr = np.array(testText.todata(2))
  for s in snowflakes:
    pixels[s['y'], s['x']] = WHITE
    s['life'] -= 1
    s['y'] += 1

    #out_pixels = pixels[s['y']+snowflake_spr.shape[0], s['x']+snowflake_spr.shape[1]]
    #out_pixels[snowflake_spr] = BLUISH

    #out_pixels = pixels[s['y']+snowflake_spr.shape[0], s['x']+snowflake_spr.shape[1]]
    #out_pixels[snowflake_spr] = (220, 220, 220)
    for _r in range(len(testTextArr)):
        for _c in range(len(testTextArr[0])):
            if testTextArr[_r,_c] == 1 and s['y']+_r < ft.height-1 and s['x']+_c < ft.width-1:
                pixels[s['y']+_r,s['x']+_c] = (220,220,220)


        #testText = self.font.draw("Hello there!")
        #testTextArr = np.array(testText.todata(2))

        #for _r in range(len(testTextArr)):
        #    for _c in range(len(testTextArr[0])):
        #        if testTextArr[_r,_c] == 1:
        #            self.pixels[_r,_c] = (0,255,0)



    if random.random() > 0.9:
      s['x'] += random.choice([0, 0, 0, -1, 1])
    if s['x'] < 0: s['x'] = 0
    if s['x'] > ft.width-1: s['x'] = ft.width-1
  snowflakes = [s for s in snowflakes if s['y'] < ft.height-1 and s['life'] > 0]


  ft.send()
  z += 1
  time.sleep(0.05)
