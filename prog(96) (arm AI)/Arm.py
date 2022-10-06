import matplotlib.pyplot as plt
from datetime import datetime
import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *
import itertools
from QT import *
import shutil
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

max_frames = 1000

if learn_mode in ["s", "d"]:
    import pygame as pg
    pg.init()

arms_count = 2

commands = list(range(3**arms_count))
actions_for_arm = list(set(itertools.combinations([-1, 0, 1] * arms_count, arms_count)))
actions_for_arm.sort()

precision = .5

class Arm:
    def __init__(self, parent, len, index) -> None:
        self.len = len
        self.parent = parent
        self.index = index
        self.rotation = np.floor(rnd.randint(0, 359) / precision) * precision if precision > 1 else rnd.randint(0, 359) * precision

    def phys(self, action):
        self.rotation += actions_for_arm[action][self.index] * precision
        self.rotation = divmod(self.rotation, 360)[1]
        self.position = self.parent.arms[self.index-1].point if self.index != 0 else self.parent.base
        self.point = self.position.point_from_degs(self.rotation, self.len)
    
    def draw(self):
        pg.draw.line(self.parent.screen, (255,255,255), self.position(), self.point())

class Point:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.position = V2.randomize(V2z, self.parent.screen_size)
        self.radius = 40

    def phys(self):
        self.position = V2(info=pg.mouse.get_pos()) ##########

    def draw(self):
        pg.draw.circle(self.parent.screen, (255,0,0), self.position(), self.radius)

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        if learn_mode != "l":
            self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
            self.clock = pg.time.Clock()
        self.base = self.screen_size * V2(.5,.5)
        self.arms = [Arm(self, int(self.base.distance_to(V2z) / arms_count), i) for i in range(arms_count)]
        self.point = Point(self)
        self.last_distance = np.inf
        self.cframe = 0
        self.lasts_100 = []
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(0)
        self.clear()

        self.point.draw()
        for arm in self.arms: arm.draw()
        pg.draw.circle(self.screen, (0,0,255), self.arms[-1].point(), 20)
        pg.draw.line(self.screen, (0,255,0), self.point.position(), self.arms[-1].point())

        if ms.is_pressed():
            self.base = V2(info=pg.mouse.get_pos())

        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

    def phys(self, action):
        self.point.phys()
        for arm in self.arms: arm.phys(action)

    def get_state_id(self):
        return ".".join([str(arm.rotation) for arm in self.arms]) + "~" + str((self.point.position - self.arms[-1].point).absolute_round().round()) if self.arms[-1].point.distance_to(self.point.position) > self.point.radius else str("0.0")

    def get_reward(self):
        rew = 0
        curr_distance = self.arms[-1].point.distance_to(self.point.position)
        if self.last_distance > curr_distance:
            rew += 0
        else:
            rew -= 100
        self.last_distance = curr_distance
        death = False
        if curr_distance < self.point.radius:
            rew += 10000
            death = True
            self.lasts_100.append(100)
        return rew, death

    def frame(self, action):
        self.phys(action)
        reward, death = self.get_reward()
        if learn_mode != "l": self.draw()
        state_id = self.get_state_id()
        self.cframe += 1

        # if self.cframe > max_frames:
        #     death = True
        #     self.lasts_100.append(0)
        # if death:
        #     qt.qt["gen"] += 1
        #     self.point = Point(self)
        #     self.last_distance = np.inf
        #     self.cframe = 0
        return state_id, reward, death

qt = QT(len(commands), folder if open_file else None, epsilon=.3 if learn_mode == "l" else 0, epsilon_dec=0.999998)
#qt.save.max_file_size = 100_000

env = Env()

stime = datetime.now()
times = 0
process_time = 10

complete_in_time_list = []

while not (env.quit or key.is_pressed("x")):
    state, reward = None, 0
    print(stime)
    while (datetime.now() - stime).total_seconds() < process_time*60 and not key.is_pressed("x") and not env.quit:
        obs = state
        action = qt.get_action(obs)
        state, reward, death = env.frame(action)
        new_obs = state
        qt.set_reward(obs, action, new_obs, reward)
        if death: state = env.get_state_id()

    complete_in_time_list.append(sum(env.lasts_100)/len(env.lasts_100))
    curr_best = float(list(filter(lambda x: "best_" in x, os.listdir(main_folder_dir)))[0].replace("best_", ""))
    if curr_best < sum(env.lasts_100)/len(env.lasts_100):
        shutil.rmtree(main_folder_dir + "\\" + list(filter(lambda x: "best_" in x, os.listdir(folder.split("\\")[0])))[0])
        os.mkdir(main_folder_dir + "\\best_" + str(sum(env.lasts_100)/len(env.lasts_100)))
        qt.save(main_folder_dir + "\\best_" + str(sum(env.lasts_100)/len(env.lasts_100)))
    if (datetime.now() - stime).total_seconds() >= process_time*60:
        qt.save(folder)
        print(f"Sleeping since: {datetime.now()}")
        print(f"Gens: {qt.qt['gen']}")
        print(f"LenQT: {len(qt.qt)}")
        print(f"%: {sum(env.lasts_100)/len(env.lasts_100)}%")
        print(f"Times: {times}")
        print(f"Epsilon: {qt.epsilon}")
        times += 1
        #tm.sleep(3*60)
        stime = datetime.now()
        env.lasts_100 = []
    else:
        break

qt.save(folder)
print(f"Gens: {qt.qt['gen']}")
print(f"LenQT: {len(qt.qt)}")
print(f"Times: {times}")
print(f"Epsilon: {qt.epsilon}")
print(f"%: {sum(env.lasts_100)/len(env.lasts_100)}%")
print(f"Seed: {seed}")
print(datetime.now()-stime)

print(complete_in_time_list)
if len(complete_in_time_list) > 1:
    plt.plot(list(range(len(complete_in_time_list))), complete_in_time_list)
    plt.show()