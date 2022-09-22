import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *

import pygame as pg

seed = rnd.random()
rnd.seed(seed)
print(seed)

pg.init()

n_of_lines = 500

class Line:
    def __init__(self, parent, pre_parent, lenght, index) -> None:
        self.parent = parent
        self.pre_parent = pre_parent
        self.index = index
        self.rotation = 0
        self.position = (self.pre_parent.position.point_from_degs(self.pre_parent.rotation, self.pre_parent.length) if self.pre_parent != None else self.parent.screen_size/2)
        self.length = lenght
        self.speed = rnd.random()*2-1
    
    def frame(self):
        self.rotation += self.speed
        self.position = (self.pre_parent.position.point_from_degs(self.pre_parent.rotation, self.pre_parent.length) if self.pre_parent != None else self.parent.screen_size/2)
        if self.index == n_of_lines-1:
            self.parent.points.append(self.position.point_from_degs(self.rotation, self.length))

    def draw(self):
        end = self.position.point_from_degs(self.rotation, self.length)
        #pg.draw.circle(self.parent.screen, (0, 0, 255), self.position(), 2)
        #pg.draw.circle(self.parent.screen, (0, 0, 255), end(), 2)
        pg.draw.line(self.parent.screen, (255, 125, 0), self.position(), end())

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.lines = []
        self.points = []
        for i in range(n_of_lines):
            self.lines.append(Line(self, self.lines[-1] if len(self.lines) else None, (n_of_lines-i)*(3*10/n_of_lines), i))
        self.distances = []
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(0)
        self.clear()

        for line in self.lines:
            line.draw()
        for i, point in enumerate(self.points):
            pg.draw.circle(self.screen, (0, 0, 255/len(self.points)*i), point(), 2)
        if len(self.distances):
            pg.draw.circle(self.screen, (0, 255, 0), (self.screen_size/2)(), sum(self.distances)/len(self.distances), 2)
        pg.display.update()
    
    def frame(self):
        for line in self.lines:
            line.frame()
        self.distances.append(self.points[-1].distance_to(self.screen_size/2))
        while len(self.distances) > 100: self.distances.pop(0)
        while len(self.points) > 1000: self.points.pop(0)
        
        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

env = Env()

while not (env.quit or key.is_pressed("x")):
    env.frame()