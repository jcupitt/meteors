import random
import math

import pyglet
from pyglet.gl import *
from pyglet.window import key

from vector import *
from world import *
from enums import *

class Meteor(WObject):
    # Meteor bass class
    def __init__(self, start_pos, start_deg, num_points, size, speed, max_health):
        WObject.__init__(self)
        self.init_pos(start_pos)
        self.vel = self.deg_to_vel(start_deg) * speed
        self.size = Vector2(size, size)
        self.num_points = num_points
        self.points = self.generate_points()
        self.turn_speed = random.uniform(-20, 20)

        self.max_health = max_health
        self.health = self.max_health

        self.draw_circle = False

    def bounding_circle(self):
        return BoundingCircle(self.pos, self.size.x / 2)

    def hit(self):
        self.health = self.health - 1
        if self.health == 0:
            self.remove = True

    def generate_points(self):
        interval = 360 / self.num_points
        points = []
        first = None
        for i in range(self.num_points):
            deg = i * interval
            length = random.uniform(0.7, 1) / 2
            p = self.deg_to_vel(deg) * length + Vector2(0.5, 0.5)
            points.append(p)
            if i == 0:
                first = p
            else:
                points.append(p)
        points.append(first)
        return points

    def update(self, time, window):
        # update color (white -> yellow -> red)
        # bias to make 1 health completely red and full health completely white
        # max_health must be greater than 1
        h = float(self.health - 1) / (self.max_health - 1)
        if h > 0.5: # approach yellow
            self.color = [1, 1, (h - 0.5) / 0.5]
        else: # approach red
            self.color = [1, h / 0.5, 0]
       
        # rotate
        self.update_deg(self.deg + self.turn_speed * time)

        # update position
        # allow to dissappear off edge, but jump to the opposite edge once that happens
        pos = self.pos + self.vel * time
        (winx, winy) = window.get_size()
        if pos.x < 0 - self.size.x / 2:
            pos.x = pos.x + (1.5 * self.size.x + winx)
        if pos.x > winx + self.size.x:
            pos.x = pos.x - (1.5 * self.size.x + winx)
        if pos.y < 0 - self.size.y:
            pos.y = pos.y + (1.5 * self.size.y + winy)
        if pos.y > winy + self.size.y:
            pos.y = pos.y - (1.5 * self.size.y + winy)
        self.update_pos(pos)


class Meteor1(Meteor):
    # big meteor
    def __init__(self, start_pos, start_deg):
        Meteor.__init__(self, start_pos, start_deg, 18, 200, 40, 6)


class Meteor2(Meteor):
    # medium meteor
    def __init__(self, start_pos, start_deg):
        Meteor.__init__(self, start_pos, start_deg, 12, 100, 60, 4)


class Meteor3(Meteor):
    # small meteor
    def __init__(self, start_pos, start_deg):
        Meteor.__init__(self, start_pos, start_deg, 8, 40, 80, 2)


class Bullet(WObject):
    # gun projectile
    def __init__(self, start_pos, start_deg):
        WObject.__init__(self)
        self.init_pos(start_pos)
        self.vel = self.deg_to_vel(start_deg) * 500
        self.init_deg(start_deg)
        self.size = Vector2(5, 9)
        self.points = self.to_points([0, 0, 0.5, 1, 0.5, 1, 1, 0, 1, 0, 0, 0])

    def update(self, time, window):
        # update position and flag for removal if off screen
        self.update_pos(self.pos + self.vel * time)
        (winx, winy) = window.get_size()
        if self.pos.x < 0 or self.pos.x > winx or self.pos.y < 0 or self.pos.y > winy:
            self.remove = True

    def hit(self):
        self.remove = True

class Ship(WObject):
    # the players ship
    def __init__(self, start_pos):
        WObject.__init__(self)
        self.init_pos(start_pos)
        self.size = Vector2(10, 20)
        self.init_deg(0)
        self.vel = Vector2(0, 0)

        self.accel = 100
        self.turn_speed = 300
        self.turn_state = None
        self.thrust_state = None

        self.points = self.to_points([0.5, 1, 1, 0, 
                                      1, 0, 0.5, 0.2, 
                                      0.5, 0.2, 0, 0, 
                                      0, 0, 0.5, 1])

    def hit(self):
        self.remove = True

    def turn(self, direction, press):
        if press:
            self.turn_state = direction
        else:
            self.turn_state = None

    def thrust(self, direction, press):
        if press:
            self.thrust_state = direction
        else:
            self.thrust_state = None

    def update(self, time, window):
        # update velocity
        if self.thrust_state:
            added_vel = self.deg_to_vel(self.deg) * self.accel * time
            if self.thrust_state == THRUST.forward:
                self.vel = self.vel + added_vel
            elif self.thrust_state == THRUST.back:
                self.vel = self.vel - added_vel

        # update angle
        if self.turn_state:
            if self.turn_state == TURN.left:
                self.update_deg(self.deg + self.turn_speed * time)
            elif self.turn_state == TURN.right:
                self.update_deg(self.deg - self.turn_speed * time)
            self.update_deg(self.deg % 360)
       
        # update position based on velocity and keep within window
        pos = self.pos + self.vel * time
        (winx, winy) = window.get_size()
        pos.x = pos.x % winx
        pos.y = pos.y % winy
        self.update_pos(pos)


class Collider():
    # Helper class to aid with collision detection.
    # Register collision detection and handling methods for particular pairs of
    # objects (by class name), and you can then just call Collider.collide(obj1, obj2),
    # and Collider.handle(obj1, obj2) and this class will call the appropriate methods.
    def __init__(self):
        self.method_dict = dict()

    def register_methods(self, detector, handler, type1, type2):
        # Pass in a collision detection method, a collision handling method,
        #  and two object class names as strings.
        # The methods are expected to accept two arguments (the two objects)
        #  in the order which their types are submitted. Will raise an error if you register
        #  a method for the same pair of objects
        if self._find_methods(type1, type2) != None or self._find_methods(type2, type1) != None:
            raise('Already registered methods for ' + type1 + ' and ' + type2)
        if not type1 in self.method_dict:
            self.method_dict[type1] = dict()
        self.method_dict[type1][type2] = [detector, handler]

    def collide(self, obj1, obj2):
        # Pass it any two world objects (in any order) and it will call the appropriate
        #   collision detection method (based on their type) and return true if they collided.
        # If there is no method registered for that pair, it will return false.
        if obj1.remove or obj2.remove:
            return False
        type1 = self._type(obj1)
        type2 = self._type(obj2)
        methods1 = self._find_methods(type1, type2)
        methods2 = self._find_methods(type2, type1)
        if methods1 == None and methods2 == None:
            return False
        # only one of these will do something
        if methods1 != None:
            return methods1[0](obj1, obj2)
        elif methods2 != None:
            return methods2[0](obj2, obj1)
        return False

    def handle(self, obj1, obj2):
        # Pass it any two world objects (in any order) and it will call the appropriate
        #   collision handling method (based on their type).
        # If there is no method registered for that pair, it will do nothing.
        if obj1.remove or obj2.remove:
            return
        type1 = self._type(obj1)
        type2 = self._type(obj2)
        methods1 = self._find_methods(type1, type2)
        methods2 = self._find_methods(type2, type1)
        if methods1 == None and methods2 == None:
            return
        # only one of these will do something
        if methods1 != None:
            methods1[1](obj1, obj2)
        elif methods2 != None:
            methods2[1](obj2, obj1)

    def _find_methods(self, type1, type2):
        if type1 in self.method_dict:
            if type2 in self.method_dict[type1]:
                return self.method_dict[type1][type2]
        return None

    def _type(self, obj):
        return obj.__class__.__name__
