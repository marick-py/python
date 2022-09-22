from timeit import timeit
import keyboard as key
import random as rnd
import numpy as np
import mouse as ms
import time as tm
from e2D import *

class Mouse:
    def __init__(self) -> None:
        self.position = Vector2D(info=ms.get_position())
        self.rotation = -90
        self.acceleration = 0
        self.max_steering = 4
        self.steering = 0
        self.steering_adj = 0.7
        self.dump = 0.9
        self.max_speed = 7
        self.accel_incr = 0.25

    def phys(self):
        velocity, steering = self.input()

    #   velocity
        self.acceleration += velocity * self.accel_incr
        if not (-self.max_speed <= self.acceleration <= self.max_speed):
            self.acceleration = -self.max_speed if self.acceleration < 0 else self.max_speed
        self.position.set(info=self.position.point_from_degs(self.rotation, self.acceleration))
        if velocity == 0:
            self.acceleration *= self.dump

    #   steering
        if velocity > 0:
            self.steering += steering
        elif velocity < 0:
            self.steering -= steering
        self.rotation += self.steering
        if not (-self.max_steering <= self.steering <= self.max_steering):
            self.steering = -self.max_steering if self.steering < 0 else self.max_steering
        if self.steering != 0:
            self.steering *= self.steering_adj    
        
        ms.move(self.position.x, self.position.y)
            

    def input(self):
        velocity = 0
        if key.is_pressed("w"):
            velocity += 1
        if key.is_pressed("s"):
            velocity -= 1
        
        steering = 0
        if key.is_pressed("a"):
            steering -= 1
        if key.is_pressed("d"):
            steering += 1
        return velocity, steering

mouse = Mouse()
fps = 60

while not key.is_pressed("x"):
    time = timeit(mouse.phys, number=1, globals=globals())
    tm.sleep(1/fps - time)
