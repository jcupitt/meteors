import random
import math

import pyglet
from pyglet.gl import *
from pyglet.window import key

from vector import *
from world import *
from enums import *
from objects import *

class Game():
    # game logic/event handling class
    def __init__(self, window):
        self._init_window(window)
        self._init_opengl()
        self._init_collider()
        
        # list to hold all game objects
        self.items = []

        # set the initial score and level
        self.score = 0
        self.level = 1

        # set the initial state (start screen)
        self._init_start()

    # misc initializers

    def _init_window(self, window):
        self.window = window
        self.window.clear()
        self.window.flip()
        self.window.set_visible(True)

    def _init_opengl(self):
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        self._aa = True

    def _toggle_aa(self):
        if self._aa:
            glDisable(GL_LINE_SMOOTH)
            glDisable(GL_BLEND)
            self._aa = False
        else:
            glEnable(GL_BLEND)
            glEnable(GL_LINE_SMOOTH)
            self._aa = True

    def _init_collider(self):
        self.collider = Collider()
        self.collider.register_methods(
            self._cd_ship_meteor,
            self._ch_ship_meteor,
            'Ship', 'Meteor1')
        self.collider.register_methods(
            self._cd_ship_meteor,
            self._ch_ship_meteor,
            'Ship', 'Meteor2')
        self.collider.register_methods(
            self._cd_ship_meteor,
            self._ch_ship_meteor,
            'Ship', 'Meteor3')
        self.collider.register_methods(
            self._cd_bullet_meteor,
            self._ch_bullet_meteor1,
            'Bullet', 'Meteor1')
        self.collider.register_methods(
            self._cd_bullet_meteor,
            self._ch_bullet_meteor2,
            'Bullet', 'Meteor2')
        self.collider.register_methods(
            self._cd_bullet_meteor,
            self._ch_bullet_meteor3,
            'Bullet', 'Meteor3')

    # state initializers
    
    def _init_start(self):
        # initialize the start screen
        self.state = STATE.start
        self.remove_all_items()
        (winx, winy) = self.window.get_size()
        s1 = Font(
            Vector2(winx / 2, winy / 2), 
            Vector2(20, 30), 
            {'just-x' : 'center',
             'just-y' : 'center'})
        s1.set_string('DIE TO DIE (O PERCENT CHANCE OF HAPPENING) ')
        s1.color = [0.5, 0.5, 1]
        self.add_item(s1)
        s2 = Font(
            Vector2(winx / 2, winy / 2 - 40), 
            Vector2(10, 15), 
            {'just-x' : 'center',
             'just-y' : 'center',
             'spacing': 0.3})
        s2.set_string('ARROW KEYS TO MOVE')
        s2.color = [0.7, 0.7, 0.7]
        self.add_item(s2)
        s2 = Font(
            Vector2(winx / 2, winy / 2 - 63), 
            Vector2(10, 15), 
            {'just-x' : 'center',
             'just-y' : 'center',
             'spacing': 0.3})
        s2.set_string('SPACE OR S TO SHOOT')
        s2.color = [0.7, 0.7, 0.7]
        self.add_item(s2)

    def _init_level(self):
        # initialize the level transition screen
        self.level = self.level + 1
        self.state = STATE.level
        self.remove_all_items()
        (winx, winy) = self.window.get_size()
        s = Font(
            Vector2(winx / 2, winy / 2), 
            Vector2(20, 30), 
            {'just-x' : 'center',
             'just-y' : 'center'})
        s.set_string('LEVEL %d' % self.level)
        s.color = [0.5, 0.5, 1]
        self.add_item(s)

    def _init_play(self):
        # initialize the game
        self.remove_all_items()
        self.meteors = []
        self.bullet = None
        (winx, winy) = self.window.get_size()
        self.score_text = Font(
            Vector2(5, winy - 5), 
            Vector2(10, 15), 
            {'just-x' : 'left',
             'just-y' : 'top'})
        self.add_item(self.score_text)
        self.add_to_score(0)
        self.state = STATE.play
        self.add_ship()
        self.add_meteor1()

    def _init_game_over(self):
        # initialize the game over screen
        self.level = 1
        self.score = 0
        self.remove_all_items()
        self.state = STATE.game_over
        (winx, winy) = self.window.get_size()
        s = Font(
            Vector2(winx / 2, winy / 2), 
            Vector2(20, 30), 
            {'just-x' : 'center',
             'just-y' : 'center'})
        s.set_string('MY BOTTOM GOES HBBFGBFHBGBFHGB DADDY"S REALLY ')
        s.color = [1, 0, 0]
        self.add_item(s)
        self.add_item(self.score_text)

    # helpers

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)
        if item == self.bullet:
            self.bullet = None

    def remove_all_items(self):
        self.items = []

    def add_to_score(self, num):
        self.score = self.score + num * self.level
        self.score_text.set_string("SCORE %d" % self.score)

    # game object initializers

    def add_ship(self):
        (winx, winy) = self.window.get_size()
        pos = Vector2(winx / 2, winy / 2)
        self.ship = Ship(pos)
        self.add_item(self.ship)

    def add_bullet(self):
        if self.bullet == None:
            pos = self.ship.pos + self.ship.deg_to_vel(self.ship.deg) * self.ship.size.y / 2
            self.bullet = Bullet(pos, self.ship.deg)
            self.add_item(self.bullet)

            pos = self.ship.pos + self.ship.deg_to_vel(self.ship.deg) * self.ship.size.y * 2
            self.bullet = Bullet(pos, self.ship.deg)
            self.add_item(self.bullet)

    def add_meteor1(self):
        # adds large meteors in random locations, with random directions.
        # makes sure it's far enough away from the ship, and from each other
        (winx, winy) = self.window.get_size()
        count = self.level
        last_poses = []
        for i in range(count):
            search = True
            while search:
                pos = Vector2(random.uniform(0, winx), random.uniform(0, winy))
                search = False
                for last_pos in last_poses:
                    if abs(pos - last_pos) < 20000:
                        search = True
                        break 
                if abs(pos - self.ship.pos) < 20000:
                    search = True
            last_poses.append(pos)
            deg = random.uniform(0, 360)
            m = Meteor1(pos, deg)
            self.add_item(m)
            self.meteors.append(m)

    def add_meteor2(self, pos):
        # adds meteor2s where a meteor1 was exploded (pos)
        # uses random directions, but at least 0.2 * (360/count) degrees apart
        count = 3
        min_separation = 0.2 * (360 / count)
        last_degs = []
        for i in range(count):
            search = True
            while search:
                deg = random.uniform(0, 360)
                search = False
                for last_deg in last_degs:
                    if abs(deg - last_deg) < min_separation:
                        search = True
                        break
            last_degs.append(deg)
            m = Meteor2(pos, deg)
            self.add_item(m)
            self.meteors.append(m)

    def add_meteor3(self, pos):
        # adds meteor2s where an meteor1 was exploded (pos)
        # uses random directions, but at least 0.2 * (360/count) degrees apart
        count = 3
        min_separation = 0.2 * (360 / count)
        last_degs = []
        for i in range(count):
            search = True
            while search:
                deg = random.uniform(0, 360)
                search = False
                for last_deg in last_degs:
                    if abs(deg - last_deg) < min_separation:
                        search = True
                        break
            last_degs.append(deg)
            m = Meteor3(pos, deg)
            self.add_item(m)
            self.meteors.append(m)

    # keyboard event handler

    def on_key(self, symbol, modifiers, press):
        if symbol == key.ENTER and press:
            if self.state == STATE.start:
                self._init_play()
            elif self.state == STATE.game_over:
                self._init_start()
            elif self.state == STATE.level:
                self._init_play()
        elif symbol == key.RIGHT:
            if self.state == STATE.play:
                self.ship.turn(TURN.right, press) 
        elif symbol == key.LEFT:
            if self.state == STATE.play:
                self.ship.turn(TURN.left, press) 
        elif symbol == key.UP:
            if self.state == STATE.play:
                self.ship.thrust(THRUST.forward, press) 
        elif symbol == key.DOWN:
            if self.state == STATE.play:
                self.ship.thrust(THRUST.back, press)
        elif (symbol == key.SPACE or symbol == key.S) and press:
            if self.state == STATE.play:
                self.add_bullet()
        elif symbol == key.A and press:
            self._toggle_aa()

    # render event handler

    def draw(self):
        self.window.clear()
        for item in self.items:
            item.draw()

    # update event handler

    def update(self, frame_time):
        # update game objects
        for item in self.items:
            if item.remove:
                self.remove_item(item)
                if item == self.ship:
                    self._init_game_over()
            else:
                item.update(frame_time, self.window)
        # check for collisions
        if self.state == STATE.play:
            for item1 in self.items:
                for item2 in self.items:
                    if item1 != item2:
                        if self.collider.collide(item1, item2):
                            self.collider.handle(item1, item2)

    # collision detection methods (these could live anywhere really since they are purely functional)

    def _cd_ship_meteor(self, ship, meteor):
        ship_points = ship.get_all_points_transformed()
        for ship_point_index in range(len(ship_points)):
            ship_point = ship_points[ship_point_index]
            if meteor.bounding_circle().inside(ship_point):
                ship_point_old = ship.get_point_transformed(ship_point_index, 2)
                line1 = Line(ship_point_old, ship_point)
                for line2 in meteor.get_lines():
                    if line2.intersect(line1):
                        return True
        return False

    def _cd_bullet_meteor(self, bullet, meteor):
        if meteor.bounding_circle().inside(bullet.pos):
            line1 = Line(bullet.last_pos[1], bullet.pos)
            for line2 in meteor.get_lines():
                if line1.intersect(line2):
                    return True
        return False

    # collision handling methods (these have to be here since they affect the game state)

    def _ch_ship_meteor(self, ship, meteor):
        ship.hit()

    def _ch_bullet_meteor1(self, bullet, meteor):
        meteor.hit()
        bullet.hit()
        if meteor.remove:
            self.meteors.remove(meteor)
            self.add_to_score(25)
            self.add_meteor2(meteor.pos)

    def _ch_bullet_meteor2(self, bullet, meteor):
        meteor.hit()
        bullet.hit()
        if meteor.remove:
            self.meteors.remove(meteor)
            self.add_to_score(50)
            self.add_meteor3(meteor.pos)

    def _ch_bullet_meteor3(self, bullet, meteor):
        meteor.hit()
        bullet.hit()
        if meteor.remove:
            self.meteors.remove(meteor)
            self.add_to_score(100)
            if len(self.meteors) == 0:
                self._init_level()
