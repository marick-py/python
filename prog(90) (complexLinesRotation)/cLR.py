import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *

import pygame as pg

seed = rnd.random()
rnd.seed(seed)

pg.init()

class Car:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.position = self.parent.screen_size / 2
        self.size = V2(50, 100)
        self.rotation = 0

    def draw(self):
        self.rotation = self.position.angle_to(V2(info=pg.mouse.get_pos()))
        lines = get_lines(self.position, self.size, self.rotation, False)
        for line in lines: pg.draw.line(self.parent.screen, (255,127,0), line[0](), line[1](), 2)
        lines = get_lines(self.position, self.size, self.rotation, True)
        for line in lines: pg.draw.line(self.parent.screen, (255,127,0), line[0](), line[1](), 2)
        pg.draw.line(self.parent.screen, (0,0,255), self.position(), self.position.point_from_degs(self.rotation, 100)(),5)

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.car = Car(self)
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(0)
        self.clear()

        self.car.draw()

        pg.display.update()
    
    def frame(self):
        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

env = Env()

while not (env.quit or key.is_pressed("x")):
    env.frame()