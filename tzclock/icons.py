import math
import pygame


def draw_sun_icon(surface, cx, cy, color):
    pygame.draw.circle(surface, color, (cx, cy), 5)
    for angle in range(0, 360, 45):
        r = math.radians(angle)
        x1 = cx + int(math.cos(r) * 8)
        y1 = cy + int(math.sin(r) * 8)
        x2 = cx + int(math.cos(r) * 13)
        y2 = cy + int(math.sin(r) * 13)
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), 2)


def draw_moon_icon(surface, cx, cy, color, bg_color=(8, 10, 14)):
    pygame.draw.circle(surface, color, (cx, cy), 9)
    pygame.draw.circle(surface, bg_color, (cx + 5, cy - 2), 9)
