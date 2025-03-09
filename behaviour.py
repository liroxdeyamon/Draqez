import random
import math
import pygame
import copy

from Draqez.classes import Particle
from config import *
from auxilium import *
from managers import *
from registries import *

class Controller:
    def __init__(self, entitiesManager, entity):
        self.entitiesManager = entitiesManager
        self.entity = entity

    def update(self, DT):
        pass

    def inputs(self):
        pass

class DasherBehaviour(Controller):
    def __init__(self, entitiesManager, entity):
        super().__init__(entitiesManager, entity)

class ShooterBehaviour(Controller):
    def __init__(self, entitiesManager, entity):
        super().__init__(entitiesManager, entity)
        self.min_distance = random.randint(100,200)
        self.max_distance = random.randint(200,300)

    def inputs(self):
        returning = {}
        for i in sorted(self.entitiesManager.entities, key=lambda i: distance(*self.entity.position, *i.position)):
            if i.team == self.entity.team:
                continue
            if distance(*self.entity.position, *i.position) < self.min_distance:
                returning["horizontal"], returning["vertical"] = pos_by_angle(0,0, get_angle(*i.position, *self.entity.position), 1)
            elif distance(*self.entity.position, *i.position) > self.max_distance:
                returning["horizontal"], returning["vertical"] = pos_by_angle(0,0, get_angle(*self.entity.position, *i.position), 1)
            returning["shooting"] = True
            returning["shoot_pos"] = i.position
            break
        return returning



class PlayerController(Controller):
    def __init__(self, inputManager):
        super().__init__(None, None)
        self.inputManager = inputManager

    def inputs(self):
        return {
            "horizontal": int(self.inputManager.keyPressed(pygame.K_d))-int(self.inputManager.keyPressed(pygame.K_a)),
            "vertical": int(self.inputManager.keyPressed(pygame.K_s))-int(self.inputManager.keyPressed(pygame.K_w)),
            "charge": self.inputManager.mousePressed(self.inputManager.MOUSE_LEFT),
            "shoot": self.inputManager.mouseDownOnce(self.inputManager.MOUSE_LEFT),
            "shoot_pos": pygame.mouse.get_pos()
        }