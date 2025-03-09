import random

import pygame
import sys
from registries import *
from classes import *
from auxilium import *
from config import *
from managers import *
from entities import *

pygame.init()

VSync = True
DT = 0
FONT = pygame.font.SysFont("roboto", 25)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Draqez")
pygame.display.set_icon(random_icon(Color.random()))
clock = pygame.time.Clock()

mode = Modes.MODE_MENU

inputManager = InputManager()

entitiesManager = EntitiesManager()
# [entitiesManager.spawn(Shooter(700* random.random(),700* random.random(),10,player)) for i in range(5)]
# [entitiesManager.spawn(Dasher(700* random.random(),700* random.random(),10,player)) for i in range(5)]
# [entitiesManager.spawn(Lance(700* random.random(),700* random.random(),10,player)) for i in range(5)]
bulletsManager = BulletsManager()
particlesManager = ParticlesManager()
[entitiesManager.spawn(Shooter([700* random.random(),700* random.random()], 10, Teams.TEAM_ENEMY, entitiesManager, bulletsManager, particlesManager)) for i in range(5)]
[entitiesManager.spawn(Shooter([700* random.random(),700* random.random()], 10, Teams.TEAM_PLAYER, entitiesManager, bulletsManager, particlesManager)) for i in range(5)]
entitiesManager.spawn(Player([CW,CH], 100, Teams.TEAM_PLAYER, entitiesManager, bulletsManager, particlesManager, inputManager))

while True:
    mx, my = pygame.mouse.get_pos()
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Update
    inputManager.update(events)
    entitiesManager.update(DT)
    bulletsManager.update(DT)
    particlesManager.update(DT)


    inputManager.final()
    # Render
    screen.fill(Color.BLACK)
    particlesManager.render(screen)
    entitiesManager.render(screen)
    bulletsManager.render(screen)
    if mode == Modes.MODE_MENU:
        pass

    pygame.display.update()
    DT = clock.tick(FPS)/FPS