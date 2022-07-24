# LED-Display

## Dependencies:

* Flaschen-Taschen
* Python 3 - see `requirements.txt`

## Running in hardware mode

My hardware setup comprises the [Adafruit 64x64 LED panel](https://www.adafruit.com/product/3649){:target="_blank"}, a Raspberry Pi 4, and an 8bitdo NES controller (my model appears to be deprecated).  You can most likely use any Raspberry Pi that can hook up to the panel and any USB device that the Pi can recognize, though you may need to remap the keys (i.e., look up the keycodes and update the various `KEYCODE` dictionaries).

Run `start-server-command.sh` as super user (simple script to kick off `ft-server`).  Ensure all IP addresses and ports make sense for your setup (localhost if on the same device, IP address if not, etc.).

**What worked for my display (Adafruit 64x64, PWM solder mod applied)**

`./flaschen-taschen/server/ft-server -d --led-slowdown-gpio=4 --led-rows=64 --led-cols=64 --led-no-hardware-pulse --led-gpio-mapping=adafruit-hat --led-show-refresh --led-brightness=50`

## Running in simulated mode (terminal mode)

1. Open a separate terminal and run `bash start-terminal-server-command.sh`
2. Run the roguelike demo via: `python3 led-main.py --autostart=RL`
   1. A GUI will popup that simulates a controller - this seemed to be the easiest way to capture user input without scraping all input events.
   2. As it stands, only the roguelike is setup to run in simulated mode.
3. Currently the game is waiting for a keypress to kick off.  

## Key config:

* L (period) - wait/rest
* VI keys / D-pad - 8-way directional movement
* L+R - quit
* R - win!  (debug)

All keys will trigger a time step, so pressing a key that is not mapped will cause enemies to move.  At present though this doesn't trigger a rest.

## TODO

1. Significant code cleanup - right now there are several disparate projects being developed with the hope that an API will magically coalesce - I have some thoughts here but haven't had much time as I wanted to get things working first.
2. Write up a clear bill of materials and setup guide.
3. Harden the hardware installation so that it can be used and abused in a public space.