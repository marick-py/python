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
    def __init__(self, parent, position) -> None:
        self.parent = parent
        self.position = position
    
    def draw(self):
        pg.draw.circle(self.parent.screen, (255,127,0), self.position(), 10, 2)

    def frame(self):
        pass

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.points = []
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(60)
        self.clear()
        for point in self.points:
            point.draw()
        if key.is_pressed("space") and 1 < len(self.points):
            avg = self.avg([point.position for point in self.points])
            pg.draw.circle(self.screen, (255,0,0), avg(), avg.distance_to(self.points[0].position), 2)
        pg.display.update()
    
    def avg(self, listt):
        return sum(listt)/len(listt)

    def frame(self):
        for point in self.points:
            point.frame()
        self.draw()
        if ms.is_pressed():
            self.points.append(Point(self, V2(info=pg.mouse.get_pos())))
            while ms.is_pressed(): pass
        if ms.is_pressed("right") and len(self.points) > 0:
            mouse_p = V2(info=pg.mouse.get_pos())
            self.points.sort(key= lambda x: x.position.distance_to(mouse_p))
            if self.points[0].position.distance_to(mouse_p) < 10:
                self.points.pop(0)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

env = Env()

while not (env.quit or key.is_pressed("x")):
    env.frame()