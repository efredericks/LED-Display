import flaschen
import numpy as np
import noise

UDP_IP = 'localhost'
UDP_PORT = 1337
ft = flaschen.Flaschen(UDP_IP, UDP_PORT, 64, 64)
pixels = np.asarray(ft)
#pixels[1, :] = (255, 0, 0)
#pixels[:, 1] = (0,255,0)
#pixels[(pixels == (0,0,0)).all(axis=-1)] = (255,0,255)
#ft.send()

# noise
octaves = 4
frequency = 16.0 * octaves
z = 0

while True:
  for y in range(0,ft.height):
    for x in range(0,ft.width):
      n = noise.snoise3(x / frequency, y/frequency, z/frequency, octaves=octaves,persistence=0.25)
      col = (0,0,0)
      if n < 0.25:
        col = (20,0,0)
      elif n < 0.5:
        col = (0,20,0)
      elif n < 0.75:
        col = (0,0,20)
      pixels[y,x] = col
  ft.send()
  z += 1
    #if screen[y][x] == ' ':
      #n = noise.snoise3(x / frequency, y/frequency, z/frequency, octaves=octaves,persistence=0.25)
      #col = (0,0,0)
      #if n < 0.25:
      #  col = (20,0,0)
      #elif n < 0.5:
      #  col = (0,20,0)
      #elif n < 0.75:
      #  col = (0,0,20)
      #ft.set(x,y,col)
    #else:
      #ft.set(x,y,COLORS[screen[y][x]])
