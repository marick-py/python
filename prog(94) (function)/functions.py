import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *

import pygame as pg

seed = rnd.random()
rnd.seed(seed)

pg.init()

y = lambda x: x

class Function:
    def __init__(self, parent, function, color) -> None:
        self.parent = parent
        self.function = function
        self.color = color

    def draw(self):
        for rx in range(1,self.parent.screen_size.x):
            x = rx - self.parent.screen_size.x / 2
            pre_y, y = -self.function(x-1) + self.parent.screen_size.y / 2, -self.function(x) + self.parent.screen_size.y / 2

            if not complex in [type(i) for i in V2(rx,y)() + V2(rx-1, pre_y)()]:
                pg.draw.line(self.parent.screen, self.color, V2(rx-1, pre_y)(), V2(rx,y)(), 1 if self != self.parent.nearest[0] else 10)

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.functions = [
            #Function(self, lambda x: x**2, (255,255,255))
            ]
    
    def get_y(self, rx, function):
        y = -function(rx - self.screen_size.x / 2) + self.screen_size.y / 2
        return y if type(y) != complex else np.inf

    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(0)
        self.clear()

        pg.draw.line(self.screen, (50,50,50), (self.screen_size/2*V2(0,1))(), (self.screen_size/V2(1,2))())
        pg.draw.line(self.screen, (50,50,50), (self.screen_size/2*V2(1,0))(), (self.screen_size/V2(2,1))())

        for function in self.functions: function.draw()
        if self.nearest != None: pg.draw.circle(self.screen, (255,0,0), self.nearest[1](), 10)

        pg.display.update()
    
    def frame(self):
        if ms.is_pressed("right"):
            self.functions.remove(self.nearest[0])
            while ms.is_pressed("right"): pass


        if key.is_pressed("n"):
            try:
                inp = input(">>> ").replace("=", "= lambda x:")
                if "+-" in inp:
                    inps = [inp.replace("+-", "+"), inp.replace("+-", "-")]
                else:
                    inps = [inp]
                for inp in inps:
                    exec("global y;" + inp)
                    self.functions.append(Function(self, y, (255,255,255)))
            except Exception as err:
                print(f"Error\n{err}")
        
        mouse = V2(info=pg.mouse.get_pos())
        func_ys = [(function, V2(mouse.x, self.get_y(mouse.x, function.function))) for function in self.functions]
        func_ys.sort(key=lambda y: abs(y[1].y - mouse.y))
        self.nearest = func_ys[0] if func_ys != [] else None

        self.draw()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

env = Env()

while not (env.quit or key.is_pressed("x")):
    env.frame()

    # y = (7500 * x +- (7500**2 * x**2 - 156250000 * x**2 + 25000 * 5000**2)**(1/2))/(12500)