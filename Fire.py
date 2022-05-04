import os, pygame, random
import pygame.gfxdraw
import pygame.surface
import pygame.color
from pygame.locals import *
from pygame.color import *

from AnimatedSprite import AnimatedSprite


class Fire(AnimatedSprite):

    def __init__(self, xpos, ypos, imagename):
        AnimatedSprite.__init__(self)  # call Sprite initialize

        # Images and start image
        self.fireimage = self.sliceImage(40, 40, imagename)
        self.image = self.fireimage[0]
        self.frame = 0
        self.fps = 10
        self.delay = 1000 / self.fps

        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, self.image.get_size()[0], self.image.get_size()[1])

    def update(self):

        # Switch image after delay time has been reached
        t = pygame.time.get_ticks()
        if t - self.last_update > self.delay:
            self.frame += 1
            self.last_update = t

        if self.frame >= len(self.fireimage):
            self.frame = 0

        self.image = self.fireimage[self.frame]

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        print(">>>> fire removed")

    def collided(self):
        self.kill()
        print(">>>> fire collided")

