import keyboard as key
import random as rnd
import pygame as pg
import mouse as ms
import numpy as np
from e2D import *

pg.init()

class Map:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = (Vector2D(1920, 1080)*0.75).round()
        self.screen = pg.display.set_mode(self.screen_size())
        self.clock = pg.time.Clock()
    
    def generate_random_points(self, n):
        border = self.screen_size*.2
        self.spoints = [Vector2D(border.x+(self.screen_size.x-2*border.x)*rnd.random(), border.y+(self.screen_size.y-2*border.y)*rnd.random()) for _ in range(n)]
        # self.points.sort(key=lambda x: x.x)
        # self.left_most = self.current_vrtx = self.points[0]
        # self.next_vrtx = self.points[1]
        # self.index = 2
        # self.next_index = -1
        # self.hull = [self.current_vrtx]

    def clear(self):
        self.screen.fill(0)

    def draw(self):
        self.clear()
        sc = (255, 127, 0)
        fc = (0, 127, 255)
        pg.draw.line(self.screen, (255,255,255), self.current_vrtx(), self.next_vrtx(), 2)
        pg.draw.line(self.screen, (255,255,255), self.current_vrtx(), self.points[self.index](), 2)
        for n, p in enumerate(self.hull):
            pg.draw.line(self.screen, (0,0,255), self.hull[n-1](), p(), 4)
        for n, p in enumerate(self.points):
            # if p == self.current_vrtx:
            #     color = (0,255,0)
            # elif p == self.next_vrtx:
            #     color = (255,0,255)
            # elif p == self.left_most:
            #     color = (127, 127, 217)
            #else:
            color = tuple( (sc[i]-fc[i]) / len(self.points) * (len(self.points) - n) + fc[i] for i in range(3))
            pg.draw.circle(self.screen, color, p(), 5 if p in [self.left_most, self.next_vrtx, self.current_vrtx] else 5)
        pg.display.update()

    def frame_hull(self, n):
        self.clock.tick(60)
        self.points = self.spoints + [Vector2D(info=pg.mouse.get_pos())]
        self.points.sort(key=lambda x: x.x)
        self.left_most = self.current_vrtx = self.points[0]
        self.next_vrtx = self.points[1]
        self.index = 2
        self.next_index = -1
        self.hull = [self.current_vrtx]
        end = False
        while not end:
            a = self.next_vrtx - self.current_vrtx
            b = self.points[self.index] - self.current_vrtx
            if np.cross(a(),b()) < 0:
                self.next_vrtx = self.points[self.index]
                self.next_index = self.index
            self.index += 1
            if self.index == len(self.points):
                self.hull.append(self.next_vrtx)
                self.current_vrtx = self.next_vrtx
                self.index = 0
                if self.next_vrtx == self.left_most:
                    end = True
                self.next_vrtx = self.left_most
        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

    def frame(self):
        self.clock.tick(0)

        a = self.next_vrtx - self.current_vrtx
        b = self.points[self.index] - self.current_vrtx
        if np.cross(a(),b()) < 0:
            self.next_vrtx = self.points[self.index]
            self.next_index = self.index
        self.index += 1
        if self.index == len(self.points):
            if not self.next_vrtx == self.left_most:    
                self.hull.append(self.next_vrtx)
                self.current_vrtx = self.next_vrtx
                self.index = 0
                self.next_vrtx = self.left_most
        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

mmap = Map()
mmap.generate_random_points(4)

while not (key.is_pressed("x") or  mmap.quit):
    mmap.frame_hull(10)