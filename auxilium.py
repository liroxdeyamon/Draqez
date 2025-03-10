import math
import random
import pygame

def lerp(a, b, t):
    return a + (b - a) * t

def get_angle(start_x, start_y, end_x, end_y):
    return math.degrees(math.atan2(end_y - start_y, end_x - start_x)) % 360

def pos_by_angle(start_x, start_y, angle, length):
    angle_radians = math.radians(angle)
    return start_x + (length * math.cos(angle_radians)), start_y + (length * math.sin(angle_radians))

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def bar_polygon(x, y, width, height, offset=15):
    return [(x + offset, y), (x + width + offset, y), (x + width, y + height), (x, y + height)]

def draw_segmented_bar(surface, x, y, width, height, count, value, max_value, color):
    segment_width = (width - (count - 1) * 4) / count
    padding = 4
    full_segments = int(value / max_value * count)
    partial_fill = (value / max_value * count) - full_segments

    for i in range(full_segments):
        pygame.draw.polygon(surface, color, bar_polygon(x + i * (segment_width + padding), y, segment_width, height))

    if full_segments < count and partial_fill > 0.05:
        pygame.draw.polygon(surface, color, bar_polygon(
            x + full_segments * (segment_width + padding), y,
            segment_width * partial_fill, height
        ))

def calculate_damage(current_hp, max_hp, segments, base_damage):
    segment_size = max_hp / segments
    full_segments = current_hp/segment_size
    last_segment = full_segments-int(full_segments)
    damage = last_segment
    if last_segment < 0.7: damage+=1
    return min(damage*segment_size, base_damage), damage

def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

def normalize(dx, dy):
    length = math.sqrt(dx ** 2 + dy ** 2)
    return (dx / length, dy / length) if length > 0 else (0, 0)


def shape(radius, sides, angle, center = (0,0)):
    sides = max(2, sides)
    points = []
    for i in range(sides):
        radians = math.radians(angle+(360/sides*i))
        points.append([center[0]+math.cos(radians)*radius, center[1]+math.sin(radians)*radius])
    return points


def random_icon(color = (255,255,255)):
    icon = pygame.Surface((512, 512))
    icon.set_colorkey("black")
    icon.fill("black")
    match random.randint(1,8):
        case 1:
            pygame.draw.polygon(icon, color, shape(200 + (50 * random.random()), 2, random.randint(0,360), (256,256)), 30 + int(30 * random.random()))
            return icon
        case 2:
            pygame.draw.polygon(icon, color, shape(200 + (50 * random.random()), 3, random.randint(0,360), (256,256)), 30 + int(30 * random.random()))
            return icon
        case 3:
            pygame.draw.polygon(icon, color, shape(200 + (50 * random.random()), 4, random.randint(0,360), (256,256)), 30 + int(30 * random.random()))
            return icon
        case 4:
            pygame.draw.polygon(icon, color, shape(200 + (50 * random.random()), 5, random.randint(0,360), (256,256)), 30 + int(30 * random.random()))
            return icon
        case 5:
            pygame.draw.polygon(icon, color, shape(200 + (50 * random.random()), 6, random.randint(0,360), (256,256)), 30 + int(30 * random.random()))
            return icon
        case 6:
            pygame.draw.polygon(icon, color, shape(200 + (50 * random.random()), 7, random.randint(0,360), (256,256)), 30 + int(30 * random.random()))
            return icon
    pygame.draw.circle(icon, color, (256, 256), 200 + (50 * random.random()), 30 + int(30 * random.random()))
    return icon

def process_velocity(DT, position, velocity, W = 0, H = 0, bounce=False, slow_factor=1):
    position[0] += velocity[0] * DT
    position[1] += velocity[1] * DT

    if slow_factor > 0:
        velocity[0] = lerp(velocity[0], 0, DT / 3 * slow_factor)
        velocity[1] = lerp(velocity[1], 0, DT / 3 * slow_factor)

    if bounce:
        if position[0] < 0 or position[0] > W:
            velocity = [-velocity[0], velocity[1]]
            position[0] = max(0, min(W, position[0]))
        if position[1] < 0 or position[1] > H:
            velocity = [velocity[0], -velocity[1]]
            y = max(0, min(H, position[1]))

    return position, velocity


def lerp_angle(a, b, t):
    delta = (b - a) % 360
    if delta > 180:
        delta -= 360
    return a + delta * t