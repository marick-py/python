import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *

import pygame as pg

seed = rnd.random()
rnd.seed(seed)

pg.init()

class Cell:
    def __init__(self, position, parent) -> None:
        self.position = position
        self.parent = parent
        self.walls = [True, True, True, True] # top, right, bottom, left
        self.visited = False
    
    def draw(self):
        scr = self.parent.screen
        border = self.parent.screen_border
        size = self.parent.cell_size
        WHITE = (255, 255, 255)
        BLUE = (0, 25, 75)
        if self is self.parent.current:
            COLOR = (255, 127, 0)
        elif self.visited:
            COLOR = BLUE
        else:
            COLOR = (0, 0, 0)
        pg.draw.rect(scr, COLOR, [self.parent.screen_border.x + self.position.x * self.parent.cell_size.x, self.parent.screen_border.y + self.position.y * self.parent.cell_size.y, self.parent.cell_size.x, self.parent.cell_size.y])
        pg.draw.line(scr, WHITE if self.walls[0] else BLUE, (border + self.position * size)(), (border + self.position * size + V2(size.x,0))(), 2) # top
        pg.draw.line(scr, WHITE if self.walls[1] else BLUE, (border + self.position * size + size)(), (border + self.position * size + V2(size.x,0))(), 2) # right
        pg.draw.line(scr, WHITE if self.walls[2] else BLUE, (border + self.position * size + size)(), (border + self.position * size + V2(0,size.y))(), 2) # bottom
        pg.draw.line(scr, WHITE if self.walls[3] else BLUE, (border + self.position * size)(), (border + self.position * size + V2(0,size.y))(), 2) # left
    
    def get_neighborn(self):
        neighbors = []
        x,y = self.position()
        cells = self.parent.cells

        can_dict = {"right":cells[y][x+1-len(cells[y])], "left":cells[y][x-1], "bottom":cells[y+1-len(cells)][x], "top":cells[y-1][x]}
        if x == 0: del can_dict["left"]
        if y == 0: del can_dict["top"]
        if x == self.parent.columns-1: del can_dict["right"]
        if y == self.parent.rows-1:    del can_dict["bottom"]

        for neighbor in list(can_dict.values()):
            if not neighbor.visited:
                neighbors.append(neighbor)
            
        if len(neighbors) > 0:
            return rnd.choice(neighbors)
        return None

class Game:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size())
        self.clock = pg.time.Clock()
        self.scale = 100
        self.columns = int(self.screen_size.x/self.scale)
        self.rows = int(self.screen_size.y/self.scale)
        self.cell_size = self.screen_size * 0.9 / V2(self.columns, self.rows)
        self.screen_border = self.screen_size * 0.05
        self.set_map()
    
    def set_map(self):
        self.cells = [[Cell(V2(x, y), self) for x in range(self.columns)] for y in range(self.rows)]
        self.current = self.cells[0][0]
        self.stack = []
        self.current.visited = True

    def clear(self):
        self.screen.fill((0,0,0))

    def draw(self):
        self.clock.tick(5)
        self.clear()

        for row in self.cells:
            for cell in row:
                cell.draw()
    
        for n, cell in enumerate(self.stack[1:]):
            pg.draw.line(self.screen, (255,0,0), (self.screen_border + self.stack[n].position * self.cell_size + self.cell_size / 2)(), (self.screen_border + cell.position * self.cell_size + self.cell_size / 2)())



        pg.display.update()

    def frame(self):
        self.draw()

        next = self.current.get_neighborn()
        if next != None:
            next.visited = True
            self.stack.append(self.current)
            self.remove_walls(next)
            self.current = next
        elif len(self.stack) > 0:
            self.current = self.stack.pop(-1)


        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
    
    def remove_walls(self, next):
        nx, ny = next.position()
        cx, cy = self.current.position()
        if cx - nx == 1: #next on left
            next.walls[1] = False
            self.current.walls[3] = False
        elif cx - nx == -1: #next on right
            next.walls[3] = False
            self.current.walls[1] = False
        elif cy - ny == 1: # next on top
            next.walls[2] = False
            self.current.walls[0] = False
        elif cy - ny == -1: #next on bottom
            next.walls[0] = False
            self.current.walls[2] = False


game = Game()

while not (key.is_pressed("x") or game.quit):
    game.frame()
