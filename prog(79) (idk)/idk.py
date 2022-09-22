import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *

import pygame as pg

seed = rnd.random()
rnd.seed(seed)

pg.init()

class Point:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.spawn()
    
    def draw(self, closest=False):
        pg.draw.circle(self.parent.screen, (0,0,255), self.position(), self.radius, 2)
        if closest:
            pg.draw.line(self.parent.screen, (0,255,0), self.position(), self.position.point_from_degs(self.position.angle_to(V2(info=pg.mouse.get_pos())), self.radius)(), 2)
        else:
            pg.draw.line(self.parent.screen, (255,0,0), self.position(), self.position.point_from_degs(self.position.angle_to(V2(info=pg.mouse.get_pos())), self.radius)(), 2)
    
    def spawn(self):
        while 1:
            self.radius = rnd.random() * 499 + 1
            self.position = V2(0,0).randomize(V2z+self.parent.screen_size*0.1, self.parent.screen_size*0.9)
            can = True
            for point in self.parent.points:
                if self.position.distance_to(point.position) < point.radius + self.radius:
                    can = False
            if can:break

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.points = []
        for _ in range(100):
            self.points.append(Point(self))
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(0)
        self.clear()
        self.points.sort(key=lambda x: x.position.distance_to(V2(info=pg.mouse.get_pos())))
        for i, point in enumerate(self.points):
            point.draw(i==0)
        pg.display.update()
    
    def frame(self):
        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

env = Env()

while not (env.quit or key.is_pressed("x")):
    env.frame()