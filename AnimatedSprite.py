import os, pygame, random
import pygame.gfxdraw
import pygame.surface
import pygame.color
from pygame.locals import *
from pygame.color import *


class AnimatedSprite(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer

        # Track the time we started, and the time between updates.
        # Then we can figure out when we have to switch the image.
        self.start = pygame.time.get_ticks()
        self.fps = 10 #10
        self.delay = 1000 / self.fps #1000
        self.last_update = 0

        # Fetch images for animation

    def sliceImage(self, w, h, filename):
        images = []
        master_image = pygame.image.load(filename)

        master_width, master_height = master_image.get_size()
        for i in range(int(master_width / w)):
            image = master_image.subsurface(i * w, 0, w, h)
            image = image.convert()
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)
            images.append(image)
        return images


    



