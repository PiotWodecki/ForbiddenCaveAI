import os, pygame, random
import pygame.gfxdraw
import pygame.surface
import pygame.color
from pygame.locals import *
from pygame.color import *

from AnimatedSprite import AnimatedSprite

class Bat(AnimatedSprite):

    def __init__(self, xpos, ypos, imagename, map):
        AnimatedSprite.__init__(self)  # call Sprite initialize

        # Images and start image
        self.image = pygame.image.load(imagename)
        self.image.set_colorkey((0, 0, 0))

        # Images and start image and first animation frame
        self.batimage = self.sliceImage(40, 40, imagename)
        self.image = self.batimage[0]
        self.frame = 0
        self.fps = 10
        self.delay = 1000 / self.fps

        # Map for tile requests
        self.map = map

        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, self.image.get_size()[0], self.image.get_size()[1])

        # Fetch bat tile environment tiles
        env = map.fetchTileEnvironmentForPosition(xpos, ypos)

        # Set bat initial movement direction
        self.xmove = 0
        self.ymove = 0

        if env[1] == "v" or env[0] == "y":
            self.xmove = 1
        elif env[0] == "v" or env[0] == "y":
            self.ymove = -1
        elif env[2] == "v" or env[0] == "y":
            self.ymove = 1
        elif env[3] == "v" or env[0] == "y":
            self.xmove = -1

    # Update bat position
    def update(self):

        # Switch image after delay time has been reached
        t = pygame.time.get_ticks()
        if t - self.last_update > self.delay:
            self.frame += 1
            self.last_update = t

            if self.frame >= len(self.batimage):
                self.frame = 0

            self.image = self.batimage[self.frame]

            # Determine if bat direction has to be changed
        xcheck = self.rect.left + self.xmove
        ycheck = self.rect.top + self.ymove
        if self.xmove == 1:
            xcheck = xcheck + 40
        if self.ymove == 1:
            ycheck = ycheck + 40

        tile = self.map.fetchTileForPosition(xcheck, ycheck, False)
        if tile != "v" and tile != "V" and tile != "y":
            self.xmove = -self.xmove
            self.ymove = -self.ymove

        # Adjust position
        newpos = self.rect.move((self.xmove, self.ymove))
        self.rect = newpos

    # Player must avoid contact with monster

