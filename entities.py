import random
import math
import pygame
import copy

from Draqez.classes import Particle
from config import *
from auxilium import *
from managers import *
from registries import *
from weapons import *
from behaviour import *
class Entity:
    def __init__(self, position, velocity, team, size, speed, healthManager, entitiesManager, bulletsManager, particlesManager, behaviour, color = None):
        self.position = position
        self.velocity = velocity
        self.team = team
        self.size = size
        self.speed = speed
        self.angle = 0
        self.color = TEAM_COLORS.get(team, (50,50,50)) if color is None else color

        self.weapons = []
        self.current_weapon = 0
        self.after_shoot = False
        self.last_shoot_position = self.position
        self.healthManager = healthManager
        self.entitiesManager, self.bulletsManager, self.particlesManager = entitiesManager, bulletsManager, particlesManager

        self.behaviour = behaviour

    def update(self, DT):
        self.position, self.velocity = process_velocity(DT, self.position, self.velocity, WIDTH, HEIGHT, True)
        self.healthManager.update(DT)
        self.behaviour.update(DT)
        inputs = self.behaviour.inputs()
        self.velocity[0]+=inputs.get("horizontal", 0)*self.speed*DT
        self.velocity[1]+=inputs.get("vertical", 0)*self.speed*DT
        if inputs.get("shooting", False) and len(self.weapons) > 0 and (weapon := self.weapons[self.current_weapon]) is not None:
            if (shoot_pos := inputs.get("shoot_pos", None)) is not None:
                self.after_shoot = weapon.shoot(DT, self.position, shoot_pos)
                self.last_shoot_position = shoot_pos
        for weapon in self.weapons:
            weapon.update(DT)

    def render(self, surface):
        pass

class Player(Entity):
    def __init__(self, position, health, team, entitiesManager, bulletsManager,
                 particlesManager, inputManager):
        super().__init__(position, [0,0], team, 10, 5, RenderableHealthManager(health), entitiesManager, bulletsManager, particlesManager, PlayerController(inputManager))
        self.invincible_color = (0, 0, 200)
        self.speed_color = Color.WHITE
        self.dynamic_color = self.color

    def update(self, DT):
        super().update(DT)
        self.angle = lerp_angle(self.angle, get_angle(self.position[0], self.position[1], *pygame.mouse.get_pos()), DT/2)
        self.dynamic_color = Color.lerp(self.dynamic_color, Color.lerp(self.color, self.speed_color, clamp(distance(0,0,*self.velocity)/self.speed/8, 0, 1)), DT/2)


    def render(self, surface):
        super().render(surface)
        c = self.invincible_color if self.healthManager.is_invincible() else self.dynamic_color
        if self.velocity == [0, 0]:
            pygame.draw.circle(surface, c, self.position, self.size)
        else:
            vx, vy = self.velocity
            w, h = max(self.size * 1.5, distance(0, 0, vx, vy) * 1.5), self.size * 1.5
            es = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.ellipse(es, c, es.get_rect(center=(w // 2, h // 2)))
            rs = pygame.transform.rotate(es, -get_angle(0, 0, vx, vy))
            surface.blit(rs, rs.get_rect(center=self.position))
        # pygame.draw.circle(surface, self.dynamic_color, pos_by_angle(*self.position, self.angle, 20), 5)
        self.healthManager.render(surface)


class Shooter(Entity):
    def __init__(self, position, health, team, entitiesManager, bulletsManager, particlesManager):
        super().__init__(position, [0,0], team, 20, 5, HealthManager(health), entitiesManager, bulletsManager, particlesManager, ShooterBehaviour(entitiesManager, self))
        self.dynamic_color = self.color
        self.weapons.append(Bow(entitiesManager, bulletsManager, particlesManager, self))

    def update(self, DT):
        super().update(DT)
        if self.after_shoot:
            vel = pos_by_angle(0,0,get_angle(*self.position, *self.last_shoot_position), 5)
            self.velocity[0]+=vel[0]*DT
            self.velocity[1]+=vel[1]*DT
        if (perc := self.weapons[0].cooldown_percentage()) > 0:
            self.dynamic_color = Color.lerp(Color.WHITE, self.color, perc)
        elif (perc := self.weapons[0].charge_percentage()) > 0:
            self.dynamic_color = Color.lerp(self.color, Color.WHITE, perc)
        # self.shoot_cooldown -= DT
        # self.dynamic_color = Color.lerp(self.dynamic_color, Color.lerp(self.color, Color.WHITE, 1-self.shoot_cooldown/self.max_shoot_cooldown), DT/2)
        # if self.shoot_cooldown <= 0:
        #     self.shoot_cooldown = self.max_shoot_cooldown
        #     direction = pos_by_angle(0,0,get_angle(self.x-self.size/2, self.y-self.size/2,
        #                                                              self.target.x, self.target.y),5)
        #     bulletManager.spawn(
        #         Bullet(self.x-self.size/2, self.y-self.size/2, random.randint(1,3), direction,1,int(self.size/3),self.color)
        #     )
        #     self.velocity = [-direction[0], -direction[1]]

        if random.random() > 0.8:
            offset = pos_by_angle(0, 0, random.randint(0, 360), 17)
            self.particlesManager.spawn(
                Particle(
                    [self.position[0] - self.size / 2 + offset[0], self.position[1] - self.size / 2 + offset[1]],
                    random.randint(1,4), 20, self.dynamic_color, [-offset[0]/4, -offset[1]/4]
                )
            )

    def render(self, surface):
        super().render(surface)
        pygame.draw.circle(surface, self.dynamic_color, (self.position[0]-self.size/2, self.position[1]-self.size/2), self.size, 4)

        # pygame.draw.circle(surface, self.dynamic_color, (self.x-self.size/2, self.y-self.size/2), self.size/3*(1-(self.shoot_cooldown/self.max_shoot_cooldown)))

# class Lance(Enemy):
#     def __init__(self, x, y, health, target):
#         super().__init__(x, y, health, target, 20, 0)
#         self.color = (255,0,0)
#         self.max_shoot_cooldown = 100
#         self.shoot_cooldown = self.max_shoot_cooldown
#         self.target = target
#         self.velocity = [0,0]
#         self.dynamic_color = self.color
#         self.angle = 0
#         self.cx, self.cy = self.x, self.y
#         self.min_dist = random.randint(50,100)
#         self.max_dist = self.min_dist+100
#
#     def update(self, DT, enemiesManager, bulletManager, particlesManager):
#         super().update(DT, enemiesManager, bulletManager, particlesManager)
#         self.shoot_cooldown -= DT
#         self.x, self.y, self.velocity = process_velocity(DT, self.x, self.y, self.velocity, W, H, True)
#         self.velocity[0] = lerp(self.velocity[0], 0, DT/20)
#         self.velocity[1] = lerp(self.velocity[1], 0, DT/20)
#         if distance(self.x, self.y, self.target.x, self.target.y) > self.min_dist:
#             dist = pos_by_angle(0,0,get_angle(self.x, self.y, self.target.x, self.target.y), self.speed)
#             self.velocity[0]+=dist[0]
#             self.velocity[1]+=dist[1]
#             print("AAAa")
#         # elif
#         self.dynamic_color = Color.lerp(self.dynamic_color, Color.lerp(self.color, Color.WHITE, 1-self.shoot_cooldown/self.max_shoot_cooldown), DT/2)
#         if self.shoot_cooldown > self.max_shoot_cooldown/10:
#             self.angle = lerp_angle(self.angle, get_angle(self.x, self.y, self.target.x, self.target.y), DT/5)
#         if self.shoot_cooldown <= 0:
#             self.shoot_cooldown = self.max_shoot_cooldown
#             bulletManager.spawn(
#                 Laser((self.x, self.y), pos_by_angle(self.x, self.y, self.angle,1500), 3,self.team,15,self.color,15,self.dynamic_color)
#             )
#             self.velocity = list(pos_by_angle(0,0,get_angle(self.x, self.y, self.target.x, self.target.y),-5))
#
#         if random.random() > 0.8:
#             x1, y1 =  pos_by_angle(0, 0, self.angle+90, self.size)
#             x2, y2 =  pos_by_angle(0, 0, self.angle-90, self.size)
#             for x, y in ((x1,y1),(x2,y2)):
#                 particlesManager.spawn(
#                     Particle(
#                         self.x + x + random.randint(-1, 1), self.y + y + random.randint(-1, 1),
#                         random.randint(1,3), 15, self.dynamic_color, [-i*2 for i in normalize(x,y)]
#                     )
#                 )
#         self.cx = lerp(self.cx, self.x, DT/2)
#         self.cy = lerp(self.cy, self.y, DT/2)
#
#     def render(self, surface):
#         super().render(surface)
#
#         points = [
#             pos_by_angle(self.x, self.y, self.angle, self.size*2),
#             pos_by_angle(self.x, self.y, self.angle+90, self.size),
#             pos_by_angle(self.x, self.y, self.angle+180, self.size),
#             pos_by_angle(self.x, self.y, self.angle-90, self.size),
#         ]
#
#         if self.shoot_cooldown < self.max_shoot_cooldown/10:
#             pygame.draw.line(surface, self.color, (self.x, self.y), pos_by_angle(self.x, self.y, self.angle,1500))
#
#         pygame.draw.polygon(surface, self.dynamic_color, points, 5)
#         pygame.draw.circle(surface, self.dynamic_color, (self.cx, self.cy), 7)
#
# class Dasher(Enemy):
#     def __init__(self, x, y, health, target):
#         super().__init__(x, y, health, target, speed=10)
#         self.max_dash_cooldown = 70
#         self.dash_cooldown = self.max_dash_cooldown * random.random()
#         self.dashing = 0
#         self.velocity = [0, 0]
#         self.last_velocity = [0, 0]
#         self.target = target
#         self.dynamic_color = self.color
#         self.particles_cooldown = 0
#         self.angle = 0
#
#     def update(self, DT, enemiesManager, bulletManager, particlesManager):
#         super().update(DT, enemiesManager, bulletManager, particlesManager)
#         self.dash_cooldown -= DT
#         self.angle = lerp_angle(self.angle, get_angle(self.x, self.y, self.target.x, self.target.y), DT/5)
#
#         self.x, self.y, self.velocity = process_velocity(DT, self.x, self.y, self.velocity, W, H, True)
#         self.velocity[0] = lerp(self.velocity[0], 0, DT/20)
#         self.velocity[1] = lerp(self.velocity[1], 0, DT/20)
#
#         self.dynamic_color = Color.lerp(self.dynamic_color, self.color, DT/20)
#
#         if self.velocity != [0,0]:
#             self.last_velocity = self.velocity
#
#         if self.dash_cooldown <= 0:
#             direction = normalize(self.target.x - self.x, self.target.y - self.y)
#             self.velocity = [direction[0]*20, direction[1]*20]
#             self.dashing = 10
#             self.dash_cooldown = self.max_dash_cooldown+self.dashing
#
#         if self.dashing > 0:
#             self.dashing -= DT
#             self.dynamic_color = Color.WHITE
#             angle = get_angle(0,0, self.velocity[0], self.velocity[1])+180
#             self.angle = angle-180
#             x1, y1 = pos_by_angle(self.x, self.y, angle, -self.size/2)
#             velocity = normalize(x1, y1)
#             if self.particles_cooldown <= 0:
#                 for i in [45, -45]:
#                     x2, y2 = pos_by_angle(x1, y1, angle + i, self.size)
#                     particlesManager.spawn(
#                         Particle(
#                             x2, y2, random.randint(1, 2), 15, self.dynamic_color, velocity
#                         )
#                     )
#                 self.particles_cooldown = 1
#             else: self.particles_cooldown -= DT
#
#             if distance(self.x, self.y, self.target.x, self.target.y) < self.target.size:
#                 self.target.health.damage(random.randint(3, 15))
#
#
#     def render(self, surface):
#         super().render(surface)
#         angle = self.angle+180
#         x1, y1 = pos_by_angle(self.x, self.y, angle, -self.size/2)
#         x2, y2 = pos_by_angle(self.x, self.y, angle, 0)
#
#         points = [
#             [x1, y1],
#             pos_by_angle(x1, y1, angle - 45, self.size),
#             pos_by_angle(x2, y2, angle - 45, self.size),
#             [x2, y2],
#             pos_by_angle(x2, y2, angle + 45, self.size),
#             pos_by_angle(x1, y1, angle + 45, self.size),
#         ]
#
#         pygame.draw.polygon(surface, self.dynamic_color, points)
#
#         f = clamp((self.dash_cooldown-self.dashing)/self.max_dash_cooldown, 0, 1)
#         c = Color.lerp(self.color, Color.WHITE, 1-f)
#         points = [
#             pos_by_angle(x1, y1, angle - 45, self.size),
#             pos_by_angle(x1, y1, angle - 45, self.size*f),
#             pos_by_angle(x2, y2, angle - 45, self.size*f),
#             pos_by_angle(x2, y2, angle - 45, self.size),
#         ]
#         pygame.draw.polygon(surface, c, points)
#         points = [
#             pos_by_angle(x1, y1, angle + 45, self.size),
#             pos_by_angle(x1, y1, angle + 45, self.size*f),
#             pos_by_angle(x2, y2, angle + 45, self.size*f),
#             pos_by_angle(x2, y2, angle + 45, self.size),
#         ]
#         pygame.draw.polygon(surface, c, points)
#         # pygame.draw.line(surface, (255, 0, 0), (x1, y1), (x3, y3), width)



class Laser:
    def __init__(self, start_pos, end_pos, damage, team, size, color, lifetime, start_color = (255,255,255)):
        self.start_pos = start_pos  # Starting position (x, y)
        self.end_pos = end_pos  # Ending position (x, y)
        self.damage = damage
        self.team = team
        self.size = size
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.dynamic_color = start_color

    def update(self, DT, enemiesManager, bulletsManager, particlesManager):
        self.dynamic_color = Color.lerp(self.dynamic_color, self.color, DT/5)
        self.lifetime -= DT
        self.check_collision(enemiesManager)
        if self.lifetime < 0:
            bulletsManager.remove(self)

    def render(self, surface):
        width = int(self.size * (self.lifetime / self.max_lifetime)) if self.max_lifetime > 0 else self.size
        pygame.draw.line(surface, self.dynamic_color, self.start_pos, self.end_pos, max(width, 1))

    def _line_circle_collision(self, center, radius):
        x1, y1 = self.start_pos
        x2, y2 = self.end_pos
        cx, cy = center
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return (cx - x1) ** 2 + (cy - y1) ** 2 <= radius ** 2
        t = ((cx - x1) * dx + (cy - y1) * dy) / (dx * dx + dy * dy)
        if t < 0:
            closest = (x1, y1)
        elif t > 1:
            closest = (x2, y2)
        else:
            closest = (x1 + t * dx, y1 + t * dy)
        return (cx - closest[0]) ** 2 + (cy - closest[1]) ** 2 <= radius ** 2

    def check_collision(self, enemiesManager):
        # Use half the current line width as a collision buffer.
        effective_radius = (int(self.size * (self.lifetime / self.max_lifetime)) if self.max_lifetime > 0 else self.size) / 2

        for enemy in enemiesManager.enemies:
            if enemy.team != self.team and self._line_circle_collision((enemy.x, enemy.y), enemy.size + effective_radius):
                enemy.health-=self.damage
        player = enemiesManager.player
        if player.team != self.team and self._line_circle_collision((player.x, player.y), player.size + effective_radius):
            player.health.damage(self.damage)