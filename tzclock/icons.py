import math
import pygame


def draw_sun_icon(surface, cx, cy, color):
    """Draw a stylized sun."""
    core_radius = 5
    ray_inner = 8
    ray_outer = 13

    # Rays first
    for angle in range(0, 360, 45):
        r = math.radians(angle)
        x1 = cx + math.cos(r) * ray_inner
        y1 = cy + math.sin(r) * ray_inner
        x2 = cx + math.cos(r) * ray_outer
        y2 = cy + math.sin(r) * ray_outer
        pygame.draw.line(
            surface,
            color,
            (round(x1), round(y1)),
            (round(x2), round(y2)),
            2,
        )

    # Center disc
    pygame.draw.circle(surface, color, (cx, cy), core_radius)

    # Small hollow center gives it a cleaner look
    pygame.draw.circle(surface, (8, 10, 14), (cx, cy), 2)


def draw_moon_icon(surface, cx, cy, color, bg_color=(8, 10, 14)):
    """Draw a crescent moon."""
    pygame.draw.circle(surface, color, (cx, cy), 8)
    pygame.draw.circle(surface, bg_color, (cx + 4, cy - 2), 8)
