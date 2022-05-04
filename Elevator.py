import os, pygame, random
import pygame.gfxdraw
import pygame.surface
import pygame.color
from pygame.locals import *
from pygame.color import *


class Elevator(pygame.sprite.Sprite):

    def __init__(self, xpos, ypos, imagename, map):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initialize

        # Images and start image
        self.image = pygame.image.load(imagename)
        self.image.set_colorkey((0, 0, 0))

        # Map for tile requests
        self.map = map

        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, self.image.get_size()[0], self.image.get_size()[1])

        # Fetch elevator tile environment tiles
        env = map.fetchTileEnvironmentForPosition(xpos, ypos)

        # Set elevator initial movement direction
        self.xmove = 0
        self.ymove = 0

        if env[0] == "o":
            self.ymove = -1
        elif env[1] == "o":
            self.xmove = 1
        elif env[2] == "o":
            self.ymove = 1
        elif env[3] == "o":
            self.xmove = -1

    # Update elevator position
    def update(self):

        # Determine if elevator direction has to be changed
        xcheck = self.rect.left + self.xmove
        ycheck = self.rect.top + self.ymove
        if self.xmove == 1:
            xcheck = xcheck + 40
        if self.ymove == 1:
            ycheck = ycheck + 40

        tile = self.map.fetchTileForPosition(xcheck, ycheck, True)
        if tile != "o" and tile != "O":
            self.xmove = -self.xmove
            self.ymove = -self.ymove

        # Adjust position
        newpos = self.rect.move((self.xmove, self.ymove))
        self.rect = newpos