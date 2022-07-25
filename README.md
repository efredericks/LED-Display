# LED-Display

This project is intended for student outreach to demonstrate how much fun you can have with a Raspberry Pi and some hardware.  Currently the focus is developing a Roguelike (loosely following the [/r/roguelikedev tutorial series](http://rogueliketutorials.com/tutorials/tcod/v2/)), however there are a handful of other demos that are half-developed as well!

## Dependencies:

* [Flaschen-Taschen](https://github.com/hzeller/flaschen-taschen) for communicating with the LED panel / simulating the LED panel
* Python 3 - see `requirements.txt`

## Running in hardware mode

My hardware setup comprises the [Adafruit 64x64 LED panel](https://www.adafruit.com/product/3649), a Raspberry Pi 4, and an 8bitdo NES controller (my model appears to be deprecated).  You can most likely use any Raspberry Pi that can hook up to the panel and any USB device that the Pi can recognize, though you may need to remap the keys (i.e., look up the keycodes and update the various `KEYCODE` dictionaries).

Run `sudo bash start-server-command.sh` (simple script to kick off `ft-server`).  Ensure all IP addresses and ports make sense for your setup (localhost if on the same device, IP address if not, etc.).

**Note** - ensure you clone the Flaschen-Taschen repository and put it at the same level as the LED-Display repository - or modify the paths inside the bash script to reflect your setup.

## Running in simulated mode (terminal mode)

1. Open a separate terminal and run `bash start-terminal-server-command.sh`
2. Run the roguelike demo via: `python3 led-main.py --autostart=RL`
   1. A GUI will popup that simulates a controller - this seemed to be the easiest way to capture user input without scraping all input events.
   2. As it stands, only the roguelike is setup to run in simulated mode.
3. Currently the game is waiting for a keypress to kick off.  Hitting the `.` on the controller is a decent way to start.

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
4. Write a better hand-holding set of steps in this guide.

## Screenshots / GIFs

### [Week 1 updates](https://www.reddit.com/r/roguelikedev/comments/vm9yam/roguelikedev_does_the_complete_roguelike_tutorial/ie4sv5d/)

![Initial attempt](https://i.imgur.com/L0ylMVa.jpg)

### [Week 2 updates](https://www.reddit.com/r/roguelikedev/comments/vrnoay/roguelikedev_does_the_complete_roguelike_tutorial/iey4lje/)

![Main screen + other demos](https://i.imgur.com/5uj3naj.gifv)

![RL screen](https://i.imgur.com/EaHqdmb.jpg)

![Character movement + attacking](https://i.imgur.com/eQwk6TZ.gifv)

![Sprite setup](https://i.imgur.com/rR37DIf.png)

### [Week 3 updates](https://www.reddit.com/r/roguelikedev/comments/vx0cgm/roguelikedev_does_the_complete_roguelike_tutorial/ifuq7pm/)

![Local development/testing](https://i.imgur.com/kq2DIQY.png)

![BSP map added](https://i.imgur.com/mAUspe7.gifv)

### [Week 4 updates](https://www.reddit.com/r/roguelikedev/comments/w2c8t8/roguelikedev_does_the_complete_roguelike_tutorial/igqin2i/)

![Enemy attacking](https://i.imgur.com/8Fqh0vI.gifv)

![Exit condition](https://i.imgur.com/sTMjvjy.gifv)
