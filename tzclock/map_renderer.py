import json
import math
from datetime import datetime, timezone

import pygame
import pygame.gfxdraw

from tzclock.astronomy import (
    ease_in_out_cos,
    is_daylight,
    solar_altitude,
    sun_position_approx,
)

GEOJSON_PATH = "assets/ne_110m_land.geojson"


class MapRenderer:
    def __init__(self, screen, cities, font_info, theme):
        self.screen = screen
        self.cities = cities
        self.font_info = font_info

        self.night_alpha = theme.get("night_alpha", 155)
        self.twilight_degrees = theme.get("twilight_degrees", 12)
        self.show_map_labels = False

        self.land_polygons = self.load_land()

        self.static_map_cache = None
        self.static_map_rect = None
        self.overlay_cache = None
        self.overlay_cache_minute = None

    def load_land(self):
        with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        polygons = []
        for feature in data["features"]:
            geom = feature["geometry"]
            if geom["type"] == "Polygon":
                polygons.extend(geom["coordinates"])
            elif geom["type"] == "MultiPolygon":
                for poly in geom["coordinates"]:
                    polygons.extend(poly)

        return polygons

    @staticmethod
    def latlon_to_xy(lat, lon, rect):
        x = rect.left + int((lon + 180) / 360 * rect.width)
        y = rect.top + int((90 - lat) / 180 * rect.height)
        return x, y

    def make_static_map(self, rect):
        surf = pygame.Surface((rect.width, rect.height)).convert()
        surf.fill((20, 24, 30))

        for lon in range(-180, 181, 30):
            x = int((lon + 180) / 360 * rect.width)
            pygame.draw.line(surf, (55, 58, 64), (x, 0), (x, rect.height), 1)

        for lat in range(-60, 61, 30):
            y = int((90 - lat) / 180 * rect.height)
            pygame.draw.line(surf, (55, 58, 64), (0, y), (rect.width, y), 1)

        for ring in self.land_polygons:
            pts = []
            for lon, lat in ring:
                x = int((lon + 180) / 360 * rect.width)
                y = int((90 - lat) / 180 * rect.height)
                pts.append((x, y))

            if len(pts) >= 3:
                try:
                    pygame.gfxdraw.filled_polygon(surf, pts, (58, 68, 58))
                    pygame.gfxdraw.aapolygon(surf, pts, (95, 102, 95))
                except Exception:
                    pygame.draw.polygon(surf, (58, 68, 58), pts)
                    pygame.draw.lines(surf, (95, 102, 95), True, pts, 1)

        return surf

    def make_day_night_overlay(self, rect):
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        decl, subsolar_lon = sun_position_approx()

        for y in range(rect.height):
            lat = 90 - (y / rect.height) * 180

            for x in range(rect.width):
                lon = (x / rect.width) * 360 - 180
                alt = solar_altitude(lat, lon, decl, subsolar_lon)

                if alt >= 0:
                    alpha = 0
                elif alt <= self.twilight_degrees * -1:
                    alpha = self.night_alpha
                else:
                    t = -alt / self.twilight_degrees
                    alpha = int(ease_in_out_cos(t) * self.night_alpha)

                if alpha:
                    overlay.set_at((x, y), (12, 10, 18, alpha))

        return overlay

    def draw_city_marker(self, city, rect):
        daylight = is_daylight(city["lat"], city["lon"])
        x, y = self.latlon_to_xy(city["lat"], city["lon"], rect)

        if daylight:
            marker = (245, 245, 245)
            glow_alpha = 45
            radius = 5
        else:
            marker = (120, 120, 120)
            glow_alpha = 10
            radius = 4

        glow_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 255, 255, glow_alpha), (15, 15), 13)
        self.screen.blit(glow_surface, (x - 15, y - 15))

        pygame.draw.circle(self.screen, marker, (x, y), radius)
        pygame.draw.circle(self.screen, (15, 15, 15), (x, y), radius + 3, 1)

    def draw(self, rect):
        if self.static_map_cache is None or self.static_map_rect != rect:
            self.static_map_cache = self.make_static_map(rect)
            self.static_map_rect = rect.copy()

        self.screen.blit(self.static_map_cache, rect)

        current_minute = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        if self.overlay_cache is None or self.overlay_cache_minute != current_minute:
            self.overlay_cache = self.make_day_night_overlay(rect)
            self.overlay_cache_minute = current_minute

        self.screen.blit(self.overlay_cache, rect)

        decl, subsolar_lon = sun_position_approx()
        sx, sy = self.latlon_to_xy(decl, subsolar_lon, rect)
        self.draw_sun_marker(sx, sy)

        for city in self.cities:
            self.draw_city_marker(city, rect)


    def draw_sun_marker(self, x, y):
        color = (255, 210, 80)
        outline = (15, 15, 15)
        background = (20, 24, 30)

        # Rays
        for angle in range(0, 360, 45):
            r = math.radians(angle)

            x1 = x + int(math.cos(r) * 8)
            y1 = y + int(math.sin(r) * 8)
            x2 = x + int(math.cos(r) * 15)
            y2 = y + int(math.sin(r) * 15)

            # Dark outline behind each ray
            pygame.draw.line(
                self.screen,
                outline,
                (x1, y1),
                (x2, y2),
                4,
            )

            # Colored ray
            pygame.draw.line(
                self.screen,
                color,
                (x1, y1),
                (x2, y2),
                2,
            )

        # Dark outline around center
        pygame.draw.circle(self.screen, outline, (x, y), 7)

        # Sun center
        pygame.draw.circle(self.screen, color, (x, y), 6)

        # Hollow center
        pygame.draw.circle(self.screen, background, (x, y), 2)
