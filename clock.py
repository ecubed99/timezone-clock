import os
import pygame

from tzclock.config import CONFIG_PATH, load_config
from tzclock.display import ClockDisplay
from tzclock.web_config import start_web_config

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    start_web_config()

    clock = pygame.time.Clock()

    config_mtime = None
    display = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Hot-reload config.yaml if it changes
        try:
            current_mtime = os.path.getmtime(CONFIG_PATH)
            if display is None or current_mtime != config_mtime:
                config = load_config()
                display = ClockDisplay(screen, config)
                config_mtime = current_mtime
                print("Reloaded config.yaml")
        except Exception as e:
            print(f"Config reload failed: {e}")

        if display is not None:
            display.draw()

        clock.tick(1)

    pygame.quit()


if __name__ == "__main__":
    main()
