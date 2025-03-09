import random
import math
import pygame
import copy
from config import *
from managers import *
from auxilium import *
from registries import *

class Item:
    def __init__(self, texture_surface, settings = None):
        self.texture_surface = texture_surface
        self.settings = copy.deepcopy(settings)

class Particle:
    def __init__(self, position, size, lifetime, color = None, velocity = None):
        self.position = position
        self.size = size
        self.lifetime = lifetime
        self.start_lifetime = lifetime
        self.color = color if color is not None else Color.WHITE
        self.velocity = velocity if velocity is not None else [0,0]

    def update(self, DT):
        self.position, self.velocity = process_velocity(DT, self.position, self.velocity)
        self.lifetime-=DT

    def render(self, surface):
        pygame.draw.circle(surface, self.color, self.position, max(1, int(self.size*(self.lifetime/self.start_lifetime))))