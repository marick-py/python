import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *

import pygame as pg

seed = rnd.random()
rnd.seed(seed)

pg.init()

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.min = self.screen_size.x * 0.3
        self.max = self.screen_size.x * 0.7
        self.block = self.screen_size.x / 2
        self.rotation = 0
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(0)
        self.clear()

        pg.draw.line(self.screen, (127,127,127), (self.screen_size*V2(0,.5))(), (self.screen_size*V2(1,.5))(), 2)
        if abs(self.center_distance) < self.external_distance:
            pg.draw.line(self.screen, (255,0,0), V2(self.mouse.x, self.screen_size.y/2)(), V2(self.mouse.x + self.center_distance, self.screen_size.y/2)(), 10)
        else:
            if self.block < self.mouse.x:
                pg.draw.line(self.screen, (255,0,0), V2(self.block, self.screen_size.y/2)(), V2(self.min, self.screen_size.y/2)(), 10)
                pg.draw.line(self.screen, (255,0,0), V2(self.mouse.x, self.screen_size.y/2)(), V2(self.max, self.screen_size.y/2)(), 10)
            else:
                pg.draw.line(self.screen, (255,0,0), V2(self.block, self.screen_size.y/2)(), V2(self.max, self.screen_size.y/2)(), 10)
                pg.draw.line(self.screen, (255,0,0), V2(self.mouse.x, self.screen_size.y/2)(), V2(self.min, self.screen_size.y/2)(), 10)

        pg.draw.line(self.screen, (255,0,0), V2(self.block, self.screen_size.y/2)(), V2(self.block, self.screen_size.y/2).point_from_degs(self.rotation, 1000)(), 5)

        pg.draw.circle(self.screen, (0,255,0), V2(self.min, self.screen_size.y*.5)(), 5)
        pg.draw.circle(self.screen, (255,0,0), V2(self.max, self.screen_size.y*.5)(), 5)
        pg.draw.circle(self.screen, (0,0,255), V2(self.block, self.screen_size.y*.5)(), 15, 5)
        pg.draw.circle(self.screen, (255,127,0), V2(self.mouse.x, self.screen_size.y*.5)(), 10, 5)

        pg.display.update()
    
    def frame(self):
        self.mouse = V2(info=pg.mouse.get_pos())

        if ms.is_pressed("right"):
            self.block = self.mouse.x
            while not (self.min <= self.block < self.max):
                if self.block < self.min: self.block += self.max - self.min
                if self.block >= self.max: self.block -= self.max - self.min

        self.center_distance = self.block - self.mouse.x
        if self.block < self.mouse.x:
            self.external_distance = abs(self.block - self.min) + abs(self.mouse.x - self.max)
        else:
            self.external_distance = abs(self.block - self.max) + abs(self.mouse.x - self.min)
        
        self.rot1 = V2(self.block, self.screen_size.y/2).angle_to(self.mouse) - self.rotation
        if V2(self.block, self.screen_size.y/2).angle_to(self.mouse) < self.rotation:
            self.rot2 = abs(V2(self.block, self.screen_size.y/2).angle_to(self.mouse) - 1) + abs(self.rotation - 360)
        else:
            self.rot2 = abs(V2(self.block, self.screen_size.y/2).angle_to(self.mouse) - 360) + abs(self.rotation - 1)

        print(round(self.rot1), round(self.rot2))

        if abs(self.rot1) < self.rot2:
            self.rotation += self.rot1 / 100
        else:
            self.rotation += self.rot2 / 100

        self.rotation = divmod(self.rotation, 360)[1]

        self.draw()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

env = Env()

while not (env.quit or key.is_pressed("x")):
    env.frame()