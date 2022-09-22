from datetime import datetime
import itertools
import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *
from QT import *
import os

seed = rnd.random()
rnd.seed(seed)

inp = None
print("Start with a QTable: [file/new]")
while inp not in ["n", "f", "file", "new"]:
    inp = input(">>> ").replace(" ", "").lower()
open_file = True if inp in ["f", "file"] else False
folder_name = f"pickles"
main_folder_dir = "\\".join(__file__.split("\\")[:-1])
folder = f"{main_folder_dir}\\{folder_name}\\"
if not folder_name in os.listdir(main_folder_dir):
    os.mkdir(folder)
inp = None
print("Select Mode: [learn/show/debug]")
while inp not in ["l", "s", "d"]:
    inp = input(">>> ").replace(" ", "").lower()
learn_mode = inp

if learn_mode in ["s", "d"]:
    import pygame as pg
    pg.init()
    pg.font.init()
    my_font = pg.font.SysFont('Comic Sans MS', 16)

commands = {i:l for i, l in enumerate([
    "w",
    "d",
    "s",
    "a",
])}

key_commands = {ch:[] for ch in "wasd"}
for c in commands:
    for ch in commands[c]:
        key_commands[ch].append(c)

class Block:
    def __init__(self, parent, position, is_start=False, is_end=False) -> None:
        self.parent = parent
        self.position = position
        self.is_start = is_start
        self.is_end = is_end
        self.size = V2(100, 100)
    
    def draw(self):
        offset = V2(600, 100)
        color = (255,0,0) if self.is_start else ((0,0,255) if self.is_end else (255,255,255))
        pg.draw.rect(self.parent.screen, color, (self.position * self.size + offset)() + self.size())
        if self.position() == self.parent.current():
            pg.draw.rect(self.parent.screen, (255,127,0), (self.position * self.size + offset + self.size * 0.2)() + (self.size * 0.6)())
    
    def draw_text(self):
        offset = V2(600, 100)
        if str(self.position) in qt.qt:
            for action in qt.qt[str(self.position)]:
                if action == 0: new_pos = self.position + V2(0, -1)
                elif action == 1: new_pos = self.position + V2(1, 0)
                elif action == 2: new_pos = self.position + V2(0, 1)
                elif action == 3: new_pos = self.position + V2(-1, 0)
                n = round(qt.qt[str(self.position)][action], 4)
                position = (new_pos * self.size + offset + self.size * V2(0, .35) + V2(50 - 5 * len(str(n)), 0))
                text_surface = my_font.render(str(n), False, (0, 0, 0))
                self.parent.screen.blit(text_surface, position())

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        if learn_mode != "l":
            self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
            self.clock = pg.time.Clock()
        self.start = V2(-1,2)
        self.end = V2(8,5)
        self.blocks = [Block(self, self.start, is_start=True)] + [Block(self, V2(i[0],i[1])) for i in [
            (1,0),(2,0),(2,1),(0,2),(1,2),(2,2),(4,2),(2,3),(3,3),(4,3),(5,3),(0,4),(3,4),(6,4),(0,5),(1,5),(2,5),(3,5),(4,5),(6,5),(7,5),(2,6),(4,6),(5,6),(6,6),(1,7),(2,7)
            ]] + [Block(self, self.end, is_end=True)]
        #self.blocks = [Block(self, self.start, is_start=True)] + [Block(self, V2(i[0],i[1])) for i in list(itertools.product(range(8), range(8)))] + [Block(self, self.end, is_end=True)]
        self.current = self.start
        self.last = V2(-100,-100)
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(5)
        self.clear()

        for block in self.blocks: block.draw()
        for block in self.blocks: block.draw_text()

        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
    
    def phys(self, action):
        self.last = self.current
        if   action == 0: self.current += V2(0, -1)
        elif action == 1: self.current += V2(1,  0)
        elif action == 2: self.current += V2(0,  1)
        elif action == 3: self.current += V2(-1, 0)
        doable = [0,1,2,3]
        blocks = [b.position() for b in self.blocks if b.position() != self.last()]
        if not (self.current + V2(0, -1))() in blocks: doable.remove(0)
        if not (self.current + V2(1,  0))() in blocks: doable.remove(1)
        if not (self.current + V2(0,  1))() in blocks: doable.remove(2)
        if not (self.current + V2(-1, 0))() in blocks: doable.remove(3)
        return doable

    def get_state_id(self):
        return str(self.current)

    def frame(self, action):
        doable = self.phys(action)
        death = False
        if doable == []: death = True

        if learn_mode != "l": self.draw()
        state_id = self.get_state_id()
        reward = -1
        if death:
            if self.current() == self.end():
                reward = 1000
            else:
                reward = -1000
            qt.qt["gen"] += 1
            self.current = self.start
        return state_id, reward, death, doable

qt = QT(len(commands), folder if open_file else None, epsilon=0.3 if learn_mode == "l" else 0, complex_mode=True, start_dec=[0,0])

env = Env()

stime = datetime.now()
times = 0

while not (env.quit or key.is_pressed("x")):
    state, reward, doable = env.get_state_id(), 0, [1]
    print(stime)
    while (datetime.now() - stime).total_seconds() < 10*60 and not key.is_pressed("x") and not env.quit:
        obs = state
        action = qt.get_action(obs, doable)
        state, reward, death, doable = env.frame(action)
        new_obs = state
        if death:
            state, doable = env.get_state_id(), [1]
            qt.set_reward(obs, action, new_obs, reward, doable)
        else:
            qt.set_reward(obs, action, new_obs, reward, doable)

    qt.save(folder)
    if (datetime.now() - stime).total_seconds() >= 10*60:
        print(f"Sleeping since: {datetime.now()}")
        print(f"Gens: {qt.qt['gen']}")
        print(f"LenQT: {len(qt.qt)}")
        print(f"Times: {times}")
        print(f"Epsilon: {qt.epsilon}")
        times += 1
        #tm.sleep(3*60)
        stime = datetime.now()
    else:
        break

qt.save(folder)
print(qt.qt)
print(f"Gens: {qt.qt['gen']}")
print(f"LenQT: {len(qt.qt)}")
print(f"Times: {times}")
print(f"Epsilon: {qt.epsilon}")
print(datetime.now()-stime)
