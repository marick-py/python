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
    def __init__(self, parent, position, g, color) -> None:
        self.position = position
        self.parent = parent
        self.g = g
        self.color = color
    
    def draw(self):
        pg.draw.circle(self.parent.screen, (0,0,255), self.position(), 10)
        mouse = V2(info=pg.mouse.get_pos())
        V0 = (mouse - self.position) * V2(1, -1)

        for i in range(1000):
            f = self.position.y - self.parent.floor + i
            pre_f = self.position.y - self.parent.floor + i - 1
            delta = V0.y**2 - 2 * self.g * f
            pre_delta = V0.y**2 - 2 * self.g * pre_f
            if delta > 0:
                max_x = (V0.y + (delta) ** (1/2)) / self.g * V0.x + self.position.x
                pre_max_x = (V0.y + (pre_delta) ** (1/2)) / self.g * V0.x + self.position.x
                min_x = (V0.y - (delta) ** (1/2)) / self.g * V0.x + self.position.x
                pre_min_x = (V0.y - (pre_delta) ** (1/2)) / self.g * V0.x + self.position.x

                if i == 0:
                    pg.draw.circle(self.parent.screen, (255,0,0), V2(max_x, self.parent.floor - i)(), 10)
                else:
                    if V0.y >= 0:
                        pg.draw.line(self.parent.screen, self.color, V2(max_x, self.parent.floor - i)(), V2(pre_max_x, self.parent.floor - i - 1)())
                    elif V0.y < 0:
                        if V2(max_x, self.parent.floor - i).y > self.position.y:
                            pg.draw.line(self.parent.screen, self.color, V2(max_x, self.parent.floor - i)(), V2(pre_max_x, self.parent.floor - i - 1)())

                    if V0.x > 0 and V2(min_x, self.parent.floor - i).x - self.position.x > 0:
                        pg.draw.line(self.parent.screen, self.color, V2(min_x, self.parent.floor - i)(), V2(pre_min_x, self.parent.floor - i - 1)())
                    elif V0.x < 0 and V2(min_x, self.parent.floor - i).x - self.position.x < 0:
                        pg.draw.line(self.parent.screen, self.color, V2(min_x, self.parent.floor - i)(), V2(pre_min_x, self.parent.floor - i - 1)())
            else:
                if V0.y > 0 or (V0.y < 0 and V2(max_x, self.parent.floor - i).y > self.position.y):
                    i -= 1
                    f = self.position.y - self.parent.floor + i
                    delta = V0.y**2 - 2 * self.g * f
                    max_x = (V0.y + (delta) ** (1/2)) / self.g * V0.x + self.position.x
                    min_x = (V0.y - (delta) ** (1/2)) / self.g * V0.x + self.position.x
                    pg.draw.line(self.parent.screen, self.color, V2(max_x, self.parent.floor - i)(), V2(min_x, self.parent.floor - i)())
                break

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.earth = Point(self, self.screen_size/2, 9.81, (0,255,0))
        self.moon = Point(self, self.screen_size/2, 1.62, (255,255,255))
        self.sun = Point(self, self.screen_size/2, 274, (255,255,0))
        self.floor = 700
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(0)
        self.clear()

        pg.draw.line(self.screen, (255,255,255), V2(0, self.floor)(), V2(self.screen_size.x, self.floor)(), 2)

        self.earth.draw()
        self.moon.draw()
        self.sun.draw()

        pg.display.update()
    
    def frame(self):
        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

env = Env()

while not (env.quit or key.is_pressed("x")):
    env.frame()