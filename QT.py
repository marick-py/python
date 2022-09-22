import numpy as _np
import save as _save

class QT:
    def __init__(self, actions_space, path=None, epsilon=0.3, epsilon_dec=0.9998, start_dec=[-10,10], learningR=0.1, discount=0.95, complex_mode=False) -> None:
        self.qt = {"gen":0}
        if path != None:
            self.load(path)
        self.actions_space = actions_space
        self.learningR = learningR
        self.discount = discount
        self.start_dec = start_dec
        self.epsilon = epsilon
        self.eps_dec = epsilon_dec
        self.is_complex = complex_mode

    def load(self, path):
        self.qt = _save.load(path)
    
    def save(self, path):
        _save.save(path, self.qt)
    
    def new_gen(self):
        self.qt["gen"] += 1

    def get_action(self, obs, doable_actions=[]):
        if not obs in self.qt:
            if not self.is_complex:
                self.qt[obs] = [_np.random.uniform(self.start_dec[0], self.start_dec[1]) for _ in range(self.actions_space)]
            else:
                self.qt[obs] = {action:_np.random.uniform(self.start_dec[0], self.start_dec[1]) for _ in range(self.actions_space) for action in doable_actions}
        
        if _np.random.random() > self.epsilon:
            if not self.is_complex:
                action = _np.argmax(self.qt[obs])
            else:
                action = list(self.qt[obs].keys())[_np.argmax(list(self.qt[obs].values()))]
        else:
            if not self.is_complex:
                action = _np.random.randint(0, self.actions_space)
            else:
                action = _np.random.choice(list(self.qt[obs].keys()))

        return action

    def set_reward(self, old_state, action, new_state, reward, doable_actions=[]):
        obs = old_state
        new_obs = new_state

        if not new_obs in self.qt:
            if not self.is_complex:
                self.qt[new_obs] = [_np.random.uniform(self.start_dec[0], self.start_dec[1]) for _ in range(self.actions_space)]
            else:
                self.qt[new_obs] = {action:_np.random.uniform(self.start_dec[0], self.start_dec[1]) for _ in range(self.actions_space) for action in doable_actions}

        max_fq = max(list(self.qt[new_obs].values()))
        curr_q = self.qt[obs][action]
        
        new_q = ( 1 - self.learningR ) * curr_q + self.learningR * ( reward + self.discount * max_fq )
        self.qt[obs][action] = new_q
        self.epsilon *= self.eps_dec

"""
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
    "s",
    "sd",
    "sa",
    "a",
    "d"
])}

key_commands = {ch:[] for ch in "wasd"}
for c in commands:
    for ch in commands[c]:
        key_commands[ch].append(c)

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        if learn_mode != "l":
            self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
            self.clock = pg.time.Clock()
        self.frame = 0
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(0)
        self.clear()

        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
    
    def phys(self, action):
        rew = 0
        return rew

    def get_state_id(self):
        return ""
    
    def get_reward(self):
        rew = 0
        return rew

    def frame(self, action):
        reward = self.phys(action)
        reward += self.get_reward()
        if learn_mode != "l": self.draw()
        death = False
        state_id = self.get_state_id()
        self.frame += 1
        if self.frame > max_frames:
            death = True
        if death:
            qt.qt["gen"] += 1
        return state_id, reward, death

qt = QT(len(commands), folder if open_file else None)

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

"""