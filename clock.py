import pygame

from tzclock.config import load_config
from tzclock.display import ClockDisplay


def main():
    config = load_config()

    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    clock = pygame.time.Clock()
    display = ClockDisplay(screen, config)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        display.draw()
        clock.tick(1)

    pygame.quit()


if __name__ == "__main__":
    main()
