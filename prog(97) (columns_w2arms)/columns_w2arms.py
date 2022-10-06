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

if learn_mode in ["s", "d"]:
    import pygame as pg
    pg.init()

max_frames = 1000

commands = list(range(9))

speed = 5

class Point:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.position = V2.randomize(V2z, self.parent.screen_size)
        self.radius = 40

    def phys(self):
        pass #self.position = V2(info=pg.mouse.get_pos())

    def draw(self):
        pg.draw.circle(self.parent.screen, (255,0,0), self.position(), self.radius)

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        if learn_mode != "l":
            self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
            self.clock = pg.time.Clock()
        self.l_arm = V2.randomize(V2z, self.screen_size)
        self.r_arm = V2.randomize(V2z, self.screen_size)
        self.point = Point(self)
        self.last_distance = np.inf
        self.cframe = 0
        self.lasts_100 = []

    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(0)
        self.clear()

        pg.draw.line(self.screen, (0,255,0), V2(0, self.l_arm.y)(), self.l_arm(), 2)
        pg.draw.line(self.screen, (0,0,255), V2(self.screen_size.x, self.r_arm.y)(), self.r_arm(), 2)
        pg.draw.lines(self.screen, (255,127,0), True, self.square_points, 10)
        
        self.point.draw()

        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
    
    def phys(self, action):
        rew = 0
        if action == 0: pass
        elif action == 1:
            self.l_arm.y -= 1 * speed
        elif action == 2:
            self.l_arm.x += 1 * speed
        elif action == 3:
            self.l_arm.y += 1 * speed
        elif action == 4:
            self.l_arm.x -= 1 * speed
        elif action == 5:
            self.r_arm.y -= 1 * speed
        elif action == 6:
            self.r_arm.x += 1 * speed
        elif action == 7:
            self.r_arm.y += 1 * speed
        elif action == 8:
            self.r_arm.x -= 1 * speed

        self.point.phys()
        self.middle = avg_position(self.l_arm, self.r_arm)
        self.square_lines = get_lines(self.middle, V2(100,100), 0, True)
        self.square_points = get_points(self.middle, V2(100,100), 0, True, True, True)

        return rew

    def get_state_id(self):
        return ""
    
    def get_reward(self):
        rew = 0
        curr_distance = self.middle.distance_to(self.point.position)
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

        if self.cframe > max_frames:
            death = True
            self.lasts_100.append(0)
        if death:
            qt.qt["gen"] += 1
            self.point = Point(self)
            self.last_distance = np.inf
            self.cframe = 0
        return state_id, reward, death

qt = QT(len(commands), folder if open_file else None)

env = Env()

stime = datetime.now()
times = 0
process_time = 10

complete_in_time_list = []

while not (env.quit or key.is_pressed("x")):
    state, reward = None, 0
    print(stime)
    while (datetime.now() - stime).total_seconds() < process_time*60 and not key.is_pressed("x") and not env.quit:
        print(qt.qt)
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