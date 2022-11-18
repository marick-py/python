from typing import Union
import numpy as _np
import math as _mt
import random as _rnd

_NoneType = type(None)

class Vector3D:
    use_numpy_as_default_env_option = False
    def __init__(self, x:Union[int,float]=0, y:Union[int,float]=0, z:Union[int,float]=0, info:Union[_NoneType,list,tuple]=None) -> None:
        if info != None:
            x, y, z = self.__get_info(info)
        self.x = x
        self.y = y
        self.z = z

    def move(self, x:Union[int,float]=0, y:Union[int,float]=0, z:Union[int,float]=0, info:Union[_NoneType,list,tuple]=None) -> None:
        if info != None:
            x, y, z = self.__get_info(info)
        self.x += x
        self.y += y
        self.z += z

    def set(self, x:Union[_NoneType,int,float]=None, y:Union[_NoneType,int,float]=None, z:Union[_NoneType,int,float]=None, info:Union[_NoneType,list,tuple]=None) -> None:
        if x != None:
            self.x = x
        if y != None:
            self.y = y
        if z != None:
            self.z = z
        if info != None:
            self.x, self.y, self.z = self.__get_info(info)
    
    def distance_to(self, object, squared:bool=True) -> Union[int, float]:
        if not isinstance(object, Vector3D): object = Vector3D(info=object)
        d = (self.x - object.x)**2 + (self.y - object.y)**2 + (self.z - object.z)**2
        return (d**(1/2) if squared else d)

    def angle_to(self, object) -> Union[int, float]:
        if not isinstance(object, Vector3D): object = Vector3D(info=object)
        x,y,z = self - object
        sqrt = (x**2+y**2+z**2)**(1/2)
        distance = self.distance_to(object) / sqrt
        alpha = distance * x
        beta = distance * y
        gamma = distance * z
        return alpha, beta, gamma
    #     return (_np.arctan2(object.y - self.y, object.x - self.x) * 180 / 3.141592653589793) if self.use_numpy_as_default_env_option else (_mt.atan2(object.y - self.y, object.x - self.x) * 180 / 3.141592653589793)

    # def point_from_degs(self, degs:Union[int,float], radius:Union[int,float]):
    #     rad = degs / 180 * 3.141592653589793
    #     x = radius * (_np.cos(rad) if self.use_numpy_as_default_env_option else _mt.cos(rad)) + self.x
    #     y = radius * (_np.sin(rad) if self.use_numpy_as_default_env_option else _mt.sin(rad)) + self.y
    #     return Vector3D(x, y)

    # def copy(self):
    #     return Vector3D(self.x, self.y)

    # def absolute_round(self, n=1):
    #     s_abs = self.abs()
    #     return self.no_zero_div_error(s_abs, "zero") * n

    # def randomize(start=None, end=None):
    #     if not isinstance(start, Vector3D):
    #         if type(start) in (int, float): start = Vector3D(start, start)
    #         elif type(start) in (tuple, list): start = Vector3D(info=start)
    #         elif type(start) == _NoneType: start = Vector3D(0,0)
    #         else: raise Exception(f"\nArg start must be in [Vector3D, int, float, tuple, list] not a [{type(start)}]\n")
    #     if not isinstance(end, Vector3D):
    #         if type(end) in (int, float): end = Vector3D(end, end)
    #         elif type(end) in (tuple, list): end = Vector3D(info=end)
    #         elif type(end) == _NoneType: end = Vector3D(1,1)
    #         else: raise Exception(f"\nArg end must be in [Vector3D, int, float, tuple, list] not a [{type(end)}]\n")
    #     return start + (V2(_np.random.random(), _np.random.random()) if self.use_numpy_as_default_env_option else V2(_rnd.random(), _rnd.random())) * (end - start)

    # def mid_point_to(self, *objects):
    #     return sum(list(objects) + [self]) / (len(objects)+1)

    # # V2(x,y) | [(V2(x1,y1), V2(x2,y2)), (V2(x3,y3), V2(x4,y4))]
    # def inter_points(self, self_final_point, lines:list[tuple], sort:bool=False):
    #     ray = self() + self_final_point()
    #     def lineLineIntersect(P0, P1, Q0, Q1):
    #         d = (P1[0]-P0[0]) * (Q1[1]-Q0[1]) + (P1[1]-P0[1]) * (Q0[0]-Q1[0])
    #         if d == 0:
    #             return None
    #         t = ((Q0[0]-P0[0]) * (Q1[1]-Q0[1]) +
    #              (Q0[1]-P0[1]) * (Q0[0]-Q1[0])) / d
    #         u = ((Q0[0]-P0[0]) * (P1[1]-P0[1]) +
    #              (Q0[1]-P0[1]) * (P0[0]-P1[0])) / d
    #         if 0 <= t <= 1 and 0 <= u <= 1:
    #             return round(P1[0] * t + P0[0] * (1-t)), round(P1[1] * t + P0[1] * (1-t))
    #         return None
    #     collisions = [V2(info=line) for line in [lineLineIntersect(
    #         line1[1](), line1[0](), ray[:2], ray[2:]) for line1 in lines] if line]
    #     if sort:
    #         collisions.sort(key=lambda x: self.distance_to(x, False))
    #     return collisions

    # def normalize(self, max:Union[int,float]=1, min:Union[int,float]=0):
    #     return Vector3D(min, min).point_from_degs(Vector3D(min, min).angle_to(self), max) if Vector3D(min, min).distance_to(self) != 0 else VectorZero.copy()

    # def no_zero_div_error(self, n, error_mode="zero"):
    #     if type(n) in (int, float):
    #         if n == 0:
    #             return Vector3D(0 if error_mode == "zero" else (self.x if error_mode == "null" else _np.nan), 0 if error_mode == "zero" else (self.y if error_mode == "null" else _np.nan))
    #         else:
    #             return self / n
    #     elif isinstance(n, Vector3D):
    #         return Vector3D((0 if error_mode == "zero" else (self.x if error_mode == "null" else _np.nan)) if n.x == 0 else self.x / n.x, (0 if error_mode == "zero" else (self.y if error_mode == "null" else _np.nan)) if n.y == 0 else self.y / n.y)
    #     elif type(n) in (list, tuple):
    #         n = Vector3D(info=n)
    #         return Vector3D((0 if error_mode == "zero" else (self.x if error_mode == "null" else _np.nan)) if n.x == 0 else self.x / n.x, (0 if error_mode == "zero" else (self.y if error_mode == "null" else _np.nan)) if n.y == 0 else self.y / n.y)
    #     else:
    #         raise Exception(f"\nArg n must be in [Vector3D, int, float, tuple, list] not a [{type(n)}]\n")

    def float(self):
        return self.__float__()

    def __get_info(self, info):
        if isinstance(info, Vector3D):
            return info()
        elif type(info) in (float, list):
            return info
        else:
            raise Exception(f"\nUnknown info format [{type(info)}]... accepted formats: [float, list, Vector3D]\n")

    def __str__(self) -> str:
        return f"{self.x}-{self.y}-{self.z}"

    def __sub__(self, object):
        if not isinstance(object, Vector3D): object = Vector3D(info=object)
        return Vector3D(self.x - object.x, self.y - object.y, self.z - object.z)

    def __add__(self, object):
        if not isinstance(object, Vector3D): object = Vector3D(info=object)
        return Vector3D(self.x + object.x, self.y + object.y, self.z + object.z)

    def __mod__(self, object):
        if not isinstance(object, Vector3D): object = Vector3D(info=object)
        return Vector3D(self.x % object.x, self.y % object.y, self.z % object.z)

    def __radd__(self, object):
        return self.__add__(object)

    def __repr__(self) -> str:
        return f"x:{self.x}\ty:{self.y}\tz:{self.z}"

    def __call__(self, need_tuple=False) -> Union[list,tuple]:
        return (self.x, self.y, self.z) if need_tuple else [self.x, self.y, self.z]

    def __truediv__(self, object):
        if not isinstance(object, Vector3D): object = Vector3D(info=object)
        return Vector3D(self.x / object.x, self.y / object.y, self.z / object.z)

    def __floordiv__(self, object):
        if not isinstance(object, Vector3D): object = Vector3D(info=object)
        return Vector3D(self.x // object.x, self.y // object.y, self.z // object.z)
    
    def __abs__(self):
        return Vector3D(abs(self.x), abs(self.y), abs(self.z))

    def __round__(self, n:Union[int,float]=1):
        if not isinstance(n, Vector3D): n = Vector3D(info=n)
        return Vector3D(round(self.x / n.x) * n.x, round(self.y / n.y) * n.y, round(self.z / n.z) * n.z)

    def __floor__(self, n:Union[int,float]=1):
        if not isinstance(n, Vector3D): n = Vector3D(info=n)
        return (Vector3D(_np.floor(self.x / n.x) * n.x, _np.floor(self.y / n.y) * n.y, _np.floor(self.z / n.z) * n.z)) if self.use_numpy_as_default_env_option else (Vector3D(_mt.floor(self.x / n.x) * n.x, _mt.floor(self.y / n.y) * n.y, _mt.floor(self.z / n.z) * n.z))

    def __ceil__(self, n:Union[int,float]=1):
        if not isinstance(n, Vector3D): n = Vector3D(info=n)
        return (Vector3D(_np.ceil(self.x / n.x) * n.x, _np.ceil(self.y / n.y) * n.y, _np.ceil(self.z / n.z) * n.z)) if self.use_numpy_as_default_env_option else (Vector3D(_mt.ceil(self.x / n.x) * n.x, _mt.ceil(self.y / n.y) * n.y, _mt.ceil(self.z / n.z) * n.z))

    def __mul__(self, n):
        if not isinstance(object, Vector3D): object = Vector3D(info=object)
        return Vector3D(self.x * object.x, self.y * object.y, self.z * object.z)

    def __float__(self):
        return Vector3D(float(self.x), float(self.y), float(self.z))

    def __pow__(self, n):
        if not isinstance(object, Vector3D): object = Vector3D(info=object)
        return Vector3D(self.x ** object.x, self.y ** object.y)

    def __getitem__(self, n):
        if n in [0, "x"]:
            return self.x
        elif n in [1, "y"]:
            return self.y
        elif n in [2, "z"]:
            return self.z
        else:
            raise IndexError("V3 has only x,y,z...")


V3 = Vector3D
V3inf = V3(float('inf'), float('inf'), float('inf'))
V3z = Vector3Zero = Vector3D()
