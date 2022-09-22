import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *

import pygame as pg

seed = rnd.random()
rnd.seed(seed)

pg.init()

class Circle:
    def __init__(self, parent, radius, position) -> None:
        self.parent = parent
        self.radius = radius
        self.position = position
    
    def draw(self):
        pg.draw.circle(self.parent.screen, (255,255,255), self.position(), self.radius, 5)
        pg.draw.circle(self.parent.screen, (255,0,0), self.position(), 5)

        mouse_pos = V2(info=pg.mouse.get_pos())
        pg.draw.line(self.parent.screen, (0,0,255), mouse_pos(), self.position(), 1)
        ppos, mpos = self.find_tangent(mouse_pos)
        if str(np.nan) != str(ppos.x) and str(np.nan) != str(mpos.x):
            pg.draw.circle(self.parent.screen, (255,0,0), ppos(), 10)
            pg.draw.circle(self.parent.screen, (255,0,0), mpos(), 10)
            pg.draw.line(self.parent.screen, (0,0,255), mouse_pos(), ppos(), 1)
            pg.draw.line(self.parent.screen, (0,0,255), mouse_pos(), mpos(), 1)
    
    def find_tangent(self, mouse):
        dx = self.position.x - mouse.x
        dy = self.position.y - mouse.y
        dd = (dx * dx + dy * dy) ** (1/2)
        a = np.arcsin(self.radius / dd)
        b = np.arctan2(dy, dx)
        t = b - a
        ta = V2(self.radius * np.sin(t), self.radius * - np.cos(t)) + self.position
        t = b + a
        tb = V2(self.radius * - np.sin(t), self.radius * np.cos(t)) + self.position
        return ta, tb

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.circles = [
            Circle(self, 200, V2(300, 350)),
            Circle(self, 150, V2(500, 850)),
            Circle(self, 175, V2(1000, 290)),
            Circle(self, 125, V2(900, 650)),
            Circle(self, 160, V2(1700, 850))
            ]
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(0)
        self.clear()
        
        self.circles.sort(key= lambda x: x.position.distance_to(V2(info=pg.mouse.get_pos())))
        self.circles[-1].draw()
        
        pg.display.update()
    
    def frame(self):
        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

env = Env()

while not (env.quit or key.is_pressed("x")):
    env.frame()