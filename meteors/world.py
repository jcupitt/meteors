#!/usr/bin/python

import math

import pyglet
from pyglet.gl import *
from pyglet.window import key

from vector import *

class WObject():
    # Represents a game/world object. Handles it's own rendering, and updating.
    # Game objects should subclass this one. Contains some helper functions as well.
    def __init__(self):
        # how many past pos/deg to keep track of
        self.state_buffer = 5 
        # position (x,y) (x > 0 => right, y > 0 => up)
        self.init_pos(Vector2(0, 0))
        # angular position in degrees. 0 = up, 90 = left
        self.init_deg(0)
        # velocity vector
        self.vel = Vector2(0, 0)
        # size vector
        self.size = Vector2(1, 1)
        # flag to mark object for removal
        self.remove = False
        
        # Define the shape. Place all vertexes within the unit square as defined below.
        #  Use size to then size it appropriately. Points should always be in groups of
        #  2 vectors. To connect lines, you must define the connecting
        #  vertices twice.
        self.points = self.to_points([0, 0, 0, 1, 
                                      0, 1, 1, 1, 
                                      1, 1, 1, 0, 
                                      1, 0, 0, 0]) # square

        # where within the unit square should the position be defined.
        # it is also the point about which the object will rotate
        self.anchor = Vector2(0.5, 0.5)
        
        # color in RGB
        self.color = [1, 1, 1]

        # debug stuff
        self.box = self.points 
        self.circle = self.generate_circle(48)
        self.cross = self.to_points([0, 0.5, 1, 0.5, 0.5, 0, 0.5, 1])
        self.draw_box = False # shows the unit box around the object
        self.draw_circle = False # shows the unit circle around the object
        self.draw_cross = False # shows a unit cross centered on object
        self.draw_transform = False # draw the points transformed in cpu space
        self.draw_pos_change = False # draws the positional change between two frames as a line

    def to_points(self, p_list):
        # converts flat list of floats to list of Vector2
        points = []
        for i in range(len(p_list) / 2):
            x = p_list[i * 2]
            y = p_list[i * 2 + 1]
            points.append(Vector2(x, y))
        return points

    def get_point_transformed(self, index, num = 0):
        # returns the point at index from by self.points but after
        #  translation/rotation/scaling via cpu. 
        # if num > 0, will return the points generated from an older state
        num = num % self.state_buffer
        point = self.points[index]
        # center on anchor
        point = point - self.anchor
        # scale
        point.x = point.x * self.size.x
        point.y = point.y * self.size.y
        # rotate
        if num > 0:
            deg = self.last_deg[num - 1]
        else:
            deg = self.deg
        sin = math.sin(math.radians(deg))
        cos = math.cos(math.radians(deg))
        x = point.x * cos - point.y * sin
        y = point.x * sin + point.y * cos
        point.y = y
        point.x = x
        # translate
        if num > 0:
            pos = self.last_pos[num - 1]
        else:
            pos = self.pos
        point = point + pos
        return point

    def get_all_points_transformed(self, num = 0):
        # returns all transformed points. maybe slow for many points
        points = []
        for i in range(len(self.points)):
            points.append(self.get_point_transformed(i, num))
        return points

    def get_lines(self):
        # returns a list of all line segments defined by points after transformation.
        lines = []
        for i in range(len(self.points) / 2):
            p1 = self.get_point_transformed(i * 2)
            p2 = self.get_point_transformed(i * 2 + 1)
            lines.append(Line(p1, p2))
        return lines

    def init_pos(self, pos):
        # initialize position vector
        self.pos = pos
        self.last_pos = []
        for i in range(self.state_buffer):
            self.last_pos.append(pos)

    def update_pos(self, pos):
        # update the position vector
        self.last_pos.insert(0, self.pos)
        self.last_pos.pop()
        self.pos = pos

    def init_deg(self, deg):
        # initialize degrees member
        self.deg = deg
        self.last_deg = []
        for i in range(self.state_buffer):
            self.last_deg.append(deg)

    def update_deg(self, deg):
        # update the degrees member
        self.last_deg.insert(0, self.deg)
        self.last_deg.pop()
        self.deg = deg

    def get_pos_change(self, num):
        # the positional change from num update cycles ago (where num < self.state_buffer)
        num = num % self.state_buffer
        return self.pos - self.last_pos[num]

    def generate_circle(self, num_points):
        # generates a unit circle with num_points
        interval = 360.0 / num_points
        points = []
        first = None
        for i in range(num_points + 1):
            deg = i * interval
            p = self.deg_to_vel(deg) / 2 + Vector2(0.5, 0.5)
            points.append(p)
            if i == 0:
                first = p
            else:
                points.append(p)
        points.append(first)
        return points

    def deg_to_vel(self, deg):
        # convert degrees (up => 0, left => 90) 
        #  to a normalized vector (top|right => y|x > 0)
        y = abs(math.tan(math.radians(deg-90)))
        x = 1
        if deg > 0 and deg < 180:
            x = -1
        if deg > 90 and deg < 270:
            y = -y
        return Vector2(x, y).normalize()

    def draw_points(self, points):
        # draws the set of point pairs as GL_LINES
        the_points = []
        for point in points:
            the_points.append(point.x)
            the_points.append(point.y)
        pyglet.graphics.draw(len(points), GL_LINES, ('v2f', the_points))

    def draw(self):
        # simple scale/rotate/tranlate and color of gl lines
        glLoadIdentity()
        if self.draw_pos_change:
            glColor3f(1, 1, 0)
            points = [self.last_pos.x, self.last_pos.y, self.pos.x, self.pos.y]
            self.draw_points(points)
        if self.draw_transform:
            points = self.get_all_points_transformed()
            glColor3f(0, 0, 1)
            self.draw_points(points)
        glColor3f(self.color[0], self.color[1], self.color[2])
        glTranslatef(self.pos.x, self.pos.y, 0)
        glRotatef(self.deg, 0, 0, 1)
        glScalef(self.size.x, self.size.y, 1)
        glTranslatef(-self.anchor.x, -self.anchor.y, 0)
        self.draw_points(self.points)
        if self.draw_box:
            self.draw_points(self.box)
        if self.draw_circle:
            self.draw_points(self.circle)
        if self.draw_cross:
            self.draw_points(self.cross)

class Font(WObject):
    # drawable text object
    def __init__(self, pos, size, opts = {}):
        WObject.__init__(self)
        self.anchor = Vector2(0, 0)
        self.pos = pos
        self.size = size
        self.opts = {
            'spacing' : 0.2,        # space between characters relative to width
            'just-y'  : 'bottom',   # vertical justification (top|bottom|center)
            'just-x'  : 'left'      # horizontal justification (left|right|center)
        }
        self.opts.update(opts)
        self.string = ""
        self.did_update_string = True
        self._init_char_points()

    def set_string(self, string):
        # set the string to display
        self.string = string
        self.did_update_string = True

    def update(self, time, window):
        if self.did_update_string:
            self.did_update_string = False
            self.points = self._string_to_points(self.string)

    def _string_to_points(self, string):
        points = []
        index = 0
        for char in string:
            points = points + self._char_to_points(char, index)
            index += 1
        return points

    def _char_to_points(self, char, index):
        if char in self.char_points:
            points = self.to_points(self.char_points[char])
        else:
            points = []
        extra = self._find_extra(index)
        for point in points:
            point.update(point + extra)
        return points

    def _find_extra(self, index):
        extra = Vector2(0, 0)
        extra.x = (1 + self.opts['spacing']) * index
        if self.opts['just-x'] == 'center':
            extra.x = extra.x - self._find_width() / 2
        if self.opts['just-x'] == 'right':
            extra.x = extra.x - self._find_width()
        if self.opts['just-y'] == 'center':
            extra.y = extra.y - self._find_height() / 2
        if self.opts['just-y'] == 'top':
            extra.y = extra.y - self._find_height()
        return extra

    def _find_width(self):
        length = len(self.string)
        return length + self.opts['spacing'] * (length - 1)

    def _find_height(self):
        return 1

    def _init_char_points(self):
        # oh god why
        self.char_points = {
            'A': [0, 0, 0.5, 1, 0.5, 1, 1, 0, 0.25, 0.5, 0.75, 0.5],
            'B': [0, 0, 0, 1, 0, 1, 0.75, 1, 0.75, 1, 1, 0.75, 1, 0.75, 0.75, 0.5, 0.75, 
                    0.5, 1, 0.25, 1, 0.25, 0.75, 0, 0.75, 0, 0, 0, 0, 0.5, 0.75, 0.5],
            'C': [1, 0.25, 0.75, 0, 0.75, 0, 0.25, 0, 0.25, 0, 0, 0.25, 0, 0.25, 0, 
                    0.75, 0, 0.75, 0.25, 1, 0.25, 1, 0.75, 1, 0.75, 1, 1, 0.75],
            'D': [0, 0, 0, 1, 0, 1, 0.75, 1, 0.75, 1, 1, 0.75, 1, 0.75, 1, 0.25, 
                    1, 0.25, 0.75, 0, 0.75, 0, 0, 0],
            'E': [0, 1, 1, 1, 0, 0.5, 0.75, 0.5, 0, 0, 1, 0, 0, 0, 0, 1],
            'F': [0, 0, 0, 1, 0, 1, 1, 1, 0, 0.5, 0.75, 0.5],
            'G': [1, 0.75, 0.75, 1, 0.75, 1, 0.25, 1, 0.25, 1, 0, 0.75, 0, 0.75, 0, 0.25, 0, 0.25, 
                    0.25, 0, 0.25, 0, 0.75, 0, 0.75, 0, 1, 0.25, 1, 0.25, 1, 0.5, 1, 0.5, 0.5, 0.5],
            'H': [0, 0, 0, 1, 1, 0, 1, 1, 0, 0.5, 1, 0.5],
            'I': [0.25, 1, 0.75, 1, 0.25, 0, 0.75, 0, 0.5, 0, 0.5, 1],
            'J': [0, 0, 0.5, 0, 0.5, 0, 0.5, 1, 0, 1, 1, 1],
            'K': [0, 0, 0, 1, 0, 0.5, 1, 1, 0, 0.5, 1, 0],
            'L': [0, 0, 0, 1, 0, 0, 1, 0],
            'M': [0, 0, 0, 1, 0, 1, 0.5, 0.5, 0.5, 0.5, 1, 1, 1, 1, 1, 0],
            'N': [0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1],
            'O': [1, 0.75, 0.75, 1, 0.75, 1, 0.25, 1, 0.25, 1, 0, 0.75, 0, 0.75, 0, 0.25, 0, 0.25, 
                    0.25, 0, 0.25, 0, 0.75, 0, 0.75, 0, 1, 0.25, 1, 0.25, 1, 0.75],
            'P': [0, 0, 0, 1, 0, 1, 0.75, 1, 0.75, 1, 1, 0.75, 1, 0.75, 0.75, 0.5, 0.75, 0.5, 0, 0.5],
            'Q': [1, 0.75, 0.75, 1, 0.75, 1, 0.25, 1, 0.25, 1, 0, 0.75, 0, 0.75, 0, 0.25, 0, 0.25, 
                    0.25, 0, 0.25, 0, 0.75, 0, 0.75, 0, 1, 0.25, 1, 0.25, 1, 0.75, 0.75, 0.25, 1, 0],
            'R': [0, 0, 0, 1, 0, 1, 0.75, 1, 0.75, 1, 1, 0.75, 1, 0.75, 0.75, 0.5, 
                    0.75, 0.5, 0, 0.5, 0.75, 0.5, 1, 0],
            'S': [0, 0.25, 0.25, 0, 0.25, 0, 0.75, 0, 0.75, 0, 1, 0.25, 1, 0.25, 0.75, 0.5, 0.75, 0.5, 
                    0.25, 0.5, 0.25, 0.5, 0, 0.75, 0, 0.75, 0.25, 1, 0.25, 1, 0.75, 1, 0.75, 1, 1, 0.75],
            'T': [0, 1, 1, 1, 0.5, 1, 0.5, 0],
            'U': [0, 1, 0, 0.25, 0, 0.25, 0.25, 0, 0.25, 0, 0.75, 0, 0.75, 0, 1, 0.25, 1, 0.25, 1, 1],
            'V': [0, 1, 0.5, 0, 0.5, 0, 1, 1],
            'W': [0, 1, 0, 0, 0, 0, 0.5, 0.5, 0.5, 0.5, 1, 0, 1, 0, 1, 1],
            'X': [0, 0, 1, 1, 1, 0, 0, 1],
            'Y': [0, 1, 0.5, 0.5, 0.5, 0.5, 1, 1, 0.5, 0.5, 0.5, 0],
            'Z': [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0],
            '1': [0, 0.75, 0.5, 1, 0.5, 1, 0.5, 0, 0, 0, 1, 0],
            '2': [1, 0, 0, 0, 0, 0, 0.75, 0.5, 0.75, 0.5, 1, 0.75, 1, 0.75, 0.75, 
                    1, 0.75, 1, 0.25, 1, 0.25, 1, 0, 0.75],
            '3': [0, 0.75, 0.25, 1, 0.25, 1, 0.75, 1, 0.75, 1, 1, 0.75, 1, 0.75, 0.75, 0.5, 0.75, 
                    0.5, 1, 0.25, 1, 0.25, 0.75, 0, 0.75, 0, 0.25, 0, 0.25, 0, 0, 0.25, 0.25, 0.5, 0.75, 0.5],
            '4': [0.75, 0, 0.75, 1, 0.75, 1, 0, 0.25, 0, 0.25, 1, 0.25],
            '5': [1, 1, 0, 1, 0, 1, 0, 0.5, 0, 0.5, 0.75, 0.5, 0.75, 0.5, 1, 0.25, 
                    1, 0.25, 0.75, 0, 0.75, 0, 0, 0],
            '6': [1, 0.75, 0.75, 1, 0.75, 1, 0.25, 1, 0.25, 1, 0, 0.75, 0, 0.75, 0, 0.25, 0, 0.25, 0.25, 
                    0, 0.25, 0, 0.75, 0, 0.75, 0, 1, 0.25, 1, 0.25, 0.75, 0.5, 0.75, 0.5, 0, 0.5],
            '7': [0, 1, 1, 1, 1, 1, 0.25, 0],
            '8': [0, 0.75, 0.25, 1, 0.25, 1, 0.75, 1, 0.75, 1, 1, 0.75, 1, 0.75, 0.75, 0.5, 0.75, 
                    0.5, 1, 0.25, 1, 0.25, 0.75, 0, 0.75, 0, 0.25, 0, 0.25, 0, 0, 0.25, 
                    0, 0.25, 0.25, 0.5, 0.25, 0.5, 0, 0.75, 0.25, 0.5, 0.75, 0.5],
            '9': [0, 0.25, 0.25, 0, 0.25, 0, 0.75, 0, 0.75, 0, 1, 0.25, 1, 0.25, 1, 0.75, 1, 0.75, 
                    0.75, 1, 0.75, 1, 0.25, 1, 0.25, 1, 0, 0.75, 0, 0.75, 0.25, 0.5, 0.25, 0.5, 1, 0.5],
            '0': [1, 0.75, 0.75, 1, 0.75, 1, 0.25, 1, 0.25, 1, 0, 0.75, 0, 0.75, 0, 0.25, 0, 0.25, 
                    0.25, 0, 0.25, 0, 0.75, 0, 0.75, 0, 1, 0.25, 1, 0.25, 1, 0.75, 0.75, 1, 0.25, 0],
        }

