import os, pygame, random
import pygame.gfxdraw
import pygame.surface
import pygame.color
from pygame.locals import *
from pygame.color import *

from AnimatedSprite import AnimatedSprite


class Monster(AnimatedSprite):

    def __init__(self, xpos, ypos, monsterleft, monsterright, background, map):
        AnimatedSprite.__init__(self)  # call Sprite initialize

        # Init monster move direction
        self.xpos = xpos;
        self.ypos = ypos;
        self.xmove = 0.4

        # Images and start image and first animation frame
        self.monsterleft = self.sliceImage(40, 40, monsterleft)
        self.monsterright = self.sliceImage(40, 40, monsterright)
        self.image = self.monsterright[0]
        self.frame = 0
        self.fps = 5
        self.delay = 1000 / self.fps

        # Map for tile requests
        self.map = map

        # Background
        self.background = background

        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, self.image.get_size()[0], self.image.get_size()[1])

    def update(self):

        # Switch image after delay time has been reached
        t = pygame.time.get_ticks()
        if t - self.last_update > self.delay:
            self.frame += 1
            self.last_update = t

        if self.frame >= len(self.monsterleft):
            self.frame = 0

            # Determine x position of check
        if self.xmove < 0:
            xcheck = self.rect.left - 1
            self.image = self.monsterleft[self.frame]

        elif self.xmove > 0:
            xcheck = self.rect.left + 41
            self.image = self.monsterright[self.frame]
        else:
            return

        # Perform check
        tile = self.map.fetchTileForPosition(xcheck, self.rect.top + 41, 0)
        pix1 = self.background.get_at((xcheck, self.rect.top + 41))
        pix2 = self.background.get_at((xcheck, self.rect.top + 20))
        if (pix1 == THECOLORS['black'] or pix2 != THECOLORS['black']) \
                and tile != "l" and tile != "y":
            self.xmove = -self.xmove

            # Adjust position
        self.xpos = self.xpos + self.xmove
        self.rect = Rect(self.xpos, self.ypos, self.image.get_size()[0], self.image.get_size()[1])

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        print(">>>> monster removed")

    def collided(self):
        self.kill()
        print(">>>> monster collided")
