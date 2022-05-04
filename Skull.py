import os, pygame, random
import pygame.gfxdraw
import pygame.surface
import pygame.color
from pygame.locals import *
from pygame.color import *

from AnimatedSprite import AnimatedSprite

class Skull(AnimatedSprite):

    def __init__(self, xpos, ypos, skull, background):
        AnimatedSprite.__init__(self)  # call Sprite initializer

        # Images and start image and first animation frame
        self.imageskull = self.sliceImage(40, 40, skull)
        self.image = self.imageskull[0]
        self.frame = 0
        self.delay = 100

        # Reference to background and to logical background map
        self.background = background

        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, 40, 40)

    # Update sprite on screen
    def update(self):

        # Switch image after delay time has been reached
        t = pygame.time.get_ticks()
        if (t - self.last_update) > self.delay:
            self.frame += 1
            if self.frame >= len(self.imageskull):
                self.frame = 0
            self.image = self.imageskull[self.frame]
            self.last_update = t

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        print(">>>> removed")

    def collided(self):
        self.kill()
        print(">>>> collided")

    # Fires burn the player
