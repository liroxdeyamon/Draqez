import random
import math
import pygame
import copy
from config import *
from managers import *
from auxilium import *
from registries import *
from classes import *

class Bullet:
    def __init__(self, position, velocity, team, damage, size, speed, color, entitiesManager, bulletsManager, particlesManager, start_color = (255,255,255), lifetime = 100):
        self.position = position
        self.velocity = velocity
        self.team = team
        self.damage = damage
        self.size = size
        self.color = color
        self.speed = speed
        self.dynamic_color = start_color
        self.velocity = velocity
        self.lifetime = lifetime
        self.entitiesManager, self.bulletsManager, self.particlesManager = entitiesManager, bulletsManager, particlesManager

    def update(self, DT):
        self.position, self.velocity = process_velocity(DT*self.speed, self.position, self.velocity, WIDTH, HEIGHT, slow_factor=0)
        self.dynamic_color = Color.lerp(self.dynamic_color, self.color, DT/3)
        self.lifetime -= DT

    def check_collision(self):
        for i in self.entitiesManager.entities:
            if distance(*self.position, *i.position) < i.size and self.team != i.team:
                return i

    def on_death(self):
        for i in range(10):
            self.particlesManager.spawn(
                Particle(
                    [self.position[0]+random.randint(-2,2), self.position[1]+random.randint(-2,2)],
                    random.randint(1,3), 15, self.color, [random.random()*10-5,random.random()*10-5]
                )
            )

    def render(self, surface):
        pass

    def create(self, position, target_position):
        pass

class Arrow(Bullet):
    def __init__(self, position, velocity, team, damage, size, speed, color, entitiesManager, bulletsManager, particlesManager):
        super().__init__(position, velocity, team, damage, size, speed, color, entitiesManager, bulletsManager, particlesManager)
        speed = 15
        self.acceleration = 3
        self.real_speed = speed

    def update(self, DT):
        super().update(DT)
        self.speed = self.acceleration * self.real_speed
        self.acceleration = max(self.acceleration-DT/7, 1)
        if random.random() > 0.95:
            self.particlesManager.spawn(
                Particle(
                    [self.position[0]+random.randint(-2,2), self.position[1]+random.randint(-2,2)],
                    random.randint(1,3), 15, self.color, [-self.velocity[0], -self.velocity[1]]
                )
            )
    def render(self, surface):
        pygame.draw.circle(surface, self.dynamic_color, self.position, self.size)

    def create(self, position, target_position):
        return Arrow(
            list(position),
            list(pos_by_angle(0, 0, get_angle(*position, *target_position), 1)),
            self.team,
            self.damage,
            self.size,
            self.speed,
            self.color,
            self.entitiesManager,
            self.bulletsManager,
            self.particlesManager
        )