from perlin_noise import PerlinNoise
import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *

import pygame as pg

seed = rnd.random()
rnd.seed(seed)
noise = PerlinNoise(seed=seed)

pg.init()

class Block:
    def __init__(self, parent, position) -> None:
        self.parent = parent
        self.position = position
        self.size = self.parent.size
    
    def draw(self):
        c_noise = noise(( V2(1,1) / (self.parent.screen_size/self.parent.size).floor() * self.position + 2)() + [self.parent.deep])
        #color = (1 + c_noise) * 255 / 2
        if c_noise > self.parent.max_noise: self.parent.max_noise = c_noise
        if c_noise < self.parent.min_noise: self.parent.min_noise = c_noise
        self.color = (-self.parent.min_noise + c_noise) * 255 / (abs(self.parent.min_noise) + abs(self.parent.max_noise))
        pg.draw.rect(self.parent.screen, [self.color]*3, (self.parent.offset + self.position * self.size)() + self.size())
        pos = self.parent.offset + self.position * self.size + self.size / 2
        pg.draw.line(self.parent.screen, (255,127,0), pos(), pos.point_from_degs(360 / 255 * self.color, min(self.size()))())

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.size = V2(100, 100)
        self.offset = (self.screen_size % self.size) / 2
        self.blocks = [Block(self, V2(x,y)) for y in range(int(np.floor(self.screen_size.y/self.size.y))) for x in range(int(np.floor(self.screen_size.x/self.size.x)))]
        self.min_noise = np.inf
        self.max_noise = 1
        self.deep = 1
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(0)
        self.clear()

        for block in self.blocks: block.draw()
        #pg.draw.circle(self.screen, (255,0,0), V2z(), 10) 
        #pg.draw.circle(self.screen, (0,255,0), pg.mouse.get_pos(), 10)
        #pg.draw.line(self.screen, (255,127,0), pg.mouse.get_pos(), V2z(), 2)
        #points = [avg_position(*[(self.offset + block.position * block.size + block.size / 2).point_from_degs(360 / 255 * block.color, min(block.size())) for block in self.blocks[line*int(np.floor(self.screen_size.x/self.size.x)):line*int(np.floor(self.screen_size.x/self.size.x))+int(np.floor(self.screen_size.x/self.size.x))]]) for line in range(int(np.floor(self.screen_size.y/self.size.y)))]
        #for i, point in enumerate(points[1:]):
        #    pg.draw.line(self.screen, (0,0,255), point(), points[i](), 5)
        points = [(self.offset + block.position * block.size + block.size / 2).point_from_degs(360 / 255 * block.color, min(block.size())) for block in self.blocks]
        for y in range(int(np.floor(self.screen_size.y/self.size.y))-1):
            for x in range(int(np.floor(self.screen_size.x/self.size.x))-1):
                pg.draw.line(self.screen, (0,255,0), points[x+y*int(np.floor(self.screen_size.x/self.size.x))](), points[(x+1)+y*int(np.floor(self.screen_size.x/self.size.x))](), 2)
                pg.draw.line(self.screen, (0,255,0), points[x+y*int(np.floor(self.screen_size.x/self.size.x))](), points[x+(y+1)*int(np.floor(self.screen_size.x/self.size.x))](), 2)
                color = color_fade((255,0,0), (0,0,255), x+y*int(np.floor(self.screen_size.x/self.size.x)), len(points))
                pg.draw.circle(self.screen, color, points[x+y*int(np.floor(self.screen_size.x/self.size.x))](), 5)

        pg.display.update()
    
    def frame(self):
        self.draw()

        #self.size = ((self.screen_size / 2 - V2(info=pg.mouse.get_pos())).abs() * 3).round() + 1
        #self.deep = V2z.distance_to(V2(info=pg.mouse.get_pos())) / 100
        self.deep += V2z.distance_to(V2(info=pg.mouse.get_pos())) / 10000
        #self.offset = (self.screen_size % self.size) / 2
        #self.blocks = [Block(self, V2(x,y)) for x in range(int(np.floor(self.screen_size.x/self.size.x))) for y in range(int(np.floor(self.screen_size.y/self.size.y)))]


        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

env = Env()

while not (env.quit or key.is_pressed("x")):
    env.frame()