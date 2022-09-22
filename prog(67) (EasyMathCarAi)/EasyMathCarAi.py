import matplotlib.pyplot as plt
from datetime import datetime
from timeit import timeit
import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *
import time as tm
import winsound
import save
import math
import json

new = False
print("Start with a QTable: [file/new]")
while new not in ["n", "f", "file", "new"]:
    new = input(">>> ").replace(" ", "").lower()
folder_path = True if new in ["f", "file"] else False

folder = "\\".join(__file__.split("\\")[:-1])+ f"\\pickles\\"

print("Select Mode: [learn/show/debug]")
while new not in ["l", "s", "d"]:
    new = input(">>> ").replace(" ", "").lower()
learn_mode = new

if learn_mode in ["s", "d"]:
    import pygame as pg
    pg.init()

learningR = 0.5
discount = 0.95
epsilon = 0.35 if learn_mode == "l" else 0
eps_dec = 0.9998

max_frames = 200 # math.inf

CLOSER_STEP_REWARD = 10
CHEKCPOINT_REWARD = 10000
DEATH_PENALITY = -10000

rays_ang_list = [0, 45, -45, 90, -90, 135, -135, 180]

with open("\\".join(__file__.split("\\")[:-1])+ f"\\walls.json", "r") as file:
    file_wall = json.load(file)
with open("\\".join(__file__.split("\\")[:-1])+ f"\\checks.json", "r") as file:
    file_check = json.load(file)

commands = {
    0 : "",
    1 : "w",
    2 : "s",
    3 : "wd",
    4 : "wa",
    5 : "sd",
    6 : "sa"}
key_commands = {ch:[] for ch in "wasd"}
for c in commands:
    for ch in commands[c]:
        key_commands[ch].append(c)

class Car:
    def __init__(self, initial_position, initial_rotation, parent:Vector2D) -> None:
        self.parent = parent
        self.position = initial_position
        self.initial_position = initial_position
        self.initial_rotation = initial_rotation
        self.rotation = initial_rotation
        self.acceleration = 0
        self.max_steering = 4
        self.steering = 0
        self.steering_adj = 0.7
        self.dump = 0.9
        self.max_speed = 7
        self.accel_incr = 0.25
        self.rays = []
        self.car_collisions = []
        self.max_ray = 200
        self.min_ray = 10
        self.size = Vector2D(40,20)
        self.last_distance = self.position.distance_to(self.get_mid_check())
        self.last_difference = (self.get_mid_check() - self.position).abs()
        self.get_car_points()

    def get_mid_check(self):
        x,y = self.parent.checkpoints[self.parent.curr_check]
        return (Vector2D(info=x) + Vector2D(info=y))/2
    
    def draw(self):
        pg.draw.lines(surface=self.parent.screen, color=(255, 127, 0), closed=True, points=self.points, width=5)

        for deg in rays_ang_list:
            start_point = self.position.point_from_degs(VectorZero.angle_to(Vector2D(self.min_ray, 0)) + self.rotation + divmod(deg, 360)[1], VectorZero.distance_to(Vector2D(self.min_ray, 0)))()
            end_point = self.position.point_from_degs(VectorZero.angle_to(Vector2D(self.max_ray, 0)) + self.rotation + divmod(deg, 360)[1], VectorZero.distance_to(Vector2D(self.max_ray, 0)))()
            pg.draw.line(self.parent.screen, (0,127,127), start_point, end_point)

        for ray in self.rays:
            if ray != None:
                pg.draw.circle(self.parent.screen, (255,0,0), ray(), 5, 5)
                real_pos = self.position.point_from_degs(self.position.angle_to(ray), (self.position.distance_to(ray)/20).round()*20)
                pg.draw.circle(self.parent.screen, (0,255,0), real_pos(), 4, 4)

        for cc in self.car_collisions:
            if cc != None:
                for c in cc:
                    pg.draw.circle(self.parent.screen, (255,255,0), c(), 10, 10)

        X,Y = [Vector2D(info=x) for x in self.parent.checkpoints[self.parent.curr_check]]
        pg.draw.line(self.parent.screen, (255, 255, 255), self.position(), ((X+Y)/2)())

    def get_car_points(self):
        r = VectorZero.distance_to(self.size/2)
        self.points = [ self.position.point_from_degs(VectorZero.angle_to(Vector2D(-1, -1) * self.size/2) + self.rotation, r)(),
                        self.position.point_from_degs(VectorZero.angle_to(Vector2D(1, -1) * self.size/2) + self.rotation, r)(),
                        self.position.point_from_degs(VectorZero.angle_to(Vector2D(1, 1) * self.size/2) + self.rotation, r)(),
                        self.position.point_from_degs(VectorZero.angle_to(Vector2D(-1, 1) * self.size/2) + self.rotation, r)()]
        self.car_collisions = [collision if collision else None for collision in [[Vector2D(info=c) for c in self.inter_points(self.points[line[0]] + self.points[line[1]], [a+b for (a,b) in self.parent.walls])] for line in [(0,1),(1,2),(2,3),(3,0)]]]

    def get_ray_points(self):
        collisions = [[Vector2D(info=c) for c in self.inter_points(self.position.point_from_degs(VectorZero.angle_to(Vector2D(self.min_ray, 0)) + self.rotation + divmod(deg, 360)[1], VectorZero.distance_to(Vector2D(self.min_ray, 0)))() + self.position.point_from_degs(VectorZero.angle_to(Vector2D(self.max_ray, 0)) + self.rotation + divmod(deg, 360)[1], VectorZero.distance_to(Vector2D(self.max_ray, 0)))(), [a+b for (a,b) in self.parent.walls])] for deg in rays_ang_list]
        [collision.sort(key=lambda x: self.position.distance_to(x)) for collision in collisions]
        self.rays = [collision[0] if collision else None for collision in collisions]

    def lineLineIntersect(self, P0, P1, Q0, Q1):
        d = (P1[0]-P0[0]) * (Q1[1]-Q0[1]) + (P1[1]-P0[1]) * (Q0[0]-Q1[0]) 
        if d == 0: return None
        t = ((Q0[0]-P0[0]) * (Q1[1]-Q0[1]) + (Q0[1]-P0[1]) * (Q0[0]-Q1[0])) / d
        u = ((Q0[0]-P0[0]) * (P1[1]-P0[1]) + (Q0[1]-P0[1]) * (P0[0]-P1[0])) / d
        if 0 <= t <= 1 and 0 <= u <= 1: return round(P1[0] * t + P0[0] * (1-t)), round(P1[1] * t + P0[1] * (1-t))
        return None

    def inter_points(self, ray, lines):
        return [line for line in [self.lineLineIntersect(line1[:2], line1[2:], ray[:2], ray[2:]) for line1 in lines] if line]
    
    def is_dead(self):
        return self.car_collisions != [None] * 4
    
    def get_reward(self):
        rew = 0
        distance = self.position.distance_to(self.get_mid_check())
        difference = (self.get_mid_check() - self.position).abs()
        #if -3 < abs(self.last_distance - distance) < 3:
        #    rew += -CLOSER_STEP_REWARD
        
        if distance < self.last_distance: pass #rew += CLOSER_STEP_REWARD
        else: rew += -CLOSER_STEP_REWARD

        #if difference.x < self.last_difference.x: pass
        #else: rew += -CLOSER_STEP_REWARD
    
        #if difference.y < self.last_difference.y: pass
        #else: rew += -CLOSER_STEP_REWARD

        self.last_difference = difference
        self.last_distance = distance
        
        check_taken = self.next_check()
        if check_taken:
            rew += CHEKCPOINT_REWARD
        
        is_dead = self.is_dead()
        if is_dead:
            rew += DEATH_PENALITY
        if self.parent.check_frames > max_frames:
            is_dead = True
            rew -= 1

        return rew, is_dead
    
    def next_check(self):
        for line in [(0,1),(1,2),(2,3),(3,0)]:
            collision = [Vector2D(info=c) for c in self.inter_points(self.points[line[0]] + self.points[line[1]], [a+b for (a,b) in [self.parent.checkpoints[self.parent.curr_check]]])]
            if collision:
                self.parent.score += 1
                self.parent.check_frames = 0
                self.parent.curr_check = (self.parent.curr_check+1) % len(self.parent.checkpoints)
                return True
        return False

    def get_state(self):
        rays = ".".join([str(round(self.position.distance_to(ray)/20)) if ray != None else "-1" for ray in self.rays])
        X,Y = [Vector2D(info=x) for x in self.parent.checkpoints[self.parent.curr_check]]
        offset = ".".join([str(int(i/abs(i))) if abs(i) > 1 else str(0) for i in (((X+Y)/2 - self.position)/10).round()()])
        return rays + "|" + offset + "|" + str(round(divmod(self.rotation/10, 36)[1]))
    
    def randomize(self, position=True, rotation=True, border=100):
        if position:
            self.position.x = rnd.choice(list(range(border, self.parent.screen_size.x-border)))
            self.position.y = rnd.choice(list(range(border, self.parent.screen_size.y-border)))
        if rotation:
            self.rotation = divmod(rnd.choice(list(range(360))),360)[1]            
        self.initial_position = self.position
        self.initial_rotation = self.rotation

class Map:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = Vector2D(960, 540)
        if learn_mode in ["s", "d"]:
            self.screen = pg.display.set_mode(self.screen_size())
            self.clock = pg.time.Clock()
        self.max_score = 0
        self.score = 0
        self.scores = []
        self.spawn_entities()
    
    def spawn_entities(self):
        self.walls = [
            ((10, 10), (self.screen_size.x-10, 10)),
            ((10, self.screen_size.y-10), (self.screen_size.x-10, self.screen_size.y-10)),
            ((10, 10), (10, self.screen_size.y-10)),
            ((self.screen_size.x-10, 10),(self.screen_size.x-10, self.screen_size.y-10))
        ] + file_wall
        self.checkpoints = file_check
        self.check_frames = 0
        self.curr_check = 0
        self.last_check = None

        if self.max_score <= self.score:
            self.max_score = self.score
            # if self.max_score >= 100:
            #     for _ in range(100):
            #         winsound.Beep(5000, 100)
        self.scores.append(self.score)
        self.score = 0
        self.car = Car(self.screen_size/2 + V2(0, -50), divmod(0, 360)[1], self)

    def clear(self):
        self.screen.fill((0,0,0))

    def print(self):
        self.clock.tick(1 if key.is_pressed("space") else 60)
        self.clear()
        for wall in self.walls:
            pg.draw.line(self.screen, (0, 25, 127), wall[0], wall[1], 5)
        pg.draw.line(self.screen, (0, 255, 255), self.checkpoints[self.curr_check][0], self.checkpoints[self.curr_check][1], 5)
        self.car.draw()
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
        # if key.is_pressed("alt"):
        #     mousePos = V2(info=pg.mouse.get_pos())
        #     if self.last_check != None:
        #         self.checkpoints.append((self.last_check(), mousePos()))
        #     self.last_check = mousePos
        #     while key.is_pressed("alt"): pass
        # if key.is_pressed("ctrl"): self.last_check = None
    
    def phys(self, action):
        velocity, steering = self.input(action)

    #   velocity
        self.car.acceleration += velocity * self.car.accel_incr
        if not (-self.car.max_speed <= self.car.acceleration <= self.car.max_speed):
            self.car.acceleration = -self.car.max_speed if self.car.acceleration < 0 else self.car.max_speed
        self.car.position.set(info=self.car.position.point_from_degs(self.car.rotation, self.car.acceleration))
        if velocity == 0:
            steering = 0
            self.car.acceleration *= self.car.dump

    #   steering
        if velocity > 0:
            self.car.steering += steering
        elif velocity < 0:
            self.car.steering -= steering
        self.car.rotation += self.car.steering
        if not (-self.car.max_steering <= self.car.steering <= self.car.max_steering):
            self.car.steering = -self.car.max_steering if self.car.steering < 0 else self.car.max_steering
        if self.car.steering != 0 and steering == 0:
            self.car.steering *= self.car.steering_adj

        self.car.get_car_points()
        self.car.get_ray_points()
        
        reward,reset = self.car.get_reward()
        if reset:
            self.spawn_entities()
            qt["gen"] += 1
        return reward
        

    def input(self, input):
        velocity = 0
        if input in key_commands["w"]:# or key.is_pressed("w"):
            velocity += 1
        if input in key_commands["s"]:# or key.is_pressed("s"):
            velocity -= 1
        
        steering = 0
        if input in key_commands["a"]:# or key.is_pressed("a"):
            steering -= 1
        if input in key_commands["d"]:# or key.is_pressed("d"):
            steering += 1
        return velocity, steering


    def frame(self, action):
        reward = self.phys(action)
        if learn_mode in ["s", "d"]:
            self.print()
        self.check_frames += 1
        return self.car.get_state(), reward

mmap = Map()
stime = datetime.now()
times = 0

if folder_path:
    qt = save.load(folder)
else:
    qt = {"gen":0}
print("QT loaded...")

while not key.is_pressed("x") and not mmap.quit:
    state, reward = mmap.frame(0)
    print(stime)
    mmap.scores.clear()
    while (datetime.now() - stime).total_seconds() < 10*60 and not key.is_pressed("x") and not mmap.quit:
        obs = state
        if not obs in qt:
            qt[obs] = [np.random.uniform(-10, 10) for _ in range(5)]
        
        if np.random.random() > epsilon:
            action = np.argmax(qt[obs])
        else:
            action = rnd.randint(0,4)
        if learn_mode == "d":
            #input(str(qt[obs]) + " | " + str(action) + " | " exec('x = np.round(345.345)', globals())+ str(reward))
            #print(qt[obs])
            #print(obs, action)
            #print(reward)
            #print(epsilon)
            pass
        state, reward = mmap.frame(action if not learn_mode == "d" else -2)
        new_obs = state

        if not new_obs in qt:
            qt[new_obs] = [np.random.uniform(-10, 10) for _ in range(5)]

        max_fq = max(qt[new_obs])
        curr_q = qt[obs][action]
        
        new_q = ( 1 - learningR ) * curr_q + learningR * ( reward + discount * max_fq )
        qt[obs][action] = new_q
        epsilon *= eps_dec

    save.save(folder, qt)
    if mmap.score > mmap.max_score:
        mmap.max_score = mmap.score
    mmap.scores.append(mmap.score)
    if (datetime.now() - stime).total_seconds() >= 10*60:
        print(f"Sleeping since: {datetime.now()}")
        print(f"Gens: {qt['gen']}")
        print(f"LenQT: {len(qt)}")
        print(f"Times: {times}")
        print(f"MaxScore: {mmap.max_score}")
        print(f"AVGScores: {sum(mmap.scores)/len(mmap.scores)}")
        print(f"BlockGens: {len(mmap.scores)}")
        print(f"Epsilon: {epsilon}")
        epsilon = 0.35 if learn_mode == "l" else 0
        times += 1
        #tm.sleep(3*60)
        stime = datetime.now()
    else:
        break
    mmap.scores.clear()

print(f"Gens: {qt['gen']}")
print(f"LenQT: {len(qt)}")
print(f"Times: {times}")
print(f"MaxScore: {mmap.max_score}")
print(f"AVGScores: {sum(mmap.scores)/len(mmap.scores)}")
print(f"BlockGens: {len(mmap.scores)}")
print(f"Epsilon: {epsilon}")
print(datetime.now()-stime)
#_ = plt.plot(list(range(len(mmap.scores))), mmap.scores)
#try:plt.show()
#except:pass

with open("\\".join(__file__.split("\\")[:-1])+ f"\\walls.json", "w") as file:
    json.dump(mmap.walls[4:], file, indent="\t")
with open("\\".join(__file__.split("\\")[:-1])+ f"\\checks.json", "w") as file:
    json.dump(mmap.checkpoints, file, indent="\t")

input()