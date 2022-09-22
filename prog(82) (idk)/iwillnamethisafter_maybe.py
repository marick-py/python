import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *

import pygame as pg

seed = rnd.random()
rnd.seed(seed)

pg.init()

n_of_points = 10

class X:
    def __init__(self, parent, index, pre_parent) -> None:
        self.parent = parent
        self.position = self.parent.screen_size / 2
        self.index = index
        self.pre_parent = pre_parent
        self.tail = self.position
        self.scale = 10*(n_of_points-index)
    
    def draw(self):
        mouse_pos = V2(info=pg.mouse.get_pos()) if self.index == 0 else self.pre_parent.tail
        v1, v2, v3, v4 = mouse_pos, mouse_pos.mid_point_to(self.position).point_from_degs(mouse_pos.angle_to(self.position)+90, self.scale), self.position, mouse_pos.mid_point_to(self.position).point_from_degs(mouse_pos.angle_to(self.position)-90, self.scale)
        self.tail = v3
        for point in [v1, v2, v3, v4]:
            if point.y > self.parent.screen_size.y: point.y = self.parent.screen_size.y - 1
            if point.x > self.parent.screen_size.x: point.x = self.parent.screen_size.x - 1
            if point.x < 0: point.x = 0
            if point.y < 0: point.y = 0

        #pg.draw.line(self.parent.screen, (63,31,0), v1(), v3(), 1)
        #pg.draw.line(self.parent.screen, (63,31,0), v2(), v4(), 1)
        color = color_fade((255,255,255),(0,0,0), self.index, n_of_points)
        pg.draw.line(self.parent.screen, color, v1(), v2(), 2)
        pg.draw.line(self.parent.screen, color, v2(), v3(), 2)
        pg.draw.line(self.parent.screen, color, v3(), v4(), 2)
        pg.draw.line(self.parent.screen, color, v4(), v1(), 2)

    def frame(self):
        mouse_pos = V2(info=pg.mouse.get_pos()) if self.index == 0 else self.pre_parent.tail
        self.position = self.position.point_from_degs(self.position.angle_to(mouse_pos), (self.position.distance_to(mouse_pos) - self.scale*2) / 50 )

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(2560, 1440)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.xs = []
        for x in range(n_of_points):
            self.xs.append(X(self, x, self.xs[x-1] if x != 0 else None))
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(0)
        self.clear()
        for x in self.xs: x.draw()

        pg.display.update()
    
    def frame(self):
        for x in self.xs: x.frame()
        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

env = Env()

while not (env.quit or key.is_pressed("x")):
    env.frame()