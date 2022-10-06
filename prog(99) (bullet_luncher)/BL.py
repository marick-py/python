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

class Bullet:
    def __init__(self, parent, initial_position, initial_velocity) -> None:
        self.parent = parent
        self.position = initial_position
        self.velocity = initial_velocity
        self.radius = 50
        self.bounce_const = -.5
        self.collision_const = .99
        self.mouse_bounce_collision = .9
    
    def draw(self):
        pg.draw.circle(self.parent.screen, (255,127,0), self.position(), self.radius, int(self.radius / 10))
        
        pg.draw.line(self.parent.screen, (255,255,255), self.position(), self.position.point_from_degs(self.position.angle_to(self.parent.mouse.position) + 180, V2z.distance_to(self.velocity + self.parent.mouse.speed * 100))(), 2)
        for circle in self.parent.bullets:
            if circle is not self:
                pg.draw.line(self.parent.screen, [255/3*2]*3, self.position(), self.position.point_from_degs(self.position.angle_to(circle.position) + 180, V2z.distance_to(self.velocity + circle.velocity * -self.bounce_const))(), 1)

    def frame(self):
        self.velocity.y += self.parent.g
        next = self.position + self.velocity / 10
        if next.y - self.radius < 0 and self.velocity.y < 0:
            self.position.y = self.radius
            self.velocity.y *= self.bounce_const
            self.velocity.x *= self.collision_const
        if next.y + self.radius > self.parent.floor and self.velocity.y > 0:
            self.position.y = self.parent.floor - self.radius
            self.velocity.y *= self.bounce_const
            self.velocity.x *= self.collision_const
        if next.x - self.radius < 0 and self.velocity.x < 0:
            self.position.x = self.radius
            self.velocity.x *= self.bounce_const
        if next.x + self.radius > self.parent.screen_size.x and self.velocity.x > 0:
            self.position.x = self.parent.screen_size.x - self.radius
            self.velocity.x *= self.bounce_const
        if self.position.distance_to(self.parent.mouse.position) < self.radius + self.parent.mouse.radius:
            self.velocity = V2z.point_from_degs(self.position.angle_to(self.parent.mouse.position) + 180, V2z.distance_to(self.velocity + self.parent.mouse.speed * 100) * self.mouse_bounce_collision)
        for circle in self.parent.bullets:
            if self.position.distance_to(circle.position) < self.radius + circle.radius and circle is not self:
                self.velocity = V2z.point_from_degs(self.position.angle_to(circle.position) + 180, V2z.distance_to(self.velocity + circle.velocity) * -self.bounce_const)
        self.position += self.velocity * self.parent.delta * 10

class Mouse:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.position = V2z.copy()
        self.speed = V2z.copy()
        self.radius = 100
        self.update()
    
    def draw(self):
        pg.draw.circle(self.parent.screen, (0,0,255), self.position(), self.radius, int(self.radius / 10))

    def update(self):
        last_pos = self.position.copy()
        self.position = V2(info=pg.mouse.get_pos())
        self.speed = (self.position - last_pos) * self.parent.delta * 100

    def is_clicked(self, key="left"):
        return ms.is_pressed(key)

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.delta = 0
        self.mouse = Mouse(self)
        self.g = 1#9.8
        self.floor = self.screen_size.y
        self.start = None
        self.bullets = []
        pg.mouse.set_visible(False)
    
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

        for bullet in self.bullets: bullet.draw()

        self.mouse.draw()
        pg.draw.line(self.screen, (255,255,255), V2(0,self.floor)(), V2(self.screen_size.x,self.floor)(), 2)

        if self.start != None:
            pg.draw.circle(self.screen, (255,0,0), self.start(), 5)
            pg.draw.circle(self.screen, (0,255,0), self.mouse.position(), 5)
            pg.draw.line(self.screen, (255,255,255), self.start(), self.mouse.position())

        pg.display.update()

    def get_input(self):
        if self.mouse.is_clicked():
            if self.start == None:
                self.start = self.mouse.position
        else:
            if self.start != None:
                return self.mouse.position - self.start
    
    def frame(self):
        self.mouse.update()
        inp = self.get_input()
        if inp != None:
            self.bullets.append(Bullet(self, self.start.copy(), inp.copy()))
            self.start = None
        for bullet in self.bullets: bullet.frame()

        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

env = Env()

while not (env.quit or key.is_pressed("x")):
    env.frame()