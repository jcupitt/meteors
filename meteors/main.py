#!/usr/bin/python

import random
import math

import pyglet
from pyglet.gl import *
from pyglet.window import key

from vector import *
from world import *
from enums import *
from objects import *
from game import *

window = pyglet.window.Window(fullscreen=False)
window.set_exclusive_mouse()
game = Game(window)

# Event registration
@window.event
def on_draw():
    game.draw()

@window.event
def on_key_press(symbol, modifiers):
    game.on_key(symbol, modifiers, True)

@window.event
def on_key_release(symbol, modifiers):
    game.on_key(symbol, modifiers, False)

# Register update method @ 60 fps
pyglet.clock.schedule_interval(game.update, 1.0/60.0)

# start the application
pyglet.app.run()
