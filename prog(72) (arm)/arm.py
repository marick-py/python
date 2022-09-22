import keyboard as key
import random as rnd
import pygame as pg
import numpy as np
import mouse as ms
from e2D import *

pg.init()

line_softness = 1
line_lenght = 1
line_count = 1000

class Line:
    def __init__(self, startP, endP) -> None:
        self.start = startP
        self.end = endP
        self.len = self.start.distance_to(self.end)

class Game:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.base = V2(1920, 1080) / V2(2,1)  

        self.lines = [Line(self.screen_size / V2(2,1), self.screen_size / V2(2,1) - V2(0, line_lenght)) for _ in range(line_count)]
        #self.lines = [Line(V2z.copy(), V2(i, 0)) for i in range(0,line_count,5)][::-1]

    def clear(self):
        self.screen.fill((0,0,0))

    def draw(self):
        self.clock.tick(144)

        self.clear()

        sc = (255, 127, 0)
        fc = (0, 127, 255)

        for n,line in enumerate(self.lines):
            color = tuple( (sc[i]-fc[i]) / len(self.lines) * (len(self.lines) - n) + fc[i] for i in range(3))
            pg.draw.line(self.screen, color, line.start(), line.end(), 4)
        
        pg.display.update()


    def phys(self):
        head = self.lines[0]
        mouse = V2(info=pg.mouse.get_pos())
        new_end_deg = head.start.angle_to(mouse)
        head.end = head.start.point_from_degs(new_end_deg, head.len)
        head.start += ((mouse - head.start) - (head.end - head.start)) / 10

        for n, line in enumerate(self.lines[1:]):
            pre_line = self.lines[n] # not -1 cuz enum is without head
            new_end_deg = line.start.angle_to(pre_line.start)
            line.end = line.start.point_from_degs(new_end_deg, line.len)
            line.start += ((pre_line.start - line.start) - (line.end - line.start)) / line_softness

        self.lines[-1].start = self.base

        for n in range(1, len(self.lines)):
            self.lines[-n-1].start = self.lines[-n].end

    def frame(self):

        self.phys()
        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
    
        

game = Game()

while not (game.quit or key.is_pressed("x")):
    game.frame()