import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *

import pygame as pg

seed = rnd.random()
rnd.seed(seed)

pg.init()

dA = 1
dB = .5
feed = 0.055
k = 0.062

class Pixel:
    def __init__(self, position, a, b, parent) -> None:
        self.position = position
        self.a = a
        self.b = b
        self.parent = parent
    
    def draw(self):
        color = (self.a * 255 if 0 < self.a < 1 else (255 if self.a > 1 else 0), self.b * 255 if 0 < self.b < 1 else (255 if self.b > 1 else 0), 0)
        #pg.draw.circle(self.parent.screen, color, (self.position*self.parent.pixel_size + self.parent.pixel_size / 2)(), (min(self.parent.pixel_size()) / 2))
        pg.draw.rect(self.parent.screen, color, (self.position*self.parent.pixel_size)() + (self.parent.pixel_size+1)())
    
    def laplaceA(self):
        sumA = 0
        x,y = self.position()
        if x == 0 or y == 0: return 1
        if x == self.parent.pixels_count.x-1 or y == self.parent.pixels_count.y-1: return 1
        grid = self.parent.grid
        sumA += grid[y][x].a * -1
        sumA += grid[y][x-1].a * 0.2
        sumA += grid[y][x+1].a * 0.2
        sumA += grid[y-1][x].a * 0.2
        sumA += grid[y+1][x].a * 0.2
        sumA += grid[y-1][x-1].a * 0.05
        sumA += grid[y+1][x+1].a * 0.05
        sumA += grid[y-1][x+1].a * 0.05
        sumA += grid[y+1][x-1].a * 0.05
        return sumA
    
    def laplaceB(self):
        sumB = 0
        x,y = self.position()
        if x == 0 or y == 0: return 1
        if x == self.parent.pixels_count.x-1 or y == self.parent.pixels_count.y-1: return 1
        grid = self.parent.grid
        sumB += grid[y][x].b * -1
        sumB += grid[y][x-1].b * 0.2
        sumB += grid[y][x+1].b * 0.2
        sumB += grid[y-1][x].b * 0.2
        sumB += grid[y+1][x].b * 0.2
        sumB += grid[y-1][x-1].b * 0.05
        sumB += grid[y+1][x+1].b * 0.05
        sumB += grid[y-1][x+1].b * 0.05
        sumB += grid[y+1][x-1].b * 0.05
        return sumB
    
    def __mul__(self, n):
        if type(n) in (int, float):
            return Pixel(self.position, self.a * n, self.b * n, self.parent)
        elif isinstance(n, Vector2D):
            return Pixel(self.position, self.a * n.x, self.b * n.y, self.parent)
    
    def __add__(self, n):
        if type(n) in (int, float):
            return Pixel(self.position, self.a + n, self.b + n, self.parent)
        elif isinstance(n, Vector2D):
            return Pixel(self.position, self.a + n.x, self.b + n.y, self.parent)

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1080, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.resolution = 2 / 100
        self.pixel_size = self.screen_size * self.resolution
        self.pixels_count = self.screen_size / self.pixel_size
        self.setup()
    
    def setup(self):
        self.grid = [[Pixel(V2(x,y), rnd.random(), rnd.random(), self) for x in range(int(self.pixels_count.x))] for y in range(int(self.pixels_count.y))]
        self.next = self.grid.copy()
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(1)
        self.clear()

        for y in self.next:
            for pixel in y:
                pixel.draw()

        pg.display.update()
    
    def frame(self):
        self.draw()
        try:
            self.next = [[Pixel(
                vector.position,
                vector.a + dA + vector.laplaceA() - vector.a * vector.b**2 + feed * (1 - vector.a ),
                vector.b + dB + vector.laplaceB() + vector.a * vector.b**2 - (k + feed) * vector.b,
                self) for vector in y] for y in self.grid]
        except:
            print()
        self.grid = self.next

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
        if key.is_pressed("space"): print(self.clock.get_fps())

env = Env()

while not (env.quit or key.is_pressed("x")):
    env.frame()