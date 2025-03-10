import random
import math
import pygame
import copy

from config import *
from auxilium import *
from managers import *
from registries import *
from bullets import *

class Weapon:
    def __init__(self, ammo, charge_time, cooldown_time, entitiesManager, bulletsManager, particlesManager, owner, bullet, knockback = -10):
        self.ammo = self.max_ammo = max(0, ammo)
        self.charge = 0
        self.max_charge = max(0, charge_time)
        self.max_cooldown = max(0, cooldown_time)
        self.cooldown = self.max_cooldown*(1+random.random())
        self.charging = False
        self.entity = owner
        self.bullet = bullet([0,0], [0,0], self.entity.team, 1, 7, 5, self.entity.color, entitiesManager, bulletsManager, particlesManager) if bullet is not None else None
        self.entitiesManager, self.bulletsManager, self.particlesManager = entitiesManager, bulletsManager, particlesManager
        self.knockback = knockback

    def update(self, DT):
        if self.cooldown > 0:
            self.cooldown -= DT
        if not self.charging:
            self.charge = 0
        self.charging = False

    def charge_up(self, DT):
        self.charge += DT
        self.charging = True

    def shoot(self, DT, position, target_position):
        if self.bullet is None:
            return False
        if self.ammo <= 0:
            return False
        if self.max_cooldown > 0 <= self.cooldown:
            return False
        if self.max_charge > 0 and self.charge < self.max_charge:
            return False
        self.bulletsManager.spawn(self.bullet.create(position, target_position))
        self.charge = 0
        self.cooldown = self.max_cooldown
        return True

    def on_kill(self):
        pass

    def charge_percentage(self):
        return self.charge/self.max_charge if self.max_charge > 0 else 0

    def cooldown_percentage(self):
        return self.cooldown/self.max_cooldown if self.max_cooldown > 0 else 0

    def ammo_percentage(self):
        return self.ammo/self.max_ammo if self.ammo != float("inf") else 1


class Bow(Weapon):
    def __init__(self, entitiesManager, bulletsManager, particlesManager, owner):
        super().__init__(float("inf"), 30, 10, entitiesManager, bulletsManager, particlesManager, owner, Arrow)