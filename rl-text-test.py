import flaschen
from bdfparser import Font
import numpy as np
from time import sleep
import random


# font = Font("assets/Roboto-Regular-8.bdf")
# font = Font("assets/ucs-fonts/5x8.bdf")
font = Font("assets/Pixuf-8.bdf")
assert font is not None

UDP_IP = 'localhost'
UDP_PORT = 1337
ft = flaschen.Flaschen(UDP_IP, UDP_PORT, 64, 64)
pixels = np.asarray(ft)

gameMap = [
  "########",
  "#......#",
  "#......#",
  "#......#",
  "#......#",
  "#......#",
  "#......#",
  "########",
]

sprites = {
    "#": {'sprite': np.array(font.draw("#").todata(2), dtype=np.bool_), 'color': (255,0,255)},
    ".": {'sprite':np.array(font.draw(".").todata(2), dtype=np.bool_), 'color': (20,20,20)},
    "@": {'sprite':np.array(font.draw("@").todata(2), dtype=np.bool_), 'color': (0,220,0)},
    "O": {'sprite':np.array(font.draw("O").todata(2), dtype=np.bool_), 'color': (220,0,0)},
    "T": {'sprite':np.array(font.draw("T").todata(2), dtype=np.bool_), 'color': (220,0,0)},
    "😊": {'sprite':np.array(font.draw("😊").todata(2), dtype=np.bool_), 'color': (220,0,220)},
}

#testText = font.draw("Hello_there_")
#testTextArr = np.array(testText.todata(2), dtype=np.bool_)

while True:
    pixels[:,:] = (0,0,0)
    for r in range(len(gameMap)):
        for c in range(len(gameMap[r])):
            if (random.random() > 0.8 and r > 0 and r < len(gameMap)-1 and c > 0 and c < len(gameMap[0])-1):
                gameMap[r] = gameMap[r][:c] + random.choice(["😊", "O", ".", ".", "T", "@"]) + gameMap[r][c+1:]
                done = True
            char = gameMap[r][c]

            _r = r * 8
            _c = c * 8

            print(sprites[char]['sprite'].shape[0], sprites[char]['sprite'].shape[1])

            out_pixels = pixels[_r:_r+sprites[char]['sprite'].shape[0], _c:_c+sprites[char]['sprite'].shape[1]]
            out_pixels[sprites[char]['sprite']] = sprites[char]['color']

    #out_pixels = pixels[:testTextArr.shape[0], :testTextArr.shape[1]]
    #out_pixels[testTextArr] = (0, 255, 0)

    #pixels[:,-5:] = (255,0,255)

    ft.send()
    sleep(0.5)