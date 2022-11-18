from typing import Union
import numpy as _np
import math as _mt
import random as _rnd

_NoneType = type(None)

class Vector2D:
    use_numpy_as_default_env_option = False
    def __init__(self, x:Union[int,float]=0, y:Union[int,float]=0, info:Union[_NoneType,list,tuple]=None) -> None:
        if info != None:
            x, y = self.__get_info(info)
        self.x = x
        self.y = y

    def move(self, x:Union[int,float]=0, y:Union[int,float]=0, info:Union[_NoneType,list,tuple]=None) -> None:
        if info != None:
            x, y = self.__get_info(info)
        self.x += x
        self.y += y

    def set(self, x:Union[_NoneType,int,float]=None, y:Union[_NoneType,int,float]=None, info:Union[_NoneType,list,tuple]=None) -> None:
        if x != None:
            self.x = x
        if y != None:
            self.y = y
        if info != None:
            self.x, self.y = self.__get_info(info)

    def distance_to(self, object, squared:bool=True) -> Union[int, float]:
        if not isinstance(object, Vector2D): object = Vector2D(info=object)
        d = (self.x - object.x)**2 + (self.y - object.y)**2
        return (d**(1/2) if squared else d)

    def angle_to(self, object) -> Union[int, float]:
        if not isinstance(object, Vector2D): object = Vector2D(info=object)
        return (_np.arctan2(object.y - self.y, object.x - self.x) * 180 / 3.141592653589793) if self.use_numpy_as_default_env_option else (_mt.atan2(object.y - self.y, object.x - self.x) * 180 / 3.141592653589793)

    def point_from_degs(self, degs:Union[int,float], radius:Union[int,float]):
        rad = degs / 180 * 3.141592653589793
        x = radius * (_np.cos(rad) if self.use_numpy_as_default_env_option else _mt.cos(rad)) + self.x
        y = radius * (_np.sin(rad) if self.use_numpy_as_default_env_option else _mt.sin(rad)) + self.y
        return Vector2D(x, y)

    def copy(self):
        return Vector2D(self.x, self.y)

    def absolute_round(self, n=1):
        s_abs = abs(self)
        return self.no_zero_div_error(s_abs, "zero") * n

    def floor(self, n:Union[int,float]=1):
        return self.__floor__(n)

    def ceil(self, n:Union[int,float]=1):
        return self.__ceil__(n)

    def randomize(start=None, end=None):
        if not isinstance(start, Vector2D):
            if type(start) in (int, float): start = Vector2D(start, start)
            elif type(start) in (tuple, list): start = Vector2D(info=start)
            elif type(start) == _NoneType: start = Vector2D(0,0)
            else: raise Exception(f"\nArg start must be in [Vector2D, int, float, tuple, list] not a [{type(start)}]\n")
        if not isinstance(end, Vector2D):
            if type(end) in (int, float): end = Vector2D(end, end)
            elif type(end) in (tuple, list): end = Vector2D(info=end)
            elif type(end) == _NoneType: end = Vector2D(1,1)
            else: raise Exception(f"\nArg end must be in [Vector2D, int, float, tuple, list] not a [{type(end)}]\n")
        return start + (V2(_np.random.random(), _np.random.random()) if Vector2D.use_numpy_as_default_env_option else V2(_rnd.random(), _rnd.random())) * (end - start)

    def mid_point_to(self, *objects):
        return sum(list(objects) + [self]) / (len(objects)+1)

    # V2(x,y) | [(V2(x1,y1), V2(x2,y2)), (V2(x3,y3), V2(x4,y4))]
    def inter_points(self, self_final_point, lines:list[tuple], sort:bool=False, return_empty:bool=True):
        ray = self() + self_final_point()
        def lineLineIntersect(P0, P1, Q0, Q1):
            d = (P1[0]-P0[0]) * (Q1[1]-Q0[1]) + (P1[1]-P0[1]) * (Q0[0]-Q1[0])
            if d == 0:
                return None
            t = ((Q0[0]-P0[0]) * (Q1[1]-Q0[1]) +
                 (Q0[1]-P0[1]) * (Q0[0]-Q1[0])) / d
            u = ((Q0[0]-P0[0]) * (P1[1]-P0[1]) +
                 (Q0[1]-P0[1]) * (P0[0]-P1[0])) / d
            if 0 <= t <= 1 and 0 <= u <= 1:
                return round(P1[0] * t + P0[0] * (1-t)), round(P1[1] * t + P0[1] * (1-t))
            return None
        collisions = [V2(info=line) for line in [lineLineIntersect(line1[1](), line1[0](), ray[:2], ray[2:]) for line1 in lines] if line and return_empty]
        if sort:
            collisions.sort(key=lambda x: self.distance_to(x, False))
        return collisions

    def normalize(self, max:Union[int,float]=1, min:Union[int,float]=0):
        return Vector2D(min, min).point_from_degs(Vector2D(min, min).angle_to(self), max) if Vector2D(min, min).distance_to(self) != 0 else VectorZero.copy()

    def no_zero_div_error(self, n, error_mode="zero"):
        if type(n) in (int, float):
            if n == 0:
                return Vector2D(0 if error_mode == "zero" else (self.x if error_mode == "null" else _np.nan), 0 if error_mode == "zero" else (self.y if error_mode == "null" else _np.nan))
            else:
                return self / n
        elif isinstance(n, Vector2D):
            return Vector2D((0 if error_mode == "zero" else (self.x if error_mode == "null" else _np.nan)) if n.x == 0 else self.x / n.x, (0 if error_mode == "zero" else (self.y if error_mode == "null" else _np.nan)) if n.y == 0 else self.y / n.y)
        elif type(n) in (list, tuple):
            n = Vector2D(info=n)
            return Vector2D((0 if error_mode == "zero" else (self.x if error_mode == "null" else _np.nan)) if n.x == 0 else self.x / n.x, (0 if error_mode == "zero" else (self.y if error_mode == "null" else _np.nan)) if n.y == 0 else self.y / n.y)
        else:
            raise Exception(f"\nArg n must be in [Vector2D, int, float, tuple, list] not a [{type(n)}]\n")

    def float(self):
        return self.__float__()

    def __get_info(self, info):
        if isinstance(info, Vector2D):
            return info()
        elif type(info) in (tuple, list):
            return info
        elif type(info) in (int, float):
            return info, info
        else:
            raise Exception(f"\nUnknown info format [{type(info)}]... accepted formats: [float, list, int, tuples, Vector2D]\n")

    def __str__(self) -> str:
        return f"{self.x}-{self.y}"

    def __sub__(self, object):
        if not isinstance(object, Vector2D): object = Vector2D(info=object)
        return Vector2D(self.x - object.x, self.y - object.y)

    def __add__(self, object):
        if not isinstance(object, Vector2D): object = Vector2D(info=object)
        return Vector2D(self.x + object.x, self.y + object.y)

    def __mod__(self, object):
        if not isinstance(object, Vector2D): object = Vector2D(info=object)
        return Vector2D(self.x % object.x, self.y % object.y)

    def __radd__(self, object):
        return self.__add__(object)

    def __repr__(self) -> str:
        return f"x:{self.x}\ty:{self.y}"

    def __call__(self, need_tuple=False) -> Union[list,tuple]:
        return (self.x, self.y) if need_tuple else [self.x, self.y]

    def __truediv__(self, object):
        if not isinstance(object, Vector2D): object = Vector2D(info=object)
        return Vector2D(self.x / object.x, self.y / object.y)

    def __floordiv__(self, object):
        if not isinstance(object, Vector2D): object = Vector2D(info=object)
        return Vector2D(self.x // object.x, self.y // object.y)
    
    def __abs__(self):
        return Vector2D(abs(self.x), abs(self.y))

    def __round__(self, n:Union[int,float]=1):
        return Vector2D(round(self.x / n) * n, round(self.y / n) * n)

    def __floor__(self, n:Union[int,float]=1):
        return (Vector2D(_np.floor(self.x / n) * n, _np.floor(self.y / n) * n)) if self.use_numpy_as_default_env_option else (Vector2D(_mt.floor(self.x / n) * n, _mt.floor(self.y / n) * n))

    def __ceil__(self, n:Union[int,float]=1):
        return (Vector2D(_np.ceil(self.x / n) * n, _np.ceil(self.y / n) * n)) if self.use_numpy_as_default_env_option else (Vector2D(_mt.ceil(self.x / n) * n, _mt.ceil(self.y / n) * n))

    def __mul__(self, object):
        if not isinstance(object, Vector2D): object = Vector2D(info=object)
        return Vector2D(self.x * object.x, self.y * object.y)

    def __pow__(self, object):
        if not isinstance(object, Vector2D): object = Vector2D(info=object)
        return Vector2D(self.x ** object.x, self.y ** object.y)
    
    def __float__(self):
        return Vector2D(float(self.x), float(self.y))

    def __getitem__(self, n):
        if n in [0, "x"]:
            return self.x
        elif n in [1, "y"]:
            return self.y
        else:
            raise IndexError("V2 has only x,y...")

V2 = Vector2D
V2inf = V2(float('inf'), float('inf'))
V2z = VectorZero = Vector2D()

def color_fade(starting_c:Union[tuple,list], final_c:Union[tuple,list], index:Union[int,float], max_index:Union[int,float]) -> tuple:
    return tuple((starting_c[i] - final_c[i]) / max_index * (max_index - index) + final_c[i] for i in range(3))

def avg_position(*objects) -> Vector2D:
    return sum(list(objects)) / (len(objects))

def get_points(position:Vector2D, size:Vector2D, rotation:Union[int,float]=0, pos_in_middle:bool=True, return_list:bool=False, clockwise_return:bool=False):
    if pos_in_middle:
        A, B, C, D = [position.point_from_degs(rotation + V2z.angle_to(size/-2),                 V2z.distance_to(size/-2)),
                      position.point_from_degs(rotation + V2z.angle_to(V2(size.x, -1*size.y)/2), V2z.distance_to(V2(size.x, -1*size.y)/2)),
                      position.point_from_degs(rotation + V2z.angle_to(V2(-1*size.x, size.y)/2), V2z.distance_to(V2(-1*size.x, size.y)/2)),
                      position.point_from_degs(rotation + V2z.angle_to(size/2),                  V2z.distance_to(size/2))]
    else:
        A, B, C, D = [position.copy(),
                      position.point_from_degs(rotation + V2z.angle_to(V2(size.x, 0)), V2z.distance_to(V2(size.x, 0))),
                      position.point_from_degs(rotation + V2z.angle_to(V2(0, size.y)), V2z.distance_to(V2(0, size.y))),
                      position.point_from_degs(rotation + V2z.angle_to(size),          V2z.distance_to(size))]
    points = (A, B, C, D) if not clockwise_return else (A, B, D, C)
    return points if not return_list else [x() for x in points]


def get_lines(position:Vector2D, size:Vector2D, rotation:Union[int,float]=0, pos_in_middle:bool=True) -> list[list, list, list, list]:
    A, B, C, D = get_points(position, size, rotation, pos_in_middle)
    return [[A, B], [A, C], [C, D], [D, B]]

"""
import random as rnd
import numpy as np
from e2D import *

import pygame as pg

seed = rnd.random()
rnd.seed(seed)

pg.init()

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
    
    def clear(self):
        self.screen.fill((0,0,0))
    
    def draw(self):
        self.clock.tick(0)
        self.clear()

        pg.display.update()
    
    def frame(self):
        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_x):
                self.quit = True
            if event.

env = Env()

while not env.quit:
    env.frame()
"""