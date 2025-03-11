"""UI helper functions module"""

import pygame

def show_menu(screen):
    """Main game menu"""
    font = pygame.font.Font(None, 36)
    text = font.render("Stiskni ENTER pro start, ESC pro ukončení", True, (255, 255, 255))
    while True:
        screen.fill((0, 0, 128))
        screen.blit(text, (50, 250))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "start"
                if event.key == pygame.K_ESCAPE:
                    return "quit"
