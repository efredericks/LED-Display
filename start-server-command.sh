#!/bin/bash

../flaschen-taschen/server/ft-server -d --led-slowdown-gpio=4 --led-rows=64 --led-cols=64 --led-no-hardware-pulse --led-gpio-mapping=adafruit-hat --led-show-refresh --led-brightness=50
#./flaschen-taschen/server/ft-server -d --led-slowdown-gpio=4 --led-rows=64 --led-cols=64 --led-no-hardware-pulse --led-gpio-mapping=adafruit-hat-pwm --led-show-refresh --led-brightness=50
