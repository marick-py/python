from itertools import permutations
import keyboard as key
import random as rnd
import pygame as pg
import numpy as np
import mouse as ms
from e2D import *

pg.init()

spawn_points = 3

class Game:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size())
        self.clock = pg.time.Clock()

        self.points = [V2z.copy().randomize(self.screen_size*0.1, self.screen_size*0.9) for _ in range(spawn_points)]
        self.possible = []
        self.curr = 0
        self.min_distance = sum([point.distance_to(self.points[n-len(self.points)+1]) for n, point in enumerate(self.points[:-1])])
        self.best = self.points.copy()
    
    def clear(self):
        self.screen.fill((0,0,0))

    def draw(self):
        self.clock.tick(0)
        self.clear()

        for n, point in enumerate(self.points[:-1]):
            pg.draw.circle(self.screen, (255,127,0), point(), 20)
            pg.draw.line(self.screen, (25,25,25), point(), self.points[n-len(self.points)+1](), 2)
        pg.draw.circle(self.screen, (255,127,0), self.points[n-len(self.points)+1](), 20)
        
        for n, point in enumerate(self.best[:-1]):
            pg.draw.line(self.screen, (255,0,0), point(), self.best[n-len(self.points)+1](), 2)


        pg.display.update()

    def frame(self):
        self.draw()

        #i,j = rnd.choices(self.points, k=2)
        #self.swap(self.points.index(i),self.points.index(j))
        #self.points = list(self.possible[self.curr])
        #self.curr += 1
        if not (tuple(self.points) in self.possible):
            print("new")
            self.possible = list(permutations(self.points))
            self.min_distance = sum([point.distance_to(self.points[n-len(self.points)+1]) for n, point in enumerate(self.points[:-1])])
            self.best = self.points.copy()
            
            for p in self.possible:
                self.points = list(p)

                tot_distance = sum([point.distance_to(self.points[n-len(self.points)+1]) for n, point in enumerate(self.points[:-1])])
                if tot_distance < self.min_distance:
                    self.min_distance = tot_distance
                    self.best = self.points.copy()

        if ms.is_pressed():
            self.points.append(V2(info=pg.mouse.get_pos()))
            while ms.is_pressed(): pass
        if ms.is_pressed("right") and len(self.points) > 2:
            mouse = V2(info=pg.mouse.get_pos())
            cpy = self.points.copy()
            cpy.sort(key=lambda x: x.distance_to(mouse))
            if cpy[0].distance_to(mouse) < 50:
                self.points.remove(cpy[0])
                while ms.is_pressed("right"): pass

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
    
    def swap(self, i, j):
        self.points[i], self.points[j] = self.points[j], self.points[i]


game = Game()

while not (game.quit or key.is_pressed("x")):
    game.frame()