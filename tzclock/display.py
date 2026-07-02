import pygame
from datetime import datetime
from zoneinfo import ZoneInfo

from tzclock.astronomy import is_daylight
from tzclock.icons import draw_moon_icon, draw_sun_icon
from tzclock.map_renderer import MapRenderer


class ClockDisplay:
    def __init__(self, screen, config):
        self.screen = screen
        self.config = config
        self.cities = config["cities"]
        self.use_24h = config.get("use_24h", True)

        self.w, self.h = screen.get_size()

        self.font_time = pygame.font.SysFont("DejaVu Sans", int(self.h * 0.085), bold=True)
        self.font_city = pygame.font.SysFont("DejaVu Sans", int(self.h * 0.052), bold=True)
        self.font_info = pygame.font.SysFont("DejaVu Sans", int(self.h * 0.035))

        self.map_renderer = MapRenderer(
            screen=self.screen,
            cities=self.cities,
            font_info=self.font_info,
            theme=config.get("theme", {}),
        )

    def draw_header(self):
        col_w = self.w / len(self.cities)

        for i, city in enumerate(self.cities):
            now = datetime.now(ZoneInfo(city["timezone"]))
            x = int(i * col_w + col_w / 2)
            daylight = is_daylight(city["lat"], city["lon"])

            if daylight:
                time_color = (248, 248, 245)
                city_color = (215, 215, 215)
            else:
                time_color = (140, 140, 140)
                city_color = (105, 105, 105)

            time_text = now.strftime("%H:%M") if self.use_24h else now.strftime("%-I:%M %p")

            time_surf = self.font_time.render(time_text, True, time_color)
            self.screen.blit(time_surf, time_surf.get_rect(center=(x, int(self.h * 0.070))))

            city_surf = self.font_city.render(city["name"].upper(), True, city_color)
            city_rect = city_surf.get_rect(center=(x + 10, int(self.h * 0.155)))
            self.screen.blit(city_surf, city_rect)

            icon_x = city_rect.left - 18
            icon_y = city_rect.centery

            if daylight:
                draw_sun_icon(self.screen, icon_x, icon_y, city_color)
            else:
                draw_moon_icon(self.screen, icon_x, icon_y, city_color)

            if i > 0:
                pygame.draw.line(
                    self.screen,
                    (90, 95, 105),
                    (int(i * col_w), 10),
                    (int(i * col_w), int(self.h * 0.22)),
                    2,
                )

    def draw(self):
        self.screen.fill((8, 10, 14))
        self.draw_header()

        map_top = int(self.h * 0.23)
        pygame.draw.line(self.screen, (90, 95, 105), (0, map_top), (self.w, map_top), 2)

        map_rect = pygame.Rect(0, map_top + 2, self.w, self.h - map_top - 2)
        self.map_renderer.draw(map_rect)

        pygame.display.flip()
