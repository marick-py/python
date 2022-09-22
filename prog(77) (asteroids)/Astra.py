import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *
from QT import *

seed = rnd.random()
rnd.seed(seed)

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

hack = True
random_asteroid_spawn_rotation = 90

class Asteroid:
    def __init__(self, parent) -> None:
        self.parent = parent
        if rnd.random() > 0.5:
            x = rnd.random() * self.parent.screen_size.x
            y = 0 if rnd.random() > 0.5 else self.parent.screen_size.y
        else:
            x = 0 if rnd.random() > 0.5 else self.parent.screen_size.x
            y = rnd.random() * self.parent.screen_size.y
        self.position = V2(x,y)
        self.rotation = self.position.angle_to(self.parent.screen_size/2) + (rnd.random()-0.5) * random_asteroid_spawn_rotation
        self.size = rnd.random() * 25 + 10     # 10 - 35
        self.speed = rnd.random() * 5 + 5
        self.delete = False
    
    def draw(self):
        pg.draw.circle(self.parent.screen, (150, 50, 0), self.position(), self.size)
        if hack:
            pg.draw.line(self.parent.screen, (0, 0, 100), self.position(), self.position.point_from_degs(self.rotation, V2z.distance_to(self.parent.screen_size))())
            #pg.draw.line(self.parent.screen, (255,0,0), self.position(), self.position.point_from_degs(self.position.angle_to(self.parent.screen_size/2) + random_asteroid_spawn_rotation/2, V2z.distance_to(self.parent.screen_size))())
            #pg.draw.line(self.parent.screen, (255,0,0), self.position(), self.position.point_from_degs(self.position.angle_to(self.parent.screen_size/2) - random_asteroid_spawn_rotation/2, V2z.distance_to(self.parent.screen_size))())
    
    def frame(self):
        self.position.set(info=self.position.point_from_degs(self.rotation, self.speed))
        if not (0-self.size < self.position.x < self.parent.screen_size.x+self.size and 0-self.size < self.position.y < self.parent.screen_size.y+self.size):
            self.delete = True

class RKL:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.position = self.parent.screen_size / 2
        self.rotation = 0
        self.size = V2(50, 20)
    
    def circle_line_segment_intersection(self, circle_center, circle_radius, pt1, pt2, full_line=True, tangent_tol=1e-9):
        (p1x, p1y), (p2x, p2y), (cx, cy) = pt1, pt2, circle_center
        (x1, y1), (x2, y2) = (p1x - cx, p1y - cy), (p2x - cx, p2y - cy)
        dx, dy = (x2 - x1), (y2 - y1)
        dr = (dx ** 2 + dy ** 2)**.5
        big_d = x1 * y2 - x2 * y1
        discriminant = circle_radius ** 2 * dr ** 2 - big_d ** 2

        if discriminant < 0:
            return []
        else:
            intersections = [
                (cx + (big_d * dy + sign * (-1 if dy < 0 else 1) * dx * discriminant**.5) / dr ** 2,
                cy + (-big_d * dx + sign * abs(dy) * discriminant**.5) / dr ** 2)
                for sign in ((1, -1) if dy < 0 else (-1, 1))]
            if not full_line:
                fraction_along_segment = [(xi - p1x) / dx if abs(dx) > abs(dy) else (yi - p1y) / dy for xi, yi in intersections]
                intersections = [pt for pt, frac in zip(intersections, fraction_along_segment) if 0 <= frac <= 1]
            if len(intersections) == 2 and abs(discriminant) <= tangent_tol:
                return [intersections[0]]
            else:
                return intersections

    def frame(self, fire, rotation):
        #cpy = self.parent.asteroids.copy()
        #cpy.sort(key=lambda x: x.position.distance_to(self.position))
        #rotation = self.position.angle_to(cpy[0].position) if cpy else self.position.angle_to(V2(info=pg.mouse.get_pos()))
        rew = 0
        if fire:
            for i, astr in enumerate(self.parent.asteroids):
                inter = self.circle_line_segment_intersection(astr.position(), astr.size, self.position(), self.position.point_from_degs(self.rotation, V2z.distance_to(self.parent.screen_size))())
                if inter:
                    rew += 1000
                    del self.parent.asteroids[i]
        else:
            self.rotation = rotation


        diag = sum(((self.size / 2)**2)())**(1/2)
        self.lines = [
            [self.position.point_from_degs(self.rotation+330, diag),
            self.position.point_from_degs(self.rotation+30, diag)],
            [self.position.point_from_degs(self.rotation+30, diag),
            self.position.point_from_degs(self.rotation+150, diag)],
            [self.position.point_from_degs(self.rotation+150, diag),
            self.position.point_from_degs(self.rotation+210, diag)],
            [self.position.point_from_degs(self.rotation+210, diag),
            self.position.point_from_degs(self.rotation+330, diag)]
        ]
        if rew == 0 and fire:
            rew = -1000
        return rew

    def draw(self):
        for line in self.lines:
            pg.draw.line(self.parent.screen, (255, 127, 0), line[0](), line[1](), 2)
        
        pg.draw.line(self.parent.screen, (0,255,0), self.position.point_from_degs(180+self.rotation, V2z.distance_to(self.parent.screen_size))(), self.position.point_from_degs(self.rotation, V2z.distance_to(self.parent.screen_size))())
        self.intersections = [self.circle_line_segment_intersection(astr.position(), astr.size, self.position(), self.position.point_from_degs(self.rotation, V2z.distance_to(self.parent.screen_size))()) for astr in self.parent.asteroids]
        for intersection in self.intersections:
            if intersection:
                for point in intersection:
                    pg.draw.circle(self.parent.screen, (0, 255, 0), point, 10)


class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)/2
        if learn_mode != "l":
            self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
            self.clock = pg.time.Clock()
        self.asteroids = []
        self.rkl = RKL(self)
    
    def reset(self):
        self.asteroids = []
        self.rkl = RKL(self)

    def spawn_asteroids(self):
        if rnd.random() > 0.96 and len(self.asteroids) < 20: #x = [[rnd.random() > 0.99 for _ in range(144)].count(True) for _ in range(100000)]; sum(x) / len(x)
            self.asteroids.append(Asteroid(self))

    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(144)
        self.clear()

        self.rkl.draw()
        for asteroid in self.asteroids:
            asteroid.draw()

        pg.display.update()
    
    def phys(self, action):
        if action == 360:
            rew = self.rkl.frame(True, 0)
        else:
            rew = self.rkl.frame(False, action)

        for i, asteroid in enumerate(self.asteroids):
            asteroid.frame()
            if asteroid.delete: del self.asteroids[i]
        return rew
    
    def get_state(self):
        cpy = self.asteroids.copy()
        cpy.sort(key=lambda x: x.position.distance_to(self.rkl.position))
        return str(cpy[0].position if cpy else V2(-1, -1)) + "|" + str(round(self.rkl.rotation))

    def frame(self, action):
        self.spawn_asteroids()
        rew = self.phys(action)
        if learn_mode != "l":
            self.draw()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit = True
        return self.get_state(), rew

env = Env()
qt = QT(361, folder if folder_path else None, 0.35 if learn_mode == "l" else 0)

state = env.get_state()
while not (env.quit or key.is_pressed("x")):
    action = qt.get_action(state)
    old_state = state
    state, rew = env.frame(action)
    qt.set_reward(old_state, action, state, rew)
qt.save(folder)

"""
class SpaceShip:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.position = self.parent.screen_size / 2
        self.rotation = rnd.random() * 360
        self.size = V2(75, 20)
        self.acceleration = 0
        self.max_acceleration = 10
        self.dump = 0.99
    
    def circle_line_segment_intersection(circle_center, circle_radius, pt1, pt2, full_line=True, tangent_tol=1e-9):
        (p1x, p1y), (p2x, p2y), (cx, cy) = pt1, pt2, circle_center
        (x1, y1), (x2, y2) = (p1x - cx, p1y - cy), (p2x - cx, p2y - cy)
        dx, dy = (x2 - x1), (y2 - y1)
        dr = (dx ** 2 + dy ** 2)**.5
        big_d = x1 * y2 - x2 * y1
        discriminant = circle_radius ** 2 * dr ** 2 - big_d ** 2

        if discriminant < 0:
            return []
        else:
            intersections = [
                (cx + (big_d * dy + sign * (-1 if dy < 0 else 1) * dx * discriminant**.5) / dr ** 2,
                cy + (-big_d * dx + sign * abs(dy) * discriminant**.5) / dr ** 2)
                for sign in ((1, -1) if dy < 0 else (-1, 1))]
            if not full_line:
                fraction_along_segment = [(xi - p1x) / dx if abs(dx) > abs(dy) else (yi - p1y) / dy for xi, yi in intersections]
                intersections = [pt for pt, frac in zip(intersections, fraction_along_segment) if 0 <= frac <= 1]
            if len(intersections) == 2 and abs(discriminant) <= tangent_tol:
                return [V2(info=x) for x in intersections[0]]
            else:
                return V2(info=intersections)
    
    def frame(self):
        velocity, steering = self.input()
        if velocity:
            if self.acceleration < self.max_acceleration:
                self.acceleration += 0.1
        else:
            self.acceleration *= self.dump

        self.rotation += steering * 2 * (1/(1 + np.exp(-(self.acceleration) + self.max_acceleration/2)))

        self.position.set(info=self.position.point_from_degs(self.rotation, self.acceleration))

        diag = sum(((self.size / 2)**2)())**(1/2)
        self.lines = [
            [self.position.point_from_degs(self.rotation+330, diag),
            self.position.point_from_degs(self.rotation+30, diag)],
            [self.position.point_from_degs(self.rotation+30, diag),
            self.position.point_from_degs(self.rotation+150, diag)],
            [self.position.point_from_degs(self.rotation+150, diag),
            self.position.point_from_degs(self.rotation+210, diag)],
            [self.position.point_from_degs(self.rotation+210, diag),
            self.position.point_from_degs(self.rotation+330, diag)]
        ]

    def input(self, action=0):
        lin = 0
        if key.is_pressed("w"):
            lin = 1
        steering = 0
        if key.is_pressed("a"):
            steering -= 1
        if key.is_pressed("d"):
            steering += 1
        return lin, steering

    def draw(self):
        for line in self.lines:
            pg.draw.line(self.parent.screen, (255, 127, 0), line[0](), line[1](), 2)"""