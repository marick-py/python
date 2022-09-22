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
    def __init__(self, parent, position) -> None:
        self.position = position
        self.parent = parent
    
    def draw(self):
        pg.draw.circle(self.parent.screen, (255,127,0), self.position(), 10)

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.locked = None

        self.definition = 1000

        self.points = [
            Point(self, V2(self.screen_size.x / 100 * 25, self.screen_size.y / 100 * 25)),
            Point(self, V2(self.screen_size.x / 100 * 25, self.screen_size.y / 100 * 75)),
            Point(self, V2(self.screen_size.x - self.screen_size.x / 100 * 10, self.screen_size.y / 100 * 75))
        ]
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(0)
        self.clear()

#        print([[x[0](), x[1]()] for x in self.lines], pg.mouse.get_pos())
        for n,line in enumerate(self.lines):
            color = color_fade((255,127,0),(0,127,255), n, len(self.lines))
            pg.draw.line(self.screen, color, line[0](), line[1]())
            #pg.draw.circle(self.screen, (0,255,0), line[0](), 20, 2)
            #pg.draw.circle(self.screen, (255,255,0), line[1](), 15, 2)

        for i, point in enumerate(self.points[:-1]):
            pass#pg.draw.line(self.screen, (255,255,255), point.position(), self.points[i+1].position())

        for point in self.points: point.draw()

        pg.display.update()
    
    def input(self):
        mouse_pos = V2(info=pg.mouse.get_pos())
        if not key.is_pressed("ctrl"):
            if ms.is_pressed():
                if self.locked == None:
                    arg_min = np.argmin(list(map(lambda x: x.position.distance_to(mouse_pos), self.points)))
                    if self.points[arg_min].position.distance_to(mouse_pos) < 10:
                        self.points[arg_min].position = mouse_pos
                        self.locked = arg_min
                else:
                    self.points[self.locked].position = mouse_pos
            else:
                self.locked = None
            if ms.is_pressed("right"):
                arg_min = np.argmin(list(map(lambda x: x.position.distance_to(mouse_pos), self.points)))
                if self.points[arg_min].position.distance_to(mouse_pos) < 10:
                    self.points.pop(arg_min)
                    self.locked = None
        else:
            if ms.is_pressed():
                self.points.append(Point(self, mouse_pos))
                while ms.is_pressed(): pass

    def frame(self):
        self.input()

        if len(self.points) > 2:
            alines = [
                ( (point.position + (self.points[n+1].position - point.position) / self.definition * i),
                  (self.points[n+1].position + (self.points[n+2].position - self.points[n+1].position) / self.definition * (i+1)) ) for n, point in enumerate(self.points[:-2]) for i in range(self.definition)]
            self.lines = [([alines[0][0]], alines[0][0].inter_points(alines[0][1], [alines[1]]))] + [(alines[n][0].inter_points(alines[n][1], [alines[n+1]]), line[0].inter_points(line[1], [alines[n+2]])) for n, line in enumerate(alines[1:-1])]
            self.lines = self.lines + [(self.lines[-1][1], [alines[-1][1]])]
            self.lines = [(a[0],b) for a,b in [(a,b[0]) for a,b in self.lines if b != []] if a != []]
        else:
            self.lines = []

        self.draw()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

env = Env()

while not (env.quit or key.is_pressed("x")):
    env.frame()