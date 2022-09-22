from datetime import datetime
import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
import time as tm
from e2D import *
from QT import *
import os

seed = rnd.random()
rnd.seed(seed)

LINE_DEATH_PENALITY = -1000
LEVEL_COMPLETE_PRIZE = 1000
MAX_DIFF_TO_MIN_DISTANCE = 100

FPS = 0

max_frames = 2000

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

class Ray:
    def __init__(self, parent, rotation, length) -> None:
        self.parent = parent
        self.rotation = rotation
        self.len = length
    
    def phys(self) -> None:
        self.intersections = self.parent.position.inter_points(self.parent.position.point_from_degs(self.rotation + self.parent.rotation, self.len), self.parent.parent.walls.Pwalls, True)
    
    def draw(self) -> None:
        pg.draw.line(self.parent.parent.screen, (0,50,0), self.parent.position(), self.parent.position.point_from_degs(self.rotation + self.parent.rotation, self.len)(), 2)
        for point in self.intersections:
            pg.draw.circle(self.parent.parent.screen, (0,127,255), self.parent.position.point_from_degs(self.parent.position.angle_to(point), round(self.parent.position.distance_to(point)/10)*10)(), 5)
            #pg.draw.circle(self.parent.parent.screen, (255,127,0), point(), 5)

class Car:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.randomize()
        self.speed = 1
        self.rays = [Ray(self, i, 150) for i in [0, 45, 90, 135, 180, 225, 270, 315]]
    
    def randomize(self) -> None:
        qt.qt["gen"] += 1
        self.rotation = rnd.randint(0,359)
        self.position = V2z.randomize(V2(50,50), self.parent.screen_size-V2(50, 200))
    
    def phys(self, action) -> None:
        if key.is_pressed("w") or action == 0:
            self.position.y -= self.speed
        if key.is_pressed("a") or action == 1:
            self.position.x -= self.speed
        if key.is_pressed("s") or action == 2:
            self.position.y += self.speed
        if key.is_pressed("d") or action == 3:
            self.position.x += self.speed
        if key.is_pressed("q") or action == 4:
            self.rotation -= 1
        if key.is_pressed("e") or action == 5:
            self.rotation += 1
        self.rotation = divmod(self.rotation, 360)[1]
        diag = V2z.distance_to(V2(50,25))
        self.lines = [
            [self.position.point_from_degs(30 + self.rotation, diag), self.position.point_from_degs(-30 + self.rotation, diag)],
            [self.position.point_from_degs(150 + self.rotation, diag), self.position.point_from_degs(-150 + self.rotation, diag)],
            [self.position.point_from_degs(30 + self.rotation, diag), self.position.point_from_degs(150 + self.rotation, diag)],
            [self.position.point_from_degs(-150 + self.rotation, diag), self.position.point_from_degs(-30 + self.rotation, diag)]
        ]
        for ray in self.rays: ray.phys()

    def is_colliding(self) -> bool:
        for line in self.lines:
            if line[0].inter_points(line[1], self.parent.walls.Pwalls) != []:
                return True
        return False

    def draw(self):
        for ray in self.rays: ray.draw()
        for line in self.lines:
            pg.draw.line(self.parent.screen, (0,0,255), line[0](), line[1](), 2)

class Sensor:
    def __init__(self, pointA, pointB, parent) -> None:
        self.parent = parent
        self.pointA = pointA
        self.pointB = pointB
    
    def draw(self):
        pg.draw.line(self.parent.parent.screen, (0,127,255), self.pointA(), self.pointB(), 2)
    
    def is_colliding(self):
        return self.pointA.inter_points(self.pointB, self.parent.parent.car.lines) != []

class Walls:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.walls = []
        self.sensors = []
        self.spawn_space()

    def draw(self):
        for wall in self.walls:
            pg.draw.line(self.parent.screen, (255,0,0), wall[0](), wall[1]())
        for sensor in self.sensors:
            sensor.draw()
    
    def spawn_space(self):
        space = 500
        car_size = V2(200, 55)
        start = rnd.randint(self.parent.screen_size.x/2 - space/2, self.parent.screen_size.x/2 + space/2) - car_size.x/2
        end = start + car_size.x
        percent = 30
        self.sensors = [
            Sensor(V2(start + car_size.x/100*percent, self.parent.screen_size.y/2 + 250 + car_size.y), V2(start + car_size.x/100*percent, self.parent.screen_size.y/2 + 250 + car_size.y/100*90), self),
            Sensor(V2(end - car_size.x/100*percent, self.parent.screen_size.y/2 + 250 + car_size.y), V2(end - car_size.x/100*percent, self.parent.screen_size.y/2 + 250 + car_size.y/100*90), self)]
        self.Pwalls = [
            (self.parent.screen_size/2 + V2(-500,  250), V2(start, self.parent.screen_size.y/2 + 250)),
            (V2(end, self.parent.screen_size.y/2 + 250), self.parent.screen_size/2 + V2( 500,  250)),
            (V2(start, self.parent.screen_size.y/2 + 250), V2(start, self.parent.screen_size.y/2 + 250 + car_size.y)),
            (V2(end, self.parent.screen_size.y/2 + 250), V2(end, self.parent.screen_size.y/2 + 250 + car_size.y)),
            (V2(start, self.parent.screen_size.y/2 + 250 + car_size.y), V2(end, self.parent.screen_size.y/2 + 250 + car_size.y))
        ]
        self.walls = self.Pwalls

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1100, 650)
        if learn_mode != "l":
            self.screen = pg.display.set_mode(self.screen_size(), display=1, vsync=1)
            self.clock = pg.time.Clock()
        self.walls = Walls(self)
        self.car = Car(self)
        self.min_distance = np.inf
        self.cframe = 0
        self.w = 0
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(FPS)
        self.clear()

        if not key.is_pressed("space"): self.walls.draw()
        self.car.draw()

        obj_point = sum([sensor.pointA.mid_point_to(sensor.pointB) for sensor in self.walls.sensors]) / 2
        pg.draw.circle(self.screen, (0,255,0), obj_point(), self.min_distance, 1)
        pg.draw.circle(self.screen, (255,0,0), obj_point(), self.min_distance + MAX_DIFF_TO_MIN_DISTANCE, 1)

        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
    
    def phys(self, action):
        rew = 0
        self.car.phys(action)
        self.cframe += 1
        if self.cframe >= max_frames:
            self.car.randomize()
            self.walls.spawn_space()
            self.min_distance = np.inf
            self.cframe = 0
        elif self.car.is_colliding():
            self.car.randomize()
            self.walls.spawn_space()
            rew += LINE_DEATH_PENALITY
            self.min_distance = np.inf
            self.cframe = 0
        elif all([sensor.is_colliding() for sensor in self.walls.sensors]):
            self.w += 1
            print(self.w)
            self.car.randomize()
            self.walls.spawn_space()
            self.min_distance = np.inf
            rew += LEVEL_COMPLETE_PRIZE
            self.cframe = 0
        return rew

    def get_state_id(self):
        rays = ".".join([str(round(ray.parent.position.distance_to(ray.intersections[0])/10)) if ray.intersections != [] else "-1" for ray in self.car.rays])
        offset = str(((sum([sensor.pointA.mid_point_to(sensor.pointB) for sensor in self.walls.sensors]) / 2 - self.car.position)/10).round())
        return rays + "|" + offset
    
    def get_reward(self):
        obj_point = sum([sensor.pointA.mid_point_to(sensor.pointB) for sensor in self.walls.sensors]) / 2
        c_distance = self.car.position.distance_to(obj_point)
        rew = (self.min_distance - c_distance) * 10
        if c_distance - self.min_distance > MAX_DIFF_TO_MIN_DISTANCE:
            self.car.randomize()
            self.walls.spawn_space()
            self.min_distance = np.inf
            rew += LINE_DEATH_PENALITY
            self.cframe = 0
        elif c_distance < self.min_distance: self.min_distance = c_distance
        return rew

    def frame(self, action):
        reward = self.phys(action) - 1
        reward += self.get_reward()
        if learn_mode != "l": self.draw()
        return self.get_state_id(), reward

qt = QT(6, folder if open_file else None, epsilon_dec=0.99998, learningR=0.1)

env = Env()

stime = datetime.now()
times = 0

while not (env.quit or key.is_pressed("x")):
    state, reward = None, 0
    print(stime)
    while (datetime.now() - stime).total_seconds() < 10*60 and not key.is_pressed("x") and not env.quit:
        obs = state
        action = qt.get_action(obs)
        state, reward = env.frame(action)
        new_obs = state
        qt.set_reward(obs, action, new_obs, reward)
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
