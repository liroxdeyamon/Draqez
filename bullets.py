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
    def __init__(self, position, velocity, team, damage, size, speed, color, entitiesManager, bulletsManager, particlesManager, start_color = (255,255,255), lifetime = 10):
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

    def render(self, surface):
        pass

    def create(self, position, target_position):
        pass

class Arrow(Bullet):
    def __init__(self, position, velocity, team, damage, size, speed, color, entitiesManager, bulletsManager, particlesManager):
        super().__init__(position, velocity, team, damage, size, speed, color, entitiesManager, bulletsManager, particlesManager)

    def update(self, DT):
        super().update(DT)
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
        bullet = copy.deepcopy(self)
        bullet.position = position
        bullet.velocity = list(pos_by_angle(0,0,get_angle(*position, *target_position), 1))
        return bullet