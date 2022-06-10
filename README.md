# LED-Display

## Dependencies:

* Flaschen-Taschen
* Python 2.7 (for FT) - see `requirements.txt`

## Start:

Run `start-server-command.sh` as super user (simple script to kick off `ft-server`

**What worked for my display (Adafruit 64x64, PWM solder mod applied)**

`./flaschen-taschen/server/ft-server -d --led-slowdown-gpio=4 --led-rows=64 --led-cols=64 --led-no-hardware-pulse --led-gpio-mapping=adafruit-hat --led-show-refresh --led-brightness=50`
