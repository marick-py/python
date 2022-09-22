import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *

import pygame as pg

seed = rnd.random()
rnd.seed(seed)

pg.init()

class Mouse:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.max_memory = 50
        self.memory = []
        self.position = V2(info=pg.mouse.get_pos())
        self.point = Point(self)
    
    def draw(self):
        for point in self.memory:
            pg.draw.circle(self.parent.screen, (10,10,10), point(), 2)
        #pg.draw.line(self.parent.screen, (255/6, 127/6, 255/6), avg_position(*self.memory)(), self.position(), 2)
        #pg.draw.line(self.parent.screen, (255/3, 127/3, 255/3), self.prevision_point(), self.position(), 4)
        #pg.draw.circle(self.parent.screen, (255,127,0), self.position(), 4)
        #pg.draw.circle(self.parent.screen, (0,127,255), avg_position(*self.memory)(), 4)
        #pg.draw.circle(self.parent.screen, (0,255,0), self.prevision_point(), 4)
        self.point.draw()

    def frame(self):
        self.memory.append(self.position.copy())

        self.position = V2(info=pg.mouse.get_pos())

        avgP = avg_position(*self.memory)
        self.prevision_point = self.position.point_from_degs(divmod(self.position.angle_to(avgP) + 180, 360)[1], self.position.distance_to(avgP))

        self.point.frame()
        while len(self.memory) > self.max_memory: self.memory.pop(0)

class Point:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.position = self.parent.parent.screen_size / 2
        self.speed = 25
    
    def draw(self):
        pg.draw.circle(self.parent.parent.screen, (255,0,0), self.position(), 10, 4)
    
    def frame(self):
        self.position = self.position.point_from_degs(self.position.angle_to(self.parent.prevision_point), self.position.distance_to(self.parent.prevision_point) / self.speed)

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.mouse = Mouse(self)
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(0)
        self.clear()

        self.mouse.draw()

        pg.display.update()
    
    def frame(self):
        self.mouse.frame()

        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

env = Env()

while not (env.quit or key.is_pressed("x")):
    env.frame()