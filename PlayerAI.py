import os, pygame, random
from copy import deepcopy

import pygame.gfxdraw
import pygame.surface
import pygame.color
from pygame.colordict import THECOLORS
from pygame.locals import *
from pygame.color import *

from AnimatedSprite import AnimatedSprite


class PlayerAI(AnimatedSprite):

    def __init__(self, xpos, ypos, playerleft, playerright, playerclimb, playerdead, \
                 background, map):
        AnimatedSprite.__init__(self)  # call Sprite initializer

        # Start direction
        self.xmove = 0
        self.ymove = 0
        self.jump = 0

        # Images and start image and first animation frame
        self.imageleft = self.sliceImage(40, 40, playerleft)
        self.imageright = self.sliceImage(40, 40, playerright)
        self.imageclimb = self.sliceImage(40, 40, playerclimb)
        self.imagedead = self.sliceImage(40, 40, playerdead)
        self.image = self.imageright[0]
        self.frame = 0

        # Reference to background and to logical background map
        self.background = background
        self.map = map

        # Dimensions and position on screen
        self.rect = Rect(xpos, ypos, 40, 40)

        # Flags if Player can climb and is climbing
        self.canClimb = False
        self.doClimb = False
        self.climbMove = 0
        self.jumpDead = False
        self.deadJumpCnt = 7

        # Flag to indicate that player is on elevator
        self.doElevator = False
        self.elevator = None

        # Print player's state

    def printState(self):
        print("Position: " + str(self.rect.left) + ", " + str(self.rect.top))
        print("Direction: " + str(self.xmove) + ", " + str(self.ymove))
        print("Jump: " + str(self.jump))
        print("Can climb: " + str(self.canClimb))
        print("Do climb: " + str(self.doClimb))
        print("Climb move: " + str(self.climbMove))

    # Check if player's head has collided
    def checkHeadWallCollision(self, correction):

        pix1 = self.background.get_at((self.rect.left + 5, self.rect.top - 1))
        pix2 = self.background.get_at((self.rect.left + 35, self.rect.top - 1))
        if (pix1 != THECOLORS['black'] or \
                pix2 != THECOLORS['black']):
            self.jump = correction
            self.ymove = int(self.jump)

    def checkUpCollision(self) -> bool:
        collsion = False
        pix1 = self.background.get_at((self.rect.left + 5, self.rect.top - 1))
        pix2 = self.background.get_at((self.rect.left + 35, self.rect.top - 1))
        if (pix1 != THECOLORS['black'] or \
                pix2 != THECOLORS['black']):
            collsion = True
            # print("Head Collision")
        return collsion

    # Determine y move direction of player if not climbing
    def setYMove(self):

        # Player is jumping
        if self.jump < 0:
            self.jump = self.jump + 0.125
            self.ymove = int(self.jump)

        # Check if player is falling
        if self.jump >= 0:
            pix1 = self.background.get_at((self.rect.left + 5, int(self.rect.top + 40 + self.jump)))
            pix2 = self.background.get_at((self.rect.left + 35, int(self.rect.top + 40 + self.jump)))
            tile1 = self.map.fetchTileForPosition(self.rect.left + 5, int(self.rect.top + 40 + self.jump), False)
            tile2 = self.map.fetchTileForPosition(self.rect.left + 35, int(self.rect.top + 40 + self.jump), False)
            if (tile1 == "l" and tile2 == "l") or (tile1 == "y" and tile2 == "y"):
                if (self.jump > self.deadJumpCnt): self.jumpDead = True
                self.jump = 0
                self.ymove = int(self.jump)
                self.canClimb = True
            elif (tile1 == "l" or tile2 == "l") or (tile1 == "y" or tile2 == "y"):
                if (self.jump > self.deadJumpCnt): self.jumpDead = True
                self.jump = 0
                self.ymove = int(self.jump)
                self.canClimb = False
            elif pix1 == THECOLORS['black'] and \
                    pix2 == THECOLORS['black']:
                self.jump = self.jump + 0.125
                self.ymove = int(self.jump)
            else:
                if (self.jump > self.deadJumpCnt): self.jumpDead = True
                self.jump = 0
                self.ymove = int(self.jump)

                # Correct y position if player's feet are inside wall
                pix1 = self.background.get_at((self.rect.left + 5, int(self.rect.top + 39)))
                pix2 = self.background.get_at((self.rect.left + 35, int(self.rect.top + 39)))
                if (pix1 != THECOLORS['black'] or \
                        pix2 != THECOLORS['black']):
                    newpos = self.rect.move((self.xmove, -1))
                    self.rect = newpos

                    # Correct player position if his feet are still above the ground ->
        # will happen if jump > 1, don't perform correction if a ladder is
        # below player's feet
        pix1 = self.background.get_at((self.rect.left + 5, int(self.rect.top + 40 + 1)))
        pix2 = self.background.get_at((self.rect.left + 35, int(self.rect.top + 40 + 1)))
        tile1 = self.map.fetchTileForPosition(self.rect.left + 5, int(self.rect.top + 40 + 1), False)
        tile2 = self.map.fetchTileForPosition(self.rect.left + 35, int(self.rect.top + 40 + 1), False)
        while pix1 == THECOLORS['black'] and \
                pix2 == THECOLORS['black'] and \
                (tile1 != "l" and tile2 != "l") and \
                (tile1 != "y" and tile2 != "y") and self.jump == 0:
            newpos = self.rect.move((self.xmove, 1))
            self.rect = newpos
            pix1 = self.background.get_at((self.rect.left + 5, int(self.rect.top + 40 + 1)))
            pix2 = self.background.get_at((self.rect.left + 35, int(self.rect.top + 40 + 1)))
            tile1 = self.map.fetchTileForPosition(self.rect.left + 5, int(self.rect.top + 40 + 1), False)
            tile2 = self.map.fetchTileForPosition(self.rect.left + 35, int(self.rect.top + 40 + 1), False)

            # Don't allow player's head to crash into ceiling
        if self.jump < 0:
            self.checkHeadWallCollision(0)
            self.checkUpCollision()

            # Correct x move direction of player if necessary


    # move?
    def setXMove(self):

        # Determine x position of check
        if self.xmove < 0:
            xcheck = self.rect.left + 5 - 1
        elif self.xmove > 0:
            xcheck = self.rect.left + 35 + 1
        else:
            return

        # Perform check
        pix1 = self.background.get_at((xcheck, self.rect.top + 5))
        pix2 = self.background.get_at((xcheck, self.rect.top + 35))
        if pix1 != THECOLORS['black'] or pix2 != THECOLORS['black']:
            self.xmove = 0
            self.jump = 0

            # Set climb y move direction

    def setClimbMove(self):

        # Do only climb down if there is no wall below player
        pix1 = self.background.get_at((self.rect.left + 5, int(self.rect.top + 40 + self.jump)))
        pix2 = self.background.get_at((self.rect.left + 35, int(self.rect.top + 40 + self.jump)))
        if self.climbMove > 0:
            if pix1 == THECOLORS['black'] and \
                    pix2 == THECOLORS['black']:
                self.ymove = self.climbMove
            else:
                self.ymove = 0
        else:
            self.ymove = self.climbMove

            # Allow player not to run over wall when going up
        if self.ymove < 0:
            self.checkHeadWallCollision(0)

            # Set y move direction according to elevator

    def setElevatorMove(self):
        self.ymove = self.elevator.ymove

    # Update sprite on screen
    def update(self):

        # Switch image after delay time has been reached
        t = pygame.time.get_ticks()
        if t - self.last_update > self.delay:
            self.frame += 1

            # Switch back to first frame of sequence if necessary
            if self.doClimb == True:
                if self.frame >= len(self.imageclimb):
                    self.frame = 0
            else:
                if self.frame >= len(self.imageleft):
                    self.frame = 0

                    # Animate image
            if self.doClimb == True:
                self.image = self.imageclimb[self.frame]
            elif self.xmove < 0:
                self.image = self.imageleft[self.frame]
            elif self.xmove > 0:
                self.image = self.imageright[self.frame]

            self.last_update = t

            # Determine x move direction
        self.setXMove()

        # Determine y move direction
        if self.doClimb:
            self.setClimbMove()
        elif self.doElevator:
            self.setElevatorMove()
        else:
            self.setYMove()

            # Adjust position
        newpos = self.rect.move((self.xmove, self.ymove))
        self.rect = newpos

        # Correct position by elevator x movement
        if self.doElevator:
            newpos = self.rect.move((self.elevator.xmove), 0)
            self.rect = newpos

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        print(">>>> removed")

    def collided(self):
        self.kill()
        print(">>>> collided")

