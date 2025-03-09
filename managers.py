import random
import math
import pygame
import copy
from config import *
from auxilium import *

class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    GRAY = (128, 128, 128)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    PINK = (255, 192, 203)
    BROWN = (165, 42, 42)
    GOLD = (255, 215, 0)
    SILVER = (192, 192, 192)

    @classmethod
    def random(cls):
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    @classmethod
    def lerp(cls, color1, color2, t):
        return clamp(lerp(color1[0], color2[0], t), 0, 255), clamp(lerp(color1[1], color2[1], t), 0, 255), clamp(lerp(color1[2], color2[2], t), 0, 255)


class InputManager:
    MOUSE_LEFT = 1
    MOUSE_MIDDLE = 2
    MOUSE_RIGHT = 3
    MOUSE_SCROLL_UP = 4
    MOUSE_SCROLL_DOWN = 5

    def __init__(self):
        self.keys_pressed = set()
        self.keys_just_pressed = set()
        self.keys_just_released = set()
        self.mouse_buttons_pressed = set()
        self.mouse_buttons_just_pressed = set()
        self.mouse_buttons_just_released = set()

        self.mods = 0
        self.mods_just_pressed = set()
        self.mods_just_released = set()

    def update(self, events):
        keys = pygame.key.get_pressed()
        new_mods = pygame.key.get_mods()

        for key in range(len(keys)):
            if keys[key]:
                if key not in self.keys_pressed:
                    self.keys_just_pressed.add(key)
                self.keys_pressed.add(key)
            elif key in self.keys_pressed:
                self.keys_pressed.remove(key)
                self.keys_just_released.add(key)

        if new_mods != self.mods:
            for mod in (pygame.KMOD_SHIFT, pygame.KMOD_CTRL, pygame.KMOD_ALT):
                if new_mods & mod and not self.mods & mod:
                    self.mods_just_pressed.add(mod)
                if self.mods & mod and not new_mods & mod:
                    self.mods_just_released.add(mod)
            self.mods = new_mods

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                button = event.button
                if button not in self.mouse_buttons_pressed:
                    self.mouse_buttons_just_pressed.add(button)
                self.mouse_buttons_pressed.add(button)
            elif event.type == pygame.MOUSEBUTTONUP:
                button = event.button
                if button in self.mouse_buttons_pressed:
                    self.mouse_buttons_pressed.remove(button)
                self.mouse_buttons_just_released.add(button)


    def keyPressed(self, key):
        return key in self.keys_pressed

    def keyDownOnce(self, key):
        return key in self.keys_just_pressed

    def keyUpOnce(self, key):
        return key in self.keys_just_released


    def mousePressed(self, button):
        return button in self.mouse_buttons_pressed

    def mouseDownOnce(self, button):
        return button in self.mouse_buttons_just_pressed

    def mouseUpOnce(self, button):
        return button in self.mouse_buttons_just_released


    def shiftPressed(self):
        return self.mods & pygame.KMOD_SHIFT

    def shiftDownOnce(self):
        return pygame.KMOD_SHIFT in self.mods_just_pressed

    def shiftUpOnce(self):
        return pygame.KMOD_SHIFT in self.mods_just_released


    def ctrlPressed(self):
        return self.mods & pygame.KMOD_CTRL

    def ctrlDownOnce(self):
        return pygame.KMOD_CTRL in self.mods_just_pressed

    def ctrlUpOnce(self):
        return pygame.KMOD_CTRL in self.mods_just_released


    def altPressed(self):
        return self.mods & pygame.KMOD_ALT

    def altDownOnce(self):
        return pygame.KMOD_ALT in self.mods_just_pressed

    def altUpOnce(self):
        return pygame.KMOD_ALT in self.mods_just_released


    def final(self):
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.mouse_buttons_just_pressed.clear()
        self.mouse_buttons_just_released.clear()
        self.mods_just_pressed.clear()
        self.mods_just_released.clear()


class HealthManager:
    def __init__(self, max_health, health = 0, shield = 0, shield_enabled = True, invincible = False, invincible_time_on_hit = 5, safe_segments = 0):
        self.health = health if health > 0 else max_health
        self.rallying_health = health
        self.max_health = max_health
        self.shield = shield
        self.shield_enabled = shield_enabled

        self.invincible = invincible
        self.last_hit = 0
        self.invincible_time = 0
        self.invincible_time_on_hit = max(0, invincible_time_on_hit)

        self.safe_segments = safe_segments
        self.safe_segments_enabled = self.safe_segments > 0

    def update(self, DT):
        self.health = clamp(self.health, 0, self.max_health)
        self.shield = clamp(self.shield, 0, self.max_health)
        self.rallying_health = max(self.rallying_health - DT*1.2, self.health)
        self.invincible_time = max(self.invincible_time - DT, 0)
        self.last_hit = lerp(self.last_hit, 0, 0.1)

    def percentage(self):
        return self.health/self.max_health

    def rallying_percentage(self):
        return self.rallying_health/self.max_health

    def shield_percentage(self):
        return self.shield/self.max_health

    def is_invincible(self):
        return self.invincible or self.invincible_time > 0

    def is_dead(self):
        return not self.is_invincible() and self.health <= 0

    def damage(self, value, forced = False):
        if value == 0:
            return False
        if value > 0 and self.is_invincible() and not forced:
            return False
        if value < 0 and self.percentage() >= 1:
            return False

        hit_damage = value
        segments = 0
        if value > 0:
            if self.shield_enabled and self.shield > 0:
                absorbed = min(self.shield, hit_damage)
                hit_damage -= absorbed
                self.shield -= absorbed
            if self.safe_segments_enabled:
                hit_damage, segments = calculate_damage(self.health, self.max_health, self.safe_segments, hit_damage)

        self.health -= hit_damage

        if value > 0:
            self.last_hit = 10
            self.invincible_time = self.invincible_time_on_hit * 3 if segments >= 1 else 1
        else:
            self.last_hit = -10
            self.rallying_health -= abs(value/2)

    def heal(self, value):
        return self.damage(-value)

    def rallying_heal(self, value):
        if self.rallying_health <= self.health:
            return False
        return self.damage(-value/2)


class RenderableHealthManager(HealthManager):
    def __init__(self, max_health, health=0, shield=0, shield_enabled=True, invincible=False, invincible_time_on_hit=5,
                 safe_segments=10, base_color=(255, 255, 255), empty_color=(50, 50, 50), damage_color=(255, 0, 0),
                 heal_color=(50, 255, 50), shield_enabled_color=(0, 50, 255), shield_disabled_color=(70, 70, 70),
                 rallying_color=(100, 0, 0)):

        super().__init__(max_health, health, shield, shield_enabled, invincible, invincible_time_on_hit, safe_segments)
        self.dynamic_health_percentage = 0
        self.dynamic_shield_percentage = 0

        self.base_color = base_color
        self.empty_color = empty_color
        self.damage_color = damage_color
        self.heal_color = heal_color
        self.shield_enabled_color = shield_enabled_color
        self.shield_disabled_color = shield_disabled_color
        self.rallying_color = rallying_color

        self.width = 300
        self.height = 30

    # Base
    def update(self, DT):
        super().update(DT)

        self.dynamic_health_percentage = math.ceil(lerp(self.dynamic_health_percentage, self.percentage(), 0.2) * 1000) / 1000
        self.dynamic_shield_percentage = math.ceil(lerp(self.dynamic_shield_percentage, self.shield_percentage(), 0.2) * 1000) / 1000


    def render(self, surface):
        if not self.safe_segments_enabled or self.safe_segments <= 0:
            health = self.dynamic_health_percentage * self.width
            shield_width = self.dynamic_shield_percentage * self.width
            rallying_width = self.rallying_percentage() * self.width

            pygame.draw.polygon(surface, self.shield_color(), bar_polygon(10 + self.width, 10, shield_width, self.height))
            pygame.draw.polygon(surface, self.empty_color, bar_polygon(10, 10, self.width, self.height))
            pygame.draw.polygon(surface, self.rallying_color, bar_polygon(10, 10, rallying_width, self.height))
            pygame.draw.polygon(surface, self.health_color(), bar_polygon(10, 10, health, self.height))
            return

        if self.dynamic_shield_percentage > 0.05: pygame.draw.polygon(surface, self.shield_color(), bar_polygon(14 + self.width, 10, self.dynamic_shield_percentage * self.width, self.height))
        draw_segmented_bar(surface, 10, 10, self.width, self.height, self.safe_segments, self.max_health, self.max_health, self.empty_color)
        draw_segmented_bar(surface, 10, 10, self.width, self.height, self.safe_segments, self.max_health*self.rallying_percentage(), self.max_health, self.rallying_color)
        draw_segmented_bar(surface, 10, 10, self.width, self.height, self.safe_segments, self.max_health*self.dynamic_health_percentage, self.max_health, self.health_color())




    # Percentage



    # Damage


    # Colors
    def health_color(self):
        if self.last_hit > 0.01:
            return Color.lerp(self.base_color, self.damage_color, abs(self.last_hit)/10)
        elif self.last_hit < -0.01:
            return Color.lerp(self.base_color, self.heal_color, abs(self.last_hit)/10)
        return self.base_color

    def shield_color(self):
        if self.shield_enabled:
            return self.shield_enabled_color
        return self.shield_disabled_color



class EntitiesManager:
    def __init__(self):
        self.entities = []

    def update(self, DT):
        for i in self.entities:
            i.update(DT)
            if i.healthManager.is_dead():
                self.remove(i)

    def render(self, screen):
        for i in self.entities:
            i.render(screen)

    def spawn(self, obj):
        self.entities.append(obj)

    def remove(self, obj):
        self.entities.remove(obj)

class BulletsManager:
    def __init__(self):
        self.player = None
        self.bullets = []

    def update(self, DT):
        for i in self.bullets:
            i.update(DT)
            if i.lifetime <= 0:
                # self.remove(i)
                pass
    def render(self, screen):
        for i in self.bullets:
            i.render(screen)

    def spawn(self, obj):
        self.bullets.append(obj)

    def remove(self, obj):
        self.bullets.remove(obj)


class ParticlesManager:
    def __init__(self):
        self.particles = []

    def update(self, DT):
        for i in self.particles:
            i.update(DT)
            if i.lifetime <= 0:
                self.remove(i)

    def render(self, screen):
        for i in self.particles:
            i.render(screen)

    def spawn(self, obj):
        self.particles.append(obj)

    def remove(self, obj):
        self.particles.remove(obj)