from datetime import datetime
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

max_frames = 200

commands = {i:l for i, l in enumerate([
    "w",
    "wa",
    "wd",
])}

key_commands = {ch:[] for ch in "wasd"}
for c in commands:
    for ch in commands[c]:
        key_commands[ch].append(c)

block_accuracy = 5
rotation_accuracy = 10

class Car:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.speed = 10
        self.size = V2(100, 50)
        self.spawn()

    def spawn(self):
        self.position = V2.randomize(V2z, self.parent.screen_size).round(block_accuracy)
        self.rotation = round(rnd.randint(0,359) / rotation_accuracy) * rotation_accuracy
        self.last_distance = np.inf
    
    def phys(self, action):
        if action in key_commands["a"]:# or key.is_pressed("a"):
            self.rotation -= rotation_accuracy
        if action in key_commands["d"]:# or key.is_pressed("d"):
            self.rotation += rotation_accuracy
        self.rotation = int(divmod(self.rotation, 360)[1])

        if action in key_commands["w"]:# or key.is_pressed("w"):
            self.position = self.position.point_from_degs(self.rotation, self.speed).round(block_accuracy)
        
    def get_rew(self):
        reward = 0
        curr_distance = self.position.distance_to(self.parent.check.position, False)
        if curr_distance >= self.last_distance:
            reward -= 100
        self.last_distance = curr_distance
        
        death = False
        if self.position.distance_to(self.parent.check.position) < self.parent.check.radius:
            reward = 10000
            death = True

        return reward, death

    def draw(self):
        pg.draw.lines(self.parent.screen, (255,127,0), True, get_points(self.position, self.size, self.rotation, True, True, True), 2)

class CheckPoint:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.radius = 20
        self.random_move()
    
    def random_move(self):
        self.position = V2.randomize(V2z, self.parent.screen_size).round(block_accuracy)
    
    def draw(self):
        pg.draw.circle(self.parent.screen, (0,0,255), self.position(), self.radius)

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1080, 1080)
        if learn_mode != "l":
            self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
            self.clock = pg.time.Clock()
        self.cframe = 0
        self.car = Car(self)
        self.check = CheckPoint(self)
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(60)
        self.clear()

        self.check.draw()
        self.car.draw()
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
    
    def phys(self, action):
        self.car.phys(action)

    def get_state_id(self):
        return str(self.check.position - self.car.position) + "|" + str(self.car.rotation)
    
    def get_reward(self):
        rew, death = self.car.get_rew()
        return rew, death

    def frame(self, action):
        self.phys(action)
        reward, death = self.get_reward()
        if learn_mode != "l": self.draw()
        state_id = self.get_state_id()
        self.cframe += 1
        if self.cframe > max_frames:
            death = True
        if death:
            self.cframe = 0
            self.check.random_move()
            self.car.spawn()
            qt.qt["gen"] += 1
        return state_id, reward, death

qt = QT(len(commands), folder if open_file else None, epsilon=.3 if learn_mode == "l" else 0, epsilon_dec=0.999998, learningR=.5)

env = Env()

stime = datetime.now()
times = 0

while not (env.quit or key.is_pressed("x")):
    state, reward = None, 0
    print(stime)
    while (datetime.now() - stime).total_seconds() < 10*60 and not key.is_pressed("x") and not env.quit:
        obs = state
        action = qt.get_action(obs)
        state, reward, death = env.frame(action)
        new_obs = state
        qt.set_reward(obs, action, new_obs, reward)
        if death: state = env.get_state_id()

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
print(f"Gens: {qt.qt['gen']}")
print(f"LenQT: {len(qt.qt)}")
print(f"Times: {times}")
print(f"Epsilon: {qt.epsilon}")
print(datetime.now()-stime)