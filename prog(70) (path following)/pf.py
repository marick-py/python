from timeit import timeit
import keyboard as key
import pygame as pg
import numpy as np
import mouse as ms
import time as tm
from e2D import *

pg.init()

class Map:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080) * 0.9
        self.screen = pg.display.set_mode(self.screen_size())
        self.clock = pg.time.Clock()

    def clear(self):
        self.screen.fill((0,0,0))

    def draw(self):
        self.clear()

        pg.display.update()


    def frame(self):
        self.clock.tick(60)

        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

mmap = Map()

while not (key.is_pressed("x") or mmap.quit):
    mmap.frame()