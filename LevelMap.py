import os, pygame, random
import pygame.gfxdraw
import pygame.surface
import pygame.color
from pygame.locals import *
from pygame.color import *

# Map of level player is moving in
from Bat import Bat
from Door import Door
from Elevator import Elevator
from Fire import Fire
from Gem import Gem
from Ladder import Ladder
from Monster import Monster


class LevelMap:

    def __init__(self, tilefile, wallfile1, wallfile2, mapfile, yoffset):
        # Tile image for wall
        self.tile = pygame.image.load(tilefile)
        self.wall1 = pygame.image.load(wallfile1)
        self.wall2 = pygame.image.load(wallfile2)

        # Load text map
        file = open(mapfile, "r")
        self.rawtextmap = file.readlines()
        file.close()

        # Remove carriage returns
        self.textmap = []
        for line in self.rawtextmap:
            line = line[0:len(line) - 1]
            self.textmap.append(line)

        # Sprite groups
        self.levelsurface = None
        self.gemgroup = None
        self.monstergroup = None
        self.laddergroup = None
        self.elevatorgroup = None
        self.firegroup = None
        self.doorgroup = None
        self.batgroup = None

        # Offset for tile position location
        self.xoff = 0
        self.yoff = yoffset

    # Calculate tile from screen coordinates
    def calcTileFromScreenPos(self, xpos, ypos):

        # Fetch tile height and width
        xd = self.tile.get_rect().width
        yd = self.tile.get_rect().height

        # Subtract offsets
        xpos = xpos - self.xoff
        ypos = ypos - self.yoff

        # Calculate coordinates in tile map
        xp = xpos / xd
        yp = ypos / yd

        return (xp, yp)

    # Fetch tile from map for position
    def fetchTileForPosition(self, xpos, ypos, doCorrect):

        # Derive tile position from screen position
        tilePos = self.calcTileFromScreenPos(xpos, ypos)
        xp = int(tilePos[0])
        yp = int(tilePos[1])

        # Fetch tile and correct it
        result = self.textmap[yp][xp]
        if doCorrect == True:
            if result == "c" or result == "m" or result == "l" or result == "y":
                result = "."

        return result

    # Fetch tile environment from map position
    def fetchTileEnvironmentForPosition(self, xpos, ypos):

        # Derive tile position from screen position
        tilePos = self.calcTileFromScreenPos(xpos, ypos)
        xp = tilePos[0]
        yp = tilePos[1]

        # Set environment calculation deltas
        xd = [0, 1, 0, -1]
        yd = [-1, 0, 1, 0]

        # Retrieve tiles in neighborhood
        result = []
        for ndx in range(4):
            result.append(self.textmap[yp + yd[ndx]][xp + xd[ndx]])

        return result

    # Create an empty surface
    def createEmptySurface(self, rect):

        surf = pygame.Surface(rect)
        surf = surf.convert()
        surf.fill((0, 0, 0))
        return surf

        # Fetch gem group from map definition

    def fetchGemgroup(self, dirty=False):

        # Don't recreate gem group
        if self.gemgroup is not None and not dirty:
            return self.gemgroup

        # Fetch gem size
        size = self.tile.get_size()

        # Create the sprite group for the gems
        self.gemgroup = pygame.sprite.RenderPlain()

        # Create gem sprites and add them to the gem group
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                if tile == "c":
                    gem = Gem(xpos, ypos, "gem.png")
                    self.gemgroup.add(gem)
                xpos = xpos + size[0]
            ypos = ypos + size[1]

        return self.gemgroup

    # Fetch gem group from map definition
    def fetchDoorgroup(self, dirty=False):

        # Don't recreate door group
        if self.doorgroup is not None and not dirty:
            return self.doorgroup

        # Fetch door size
        size = self.tile.get_size()

        # Create the sprite group for the door
        self.doorgroup = pygame.sprite.RenderPlain()

        # Create door sprites and add them to the gem group
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                if tile == "d":
                    door = Door(xpos, ypos, "door.png")
                    self.doorgroup.add(door)
                xpos = xpos + size[0]
            ypos = ypos + size[1]

        return self.doorgroup

    # Fetch fire group from map definition
    def fetchFiregroup(self, dirty=False):

        # Don't recreate gem group
        if self.firegroup is not None and not dirty:
            return self.firegroup

        # Fetch gem size
        size = self.tile.get_size()

        # Create the sprite group for the gems
        self.firegroup = pygame.sprite.RenderUpdates()

        # Create gem sprites and add them to the gem group
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                if tile == "f":
                    fire = Fire(xpos, ypos, "fire.png")
                    self.firegroup.add(fire)
                xpos = xpos + size[0]
            ypos = ypos + size[1]

        return self.firegroup

        # Fetch monster group from map definition

    def fetchMonstergroup(self, dirty=False):

        # Don't recreate monster group
        if self.monstergroup is not None and not dirty:
            return self.monstergroup

        # Fetch monster size
        size = self.tile.get_size()

        # Create the sprite group for the monster
        self.monstergroup = pygame.sprite.RenderPlain()

        # Create monster sprites and add them to the monster group
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                if tile == "m":
                    monster = Monster(xpos, ypos, "monsterLeft.png", "monsterRight.png", self.levelsurface, self)
                    self.monstergroup.add(monster)
                xpos = xpos + size[0]
            ypos = ypos + size[1]

        return self.monstergroup

    # Fetch ladder group from map definition
    def fetchLaddergroup(self, dirty=False):

        # Don't recreate ladder group
        if self.laddergroup is not None and not dirty:
            return self.laddergroup

        # Fetch ladder size
        size = self.tile.get_size()

        # Create the sprite group for the ladders
        self.laddergroup = pygame.sprite.RenderPlain()

        # Create monster sprites and add them to the ladder group
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                if tile == "L" or tile == "l" or tile == "y":
                    ladder = Ladder(xpos, ypos, "ladder.png")
                    self.laddergroup.add(ladder)

                xpos = xpos + size[0]
            ypos = ypos + size[1]

        return self.laddergroup

        # Fetch elevator group from map definition

    def fetchElevatorgroup(self, dirty=False):

        # Don't recreate elevator group
        if self.elevatorgroup is not None and not dirty:
            return self.elevatorgroup

        # Fetch elevator size
        size = self.tile.get_size()

        # Create the sprite group for the elevators
        self.elevatorgroup = pygame.sprite.RenderPlain()

        # Create elevator sprites and add them to the elevator group
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                if tile == "O":
                    elevator = Elevator(xpos, ypos, "elevator.png", self)
                    self.elevatorgroup.add(elevator)
                xpos = xpos + size[0]
            ypos = ypos + size[1]

        return self.elevatorgroup

    # Fetch elevator group from map definition
    def fetchBatgroup(self, dirty=False):

        # Don't recreate bat group
        if self.batgroup is not None and not dirty:
            return self.batgroup

        # Fetch elevator size
        size = self.tile.get_size()

        # Create the sprite group for the bats
        self.batgroup = pygame.sprite.RenderPlain()

        # Create bat sprites and add them to the bat group
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                if tile == "V":
                    bat = Bat(xpos, ypos, "bat.png", self)
                    self.batgroup.add(bat)
                xpos = xpos + size[0]
            ypos = ypos + size[1]

        return self.batgroup

    # Create level surface from map definition
    def fetchLevelSurface(self, dirty=False):

        # Don't recreate level surface
        if self.levelsurface is not None and not dirty:
            return self.levelsurface

        # Create empty level surface
        size = self.tile.get_size()
        xwidth = len(self.textmap[0]) * size[0]
        ywidth = len(self.textmap) * size[1] + self.yoff
        self.levelsurface = self.createEmptySurface((xwidth, ywidth))

        # Paint walls on surface
        ypos = self.yoff
        for line in self.textmap:
            xpos = 0
            for tile in line:
                # Wall
                if tile == "b" or tile == "d":
                    self.levelsurface.blit(self.tile, (xpos, ypos))
                elif tile == "a":
                    if xpos / size[0] % 2 == 1:
                        self.levelsurface.blit(self.wall1, (xpos, ypos))
                    else:
                        self.levelsurface.blit(self.wall2, (xpos, ypos))

                xpos = xpos + size[0]
            ypos = ypos + size[1]

        return self.levelsurface

    # Superclass for animated sprites

