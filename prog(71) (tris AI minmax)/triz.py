from timeit import timeit
import keyboard as key
import random as rnd
import pygame as pg
import mouse as ms
import numpy as np
from e2D import *
import time as tm
import os

os.system("cls")
print("\n"*25)
pg.init()

starting_p = ""
print("Starting player: [ai / me]")
while not starting_p in ["m", "a"]:
    starting_p = input(">>> ").replace(" ", "").lower()[0]

class Map:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.new_grid()
    
    def clear(self):
        self.screen.fill((0,0,0))

    def new_grid(self):
        self.grid = np.reshape([0]*9, (3,3))
        self.max_l = min((self.screen_size*0.9)())
        offset = (self.screen_size-self.max_l)/2
        self.lines = [
            [offset.copy()+V2(self.max_l,0)/3, offset.copy()+V2(self.max_l,0)/3+V2(0,self.max_l)],
            [offset.copy()+V2(self.max_l,0)/3*2, offset.copy()+V2(self.max_l,0)/3*2+V2(0,self.max_l)],
            [offset.copy()+V2(0,self.max_l)/3, offset.copy()+V2(0,self.max_l)/3+V2(self.max_l,0)],
            [offset.copy()+V2(0,self.max_l)/3*2, offset.copy()+V2(0,self.max_l)/3*2+V2(self.max_l,0)]
        ]
        self.blocks = [offset + self.max_l/6 + V2((self.max_l/3)*x,(self.max_l/3)*y) for x in range(3) for y in range(3)]
    
    def there_is_a_winner(self):
        for player in range(2):
            if [player+1]*3 in self.grid.tolist() or [player+1]*3 in np.rot90(self.grid.copy()).tolist():
                return player
            if self.grid[0,0] == self.grid[1,1] == self.grid[2,2] == player+1 or self.grid[0,2] == self.grid[1,1] == self.grid[2,0] == player+1:
                return player
            if not 0 in self.grid:
                return -1
        return None

    def draw(self):
        self.clock.tick(60)
        self.clear()
        ## draw map
        for line in self.lines:
            pg.draw.line(self.screen, (0,0,255), line[0](), line[1](), 5)

        ppoint, index, mpos = self.get_nearest_point_from_mouse()
        pg.draw.line(self.screen, (0,200,0), mpos(), ppoint(), 2) # debug

        for n,y in enumerate(self.grid):
            for m,x in enumerate(y):
                if x == 1:
                    pg.draw.line(self.screen, (255,127,0), (self.blocks[n*3+m] - self.max_l/6*0.7)(), (self.blocks[n*3+m] + self.max_l/6*0.7)(), 5)
                    pg.draw.line(self.screen, (255,127,0), V2(self.blocks[n*3+m].x + self.max_l/6*0.7, self.blocks[n*3+m].y - self.max_l/6*0.7)(), V2(self.blocks[n*3+m].x - self.max_l/6*0.7, self.blocks[n*3+m].y + self.max_l/6*0.7)(), 5)
                elif x == 2:
                    pg.draw.circle(self.screen, (255,127,0), self.blocks[n*3+m](), self.max_l/6*0.7, 5)


        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
    
    def get_nearest_point_from_mouse(self):
        mpos = V2(info=pg.mouse.get_pos())
        copy_of_points = self.blocks.copy()
        copy_of_points.sort(key=lambda x: mpos.distance_to(x))
        return copy_of_points[0], self.blocks.index(copy_of_points[0]), mpos

class Player:
    def __init__(self, id) -> None:
        self.id = id

class AI:
    def __init__(self, id) -> None:
        self.id = id

class Game:
    def __init__(self) -> None:
        self.player = Player(0)
        self.ai = AI(1)
        self.map = Map()
        self.turn = int(not starting_p == "m")
    
    def frame(self):
        self.map.draw()
        if ms.is_pressed() and self.player.id == self.turn:
            new_pos, new_block, mouse_pos = self.map.get_nearest_point_from_mouse()
            if new_pos.distance_to(mouse_pos, False) <= (2*(self.map.max_l/6)**2):
                y, x = divmod(new_block, 3)
                if self.map.grid[y, x] == 0:
                    self.map.grid[y, x] = self.player.id + 1
                    self.turn = int(not bool(self.turn))
        elif ms.is_pressed():
            new_pos, new_block, mouse_pos = self.map.get_nearest_point_from_mouse()
            if new_pos.distance_to(mouse_pos, False) <= (2*(self.map.max_l/6)**2):
                y, x = divmod(new_block, 3)
                if self.map.grid[y, x] == 0:
                    self.map.grid[y, x] = self.turn + 1
                    self.turn = int(not bool(self.turn))
        
        print(self.map.there_is_a_winner())

game = Game()

while not (game.map.quit or key.is_pressed("x")):
    game.frame()


