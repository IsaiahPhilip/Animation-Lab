import pygame
from pygame import BLEND_RGB_SUB


class Button():
    def __init__(self, game, x, y, image, scale=1):
        width = image.get_width()
        height = image.get_height()
        self.game = game
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale))).convert_alpha()
        inv = pygame.Surface(self.image.get_rect().size, pygame.SRCALPHA)
        inv.fill((255, 255, 255, 255))
        inv.set_colorkey((255, 255, 255))
        inv.blit(self.image, (0, 0), None, BLEND_RGB_SUB)
        self.inverted_image = inv
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.highlighted = False
        self.is_over = False

    def draw(self, surface):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            self.is_over = True
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        else:
            self.is_over = False

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        if self.is_over:
            surface.blit(self.inverted_image, (self.rect.x, self.rect.y))
        else:
            surface.blit(self.image, (self.rect.x, self.rect.y))

            # draw button on screen


        return action

