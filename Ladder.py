import os, pygame, random
import pygame.gfxdraw
import pygame.surface
import pygame.color
from pygame.locals import *
from pygame.color import *


class Ladder(pygame.sprite.Sprite):

    def __init__(self, xpos, ypos, imagename):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initialize

        # Images and start image
        self.image = pygame.image.load(imagename)

        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, self.image.get_size()[0], self.image.get_size()[1])

    def collided(self):
        self.kill()
        print(">>>> ladder collided")

