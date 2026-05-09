import asyncio
import pygame
import sys
from settings import *
from game import Game


async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)

    game = Game(screen)

    # Run the game's async main loop (yields to browser event loop)
    await game.run()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())
