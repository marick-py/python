from datetime import datetime
import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *
import itertools
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

max_frames = 600

commands = {i:l for i, l in enumerate([
    "w",
    "wa",
    "wd"
])}

key_commands = {ch:[] for ch in "wasd"}
for c in commands:
    for ch in commands[c]:
        key_commands[ch].append(c)

CHECKPOINT_REWARD = 10000
OUT_OF_FRAMES_PENALITY = -1000
COLLIDING_PENALITY = -1000
STEP_PRICE = 0
WRONG_STEP_PENALITY = -100

class Car:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.reset()
        self.size = V2(100, 100)
        self.speed = 5
        self.rotation_speed = 2
        self.rotation = 90
    
    def reset(self):
        self.position = V2(200, 200)
        self.last_distance = np.inf
        self.last_distance_rotation = np.inf

    def draw(self):
        pg.draw.circle(self.parent.screen, (255,0,0) if self.parent.checkpoints[self.parent.curr_checkpoint_index].position.distance_to(self.position) > self.last_distance else (0,255,0), self.parent.checkpoints[self.parent.curr_checkpoint_index].position(), self.last_distance, 2)
        pg.draw.rect(self.parent.screen, (255,127,0), (self.position - self.size / 2)() + self.size())
        pg.draw.line(self.parent.screen, self.rot_line, self.position(), self.position.point_from_degs(self.rotation, 100)(), 10)
        pg.draw.line(self.parent.screen, self.rot_line, self.parent.checkpoints[self.parent.curr_checkpoint_index].position(), self.position.point_from_degs(self.rotation, 100)(), 10)
    
    def input(self, action):
        movement = V2z.copy()
        if action in key_commands["w"]: movement.y -= 1 #or key.is_pressed("w"): movement.y -= 1
        if action in key_commands["a"]: movement.x -= 1 #or key.is_pressed("a"): movement.x -= 1
        if action in key_commands["s"]: movement.y += 1 #or key.is_pressed("s"): movement.y += 1
        if action in key_commands["d"]: movement.x += 1 #or key.is_pressed("d"): movement.x += 1
        return movement

    def frame(self, action):
        is_colliding = False
        inp = self.input(action)
        self.rotation = divmod(self.rotation + inp.x * self.rotation_speed, 360)[1]
        self.change = self.position - self.position.point_from_degs(self.rotation, self.speed * inp.y)
        self.position.x += self.change.x
        lines = get_lines(self.position, self.size)
        if [line for line in [line[0].inter_points(line[1], itertools.chain(*[obstacle.lines for obstacle in self.parent.obstacles])) for line in lines] if line != []] != []:
            self.position.x -= self.change.x
            is_colliding = True
        self.position.y += self.change.y
        lines = get_lines(self.position, self.size)
        if [line for line in [line[0].inter_points(line[1], itertools.chain(*[obstacle.lines for obstacle in self.parent.obstacles])) for line in lines] if line != []] != []:
            self.position.y -= self.change.y
            is_colliding = True

        rew = COLLIDING_PENALITY if is_colliding else 0
        if [line for line in [line[0].inter_points(line[1], self.parent.checkpoints[self.parent.curr_checkpoint_index].lines) for line in lines] if line != []] != []:
            rew += CHECKPOINT_REWARD
            self.parent.score += 1
            self.parent.cframe = 0
            self.parent.curr_checkpoint_index += 1
            self.last_distance = np.inf
            self.last_distance_rotation = np.inf
            if self.parent.curr_checkpoint_index == len(self.parent.checkpoints):
                self.parent.curr_checkpoint_index = 0
        check = self.parent.checkpoints[self.parent.curr_checkpoint_index]
        curr_distance = check.position.distance_to(self.position)
        curr_distance_rotation = check.position.distance_to(self.position.point_from_degs(self.rotation, 100))
        if curr_distance_rotation < self.last_distance_rotation:
            self.rot_line = (0,255,0)
            rew -= WRONG_STEP_PENALITY
        elif abs(self.position.angle_to(check.position) - self.rotation) < 10:
            rew -= WRONG_STEP_PENALITY
            self.rot_line = (255,255,255)
        else:
            rew += WRONG_STEP_PENALITY
            self.rot_line = (255,0,0)
        self.last_distance_rotation = curr_distance_rotation


        if curr_distance < self.last_distance:
            self.last_distance = curr_distance
        else:
            rew += WRONG_STEP_PENALITY
        return rew
        
class Obstacle:
    def __init__(self, parent, position, size) -> None:
        self.parent = parent
        self.position = position
        self.size = size
        self.lines = get_lines(self.position, size)
    
    def draw(self):
        pg.draw.rect(self.parent.screen, (0,0,255), (self.position - self.size / 2)() + self.size())

class CheckPoint:
    def __init__(self, parent, position, size) -> None:
        self.parent = parent
        self.position = position
        self.size = size
        self.lines = get_lines(self.position, size)
    
    def draw(self):
        pg.draw.rect(self.parent.screen, (0,255,0), (self.position - self.size / 2)() + self.size())

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        if learn_mode != "l":
            self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
            self.clock = pg.time.Clock()
        self.cframe = 0
        self.car = Car(self)
        self.score = 0
        self.score_mem = []
        self.obstacles = [
            Obstacle(self, V2(0,                  self.screen_size.y/2), V2(50,  self.screen_size.y)),
            Obstacle(self, V2(self.screen_size.x, self.screen_size.y/2), V2(50,  self.screen_size.y)),
            Obstacle(self, V2(self.screen_size.x/2,                  0), V2(self.screen_size.x,  50)),
            Obstacle(self, V2(self.screen_size.x/2, self.screen_size.y), V2(self.screen_size.x,  50)),
            # Obstacle(self, V2(600,                                 450), V2(100,                850)),
            # Obstacle(self, V2(1100,                                500), V2(900,                100))
            ]
        self.checkpoints = [
            CheckPoint(self, V2(600, 960), V2(25, 140)),
            CheckPoint(self, V2(1725, 500), V2(320, 25)),
            CheckPoint(self, V2(750, 225), V2(25, 275)),
            CheckPoint(self, V2(1725, 500), V2(320, 25)),
        ]
        self.curr_checkpoint_index = 0

    def clear(self):
        self.screen.fill((0,0,0))

    def draw(self):
        self.clock.tick(0)
        self.clear()

        for obstacle in self.obstacles: obstacle.draw()
        self.checkpoints[self.curr_checkpoint_index].draw()
        self.car.draw()

        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
    
    def phys(self, action):
        rew = 0
        rew += self.car.frame(action)
        return rew

    def get_state_id(self):
        return str((self.car.position/10).round()) + "|" +str(round(self.car.rotation))+ "|" + str(self.curr_checkpoint_index)

    def frame(self, action):
        reward = self.phys(action) + STEP_PRICE
        if learn_mode != "l": self.draw()
        state_id = self.get_state_id()
        self.cframe += 1
        death = False
        if self.cframe > max_frames:
            qt.qt["gen"] += 1
            self.cframe = 0
            self.car.reset()
            self.curr_checkpoint_index = 0
            death = True
            reward += OUT_OF_FRAMES_PENALITY
            self.score_mem.append(self.score)
            self.score = 0
            while len(self.score_mem) > 100: self.score_mem.pop(0)
        return state_id, reward, death

qt = QT(len(commands), folder if open_file else None, epsilon=.3 if learn_mode == "l" else 0, epsilon_dec=0.9998)

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

    env.score_mem.append(env.score)
    if (datetime.now() - stime).total_seconds() >= 10*60:
        qt.save(folder)
        print(f"Sleeping since: {datetime.now()}")
        print(f"Gens: {qt.qt['gen']}")
        print(f"LenQT: {len(qt.qt)}")
        if len(env.score_mem):
            print(f"Max Score: {max(env.score_mem)}")
            print(f"AVG Score: {sum(env.score_mem)/len(env.score_mem)}")
        print(f"Times: {times}")
        print(f"Epsilon: {qt.epsilon}")
        times += 1
        #tm.sleep(3*60)
        stime = datetime.now()
        qt.epsilon = .3
    else:
        break

qt.save(folder)
print(f"Gens: {qt.qt['gen']}")
print(f"LenQT: {len(qt.qt)}")
if len(env.score_mem):
    print(f"Max Score: {max(env.score_mem)}")
    print(f"AVG Score: {sum(env.score_mem)/len(env.score_mem)}")
print(f"Times: {times}")
print(f"Epsilon: {qt.epsilon}")
print(datetime.now()-stime)
input()