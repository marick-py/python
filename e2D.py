import numpy as _np

class Vector2D:
    def __init__(self, x=0, y=0, info=None) -> None:
        if info != None:
            x, y = self.__get_info(info)
        self.x = x
        self.y = y

    def move(self, x=0, y=0, info=None):
        if info != None:
            x, y = self.__get_info(info)
        self.x += x
        self.y += y
    
    def set(self, x=None, y=None, info=None):
        if x != None:
            self.x = x
        if y != None:
            self.y = y
        if info != None:
            self.x, self.y = self.__get_info(info)

    def distance_to(self, object, squared=True):
        d = (self.x - object.x)**2 + (self.y - object.y)**2
        return (d**(1/2) if squared else d)
    
    def angle_to(self, object):
        return _np.arctan2(object.y - self.y, object.x - self.x) * 180 / 3.141592653589793
    
    def point_from_degs(self, degs, radius):
        rad =  degs / 180 * 3.141592653589793
        x = radius * _np.cos(rad) + self.x
        y = radius * _np.sin(rad) + self.y
        return Vector2D(x,y)
    
    def abs(self):
        return Vector2D(abs(self.x), abs(self.y))
    
    def round(self, n=1):
        return Vector2D(round(self.x / n) * n, round(self.y / n) * n)

    def floor(self, n=1):
        return Vector2D(_np.floor(self.x / n) * n, _np.floor(self.y / n) * n)

    def ceil(self, n=1):
        return Vector2D(_np.ceil(self.x / n) * n, _np.ceil(self.y / n) * n)

    def copy(self):
        return Vector2D(self.x, self.y)

    def absolute_round(self, n=1):
        return V2(self.x / self.abs().x if self.x != 0 else 0, self.y / self.abs().y if self.y != 0 else 0) * n

    def randomize(start=None, end=None):
        if start == None: start = Vector2D(0,0)
        if end == None: end = Vector2D(1,1)
        return start + V2(_np.random.random(),_np.random.random()) *(end - start)

    def mid_point_to(self, *objects):
        return sum(list(objects) + [self]) / (len(objects)+1)

    def inter_points(self, self_final_point, lines, sort=False): # V2(x,y) | [(V2(x1,y1), V2(x2,y2)), (V2(x3,y3), V2(x4,y4))]
        ray = self() + self_final_point()
        def lineLineIntersect(P0, P1, Q0, Q1):
            d = (P1[0]-P0[0]) * (Q1[1]-Q0[1]) + (P1[1]-P0[1]) * (Q0[0]-Q1[0]) 
            if d == 0: return None
            t = ((Q0[0]-P0[0]) * (Q1[1]-Q0[1]) + (Q0[1]-P0[1]) * (Q0[0]-Q1[0])) / d
            u = ((Q0[0]-P0[0]) * (P1[1]-P0[1]) + (Q0[1]-P0[1]) * (P0[0]-P1[0])) / d
            if 0 <= t <= 1 and 0 <= u <= 1: return round(P1[0] * t + P0[0] * (1-t)), round(P1[1] * t + P0[1] * (1-t))
            return None
        collisions = [V2(info=line) for line in [lineLineIntersect(line1[1](), line1[0](), ray[:2], ray[2:]) for line1 in lines] if line]
        if sort: collisions.sort(key= lambda x: self.distance_to(x, False))
        return collisions
    
    def normalize(self, max=1, min=0):
        return V2(min, min).point_from_degs(V2(min, min).angle_to(self), max) if V2(min, min).distance_to(self) != 0 else V2z.copy()

    def no_zero_div_error(self, n, mode="zero"):
        if type(n) in (int, float):
            if n == 0:
                return Vector2D(0 if mode == "zero" else (self.x if mode == "null" else _np.nan), 0 if mode == "zero" else (self.y if mode == "null" else _np.nan))
            else:
                return self / n
        else:
            return Vector2D((0 if mode == "zero" else (self.x if mode == "null" else _np.nan)) if n.x == 0 else self.x / n.x, (0 if mode == "zero" else (self.y if mode == "null" else _np.nan)) if n.y == 0 else self.y / n.y)

    def __get_info(self, info):
        if isinstance(info, Vector2D):
            return info()
        else: return info

    def __str__(self):
        return f"{self.x}.{self.y}"

    def __sub__(self, object):
        if type(object) in (int, float):
            return Vector2D(self.x - object, self.y - object)
        else:
            return Vector2D(self.x - object.x, self.y - object.y)

    def __add__(self, object):
        if type(object) in (int, float):
            return Vector2D(self.x + object, self.y + object)
        else:
            return Vector2D(self.x + object.x, self.y + object.y)
    
    def __mod__(self, object):
        if type(object) in (int, float):
            return Vector2D(self.x % object, self.y % object)
        else:
            return Vector2D(self.x % object.x, self.y % object.y)

    def __radd__(self, object):
        return self.__add__(object)

    def __repr__(self) -> str:
        return f"x:{self.x}\ty:{self.y}"
    
    def __call__(self, need_tuple=False):
        return (self.x, self.y) if need_tuple else [self.x, self.y]
    
    def __truediv__(self, n):
        if type(n) in (int, float):
            return Vector2D(self.x / n, self.y / n)
        else:
            return Vector2D(self.x / n.x, self.y / n.y)
    
    def __mul__(self, n):
        if type(n) in (int, float):
            return Vector2D(self.x * n, self.y * n)
        else:
            return Vector2D(self.x * n.x, self.y * n.y)
    
    def __pow__(self, n):
        if type(n) in (int, float):
            return Vector2D(self.x ** n, self.y ** n)
        else:
            return Vector2D(self.x ** n.x, self.y ** n.y)
    
    def __getitem__(self, n):
        if n in [0,"x"]: return self.x
        elif n in [1,"y"]: return self.y
        else: raise IndexError("V2 has only x,y...")
    
V2 = Vector2D

V2z = VectorZero = Vector2D()

def color_fade(starting_c, final_c, index, max_index):
    return tuple( (starting_c[i] - final_c[i]) / max_index * (max_index - index) + final_c[i] for i in range(3))

def avg_position(*objects):
    return sum(list(objects)) / (len(objects))

def get_points(position, size, rotation=0, pos_in_middle=True, return_list=False, clockwise_return=False):
    if pos_in_middle:
        A,B,C,D = [ position.point_from_degs(rotation + V2z.angle_to(size/-2),                 V2z.distance_to(size/-2)),
                    position.point_from_degs(rotation + V2z.angle_to(V2(size.x, -1*size.y)/2), V2z.distance_to(V2(size.x, -1*size.y)/2)),
                    position.point_from_degs(rotation + V2z.angle_to(V2(-1*size.x, size.y)/2), V2z.distance_to(V2(-1*size.x, size.y)/2)),
                    position.point_from_degs(rotation + V2z.angle_to(size/2),                  V2z.distance_to(size/2)) ]
    else:
        A,B,C,D = [ position.copy(),
                    position.point_from_degs(rotation + V2z.angle_to(V2(size.x, 0)), V2z.distance_to(V2(size.x, 0))),
                    position.point_from_degs(rotation + V2z.angle_to(V2(0, size.y)), V2z.distance_to(V2(0, size.y))),
                    position.point_from_degs(rotation + V2z.angle_to(size),          V2z.distance_to(size)) ]
    points = (A,B,C,D) if not clockwise_return else (A,B,D,C)
    return points if not return_list else [x() for x in points]

def get_lines(position, size, rotation=0, pos_in_middle=True):
    A,B,C,D = get_points(position, size, rotation, pos_in_middle)
    return [[A,B], [A,C], [C,D], [D,B]]


"""
import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
from e2D import *

import pygame as pg

seed = rnd.random()
rnd.seed(seed)

pg.init()
pg.font.init()
LucidaConsole16 = pg.font.SysFont('lucidaconsole', 16)
LucidaConsole32 = pg.font.SysFont('lucidaconsole', 32)
LucidaConsole64 = pg.font.SysFont('lucidaconsole', 64)

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def print_fps_info(self):
        curr_fps = self.clock.get_fps()
        fps_surface = LucidaConsole16.render(f"fps: {str(curr_fps)}", False, (150, 150, 150))
        self.screen.blit(fps_surface, (self.screen_size / 100)())
        if curr_fps != 0:
            self.delta = 1 / self.clock.get_fps()
            fps_surface = LucidaConsole16.render(f"len: {str(self.delta)}", False, (150, 150, 150))
            self.screen.blit(fps_surface, (self.screen_size / 100 + V2(0, self.screen_size.y / 100 + 10))())
        else:
            self.delta = 0

    def draw(self):
        self.clock.tick(0)
        self.clear()
        self.print_fps_info()

        pg.display.update()
    
    def frame(self):
        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

env = Env()

while not (env.quit or key.is_pressed("x")):
    env.frame()
"""