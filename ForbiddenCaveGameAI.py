# Import Modules
import os, pygame, random
import pygame.gfxdraw
import pygame.surface
import pygame.color
from pygame.colordict import THECOLORS
from pygame.locals import *
from pygame.color import *


from LevelMap import LevelMap
from Player import Player
from Skull import Skull


# Main class controlling the game
class ForbiddenCaveAI:

    # Initialize game controller
    def __init__(self):
        pygame.init()  # Initialize pygame environment

        self.screen = None
        self.background = None
        self.map = None
        self.yoff = 40

        # Game state constants
        self.GAMESTATE_DOOR = 0
        self.GAMESTATE_DEAD = 1
        self.GAMESTATE_QUIT = 2

        # Game state variables
        self.gemcnt = 0
        self.lives = 5
        self.levelcnt = -1
        self.totallevelcnt = 0
        self.bonus = 0
        self.beginbonus = 3000
        self.lastBonusDecTime = 0
        self.score = 0
        self.bonusscore = 0
        self.highscore = 0

        # Level maps
        self.maps = ["level1.txt", "level2.txt", "level3.txt", "level4.txt", \
                     "level5.txt", "level6.txt", "level7.txt", "level8.txt"]

        # Sounds
        self.gemSound = self.loadSound("gem.wav")
        self.jumpSound = self.loadSound("jump.wav")
        self.deadSound = self.loadSound("dead.wav")
        self.bonusSound = self.loadSound("bonus.wav")
        self.doorSound = self.loadSound("door.wav")
        self.startSound = self.loadSound("start.wav")
        self.doneSound = self.loadSound("done.wav")
        self.overSound = self.loadSound("over.wav")

        self.reset()





## #############################     METHODS     ###################################




        # load sound

    def loadSound(self, name):

        class NoneSound:
            def play(self): pass

        if not pygame.mixer or not pygame.mixer.get_init():
            return NoneSound()
        fullname = name
        try:
            sound = pygame.mixer.Sound(fullname)
        except pygame.error as message:
            print('Cannot load sound:', fullname)
            raise SystemExit(message)
        return sound

        # Initialize the game window

    def initWindow(self, width, height):

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Forbidden Cave')
        pygame.mouse.set_visible(1)

    # Start game
    def start(self):
        self.initWindow(1040, 680)

        result = 0
        while result != self.GAMESTATE_QUIT:
            # Show welcome screen
            result = self.doWelcomeLoop()
            if result == self.GAMESTATE_QUIT:
                return  # end game

            # Start game
            self.lives = 3
            self.score = 0
            self.bonusscore = 0
            self.levelcnt = -1
            self.totallevelcnt = 0

            #game loop
            while True:

                #loading map
                # Next level
                self.lastBonusDecTime = pygame.time.get_ticks()
                self.levelcnt += 1
                self.totallevelcnt += 1
                if self.levelcnt >= len(self.maps):
                    self.levelcnt = 0
                    self.beginbonus -= 500
                self.map = LevelMap("wall.png", "wall1.png", "wall2.png", self.maps[self.levelcnt], self.yoff)

                # Process game
                #play_Step????
                result = self.doMainLoop()

                # Abort if quit or dead
                if result == self.GAMESTATE_DEAD or \
                        result == self.GAMESTATE_QUIT:
                    break
                else:
                    # Add bonus to score
                    self.score += self.bonus
                    self.doLevelDoneLoop()

                    # Check bonus life
                    self.bonusscore += self.bonus
                    if self.bonusscore >= 5000:
                        self.bonusscore -= 5000
                        self.lives += 1

            # Game over!
            if result == self.GAMESTATE_DEAD:
                self.doGameOverLoop()

    # Add text to provided background
    def addText(self, text, background, xpos, ypos, \
                color=(255, 255, 255), bgcolor=(0, 0, 0), size=22, center=False, rightpad=0):

        font = pygame.font.Font("OptaneBold.ttf", size)
        text = font.render(text, 4, color)
        textpos = text.get_rect()
        textpos.left = 0
        textpos.top = 0
        if center == True:
            xpos = background.get_width() / 2 - textpos.width / 2
        cleanrec = (xpos - 1, ypos - 1, textpos.width + 1 + rightpad, textpos.height)
        if bgcolor != None:
            background.fill(bgcolor, cleanrec);
        background.blit(text, (xpos, ypos));

        # Show welcome screen

    def doWelcomeLoop(self):

        # Load map for screen bounds decoration
        map = LevelMap("wall.png", "wall1.png", "wall2.png", "welcome.txt", 0)
        background = map.fetchLevelSurface()

        self.addText("Forbidden Cave", background, 0, 80, (255, 48, 48), THECOLORS['black'], 80, True)
        self.addText("by Heiko Nolte, written May 2011", background, 0, 190, (209, 209, 209), THECOLORS['black'], 18,
                     True)
        self.addText("Version 1.0", background, 0, 210, (209, 209, 209), THECOLORS['black'], 12, True)
        self.addText("You have dared to enter:", background, 0, 250, (255, 193, 37), THECOLORS['black'], 25, True)
        self.addText("Collect all gems to proceed to the next level.", background, 0, 280, (255, 193, 37),
                     THECOLORS['black'], 25, True)
        self.addText("Use the arrow keys to control your movement.", background, 0, 310, (255, 193, 37),
                     THECOLORS['black'], 25, True)
        self.addText("Press space to jump.", background, 0, 340, (255, 193, 37), THECOLORS['black'], 25, True)
        self.addText("Highscore: " + str(self.highscore), background, 0, 400, THECOLORS["cyan"], THECOLORS['black'], 30,
                     True)
        self.addText("  Press space to start game  ", background, 0, 500, (255, 48, 48), THECOLORS['black'], 40, True)

        # Repeat until space or quit pressed
        while True:
            # Handle key events
            for event in pygame.event.get():
                if event.type == QUIT:
                    return self.GAMESTATE_QUIT
                if event.type == KEYDOWN:
                    if event.key == 32:
                        return

            self.screen.blit(background, (0, 0))
            pygame.display.flip()

            # Display level completed information box

    def doLevelDoneLoop(self):

        # Calculate info box coordinates
        width = 400
        height = 200
        left = self.background.get_rect().width / 2 - width / 2
        top = self.background.get_rect().height / 2 - height / 2
        rect = Rect(left, top, height, width)

        self.doneSound.play(6)
        begin = pygame.time.get_ticks()
        tsize = 25
        timediff = 0
        lasttimediff = 0
        while timediff < 5000:

            timediff = pygame.time.get_ticks() - begin

            # Catch QUIT key event
            for event in pygame.event.get():
                if event.type == QUIT:
                    return self.GAMESTATE_QUIT

                    # Create info box
            infobox = pygame.Surface((width, height))
            infobox = infobox.convert()
            infobox.fill((135, 206, 250))

            # Add texts to infobox
            self.addText("Level " + str(self.totallevelcnt) + " completed.", infobox, 0, 30, THECOLORS["black"],
                         (135, 206, 250), 25, True)
            self.addText("Bonus: " + str(self.bonus), infobox, 0, 80, THECOLORS["black"], (135, 206, 250), 23, True)
            self.addText("Get ready for next level!", infobox, 0, 130, THECOLORS["black"], (135, 206, 250), tsize, True)

            # Change ready text size
            if timediff - lasttimediff > 100:
                tsize += 1
                if tsize > 30: tsize = 25
                lasttimediff = timediff

                # Draw infobox
            self.screen.blit(infobox, (left, top))
            pygame.display.flip()

            # Display game over information box

    def doGameOverLoop(self):

        # Calculate info box coordinates
        width = 300
        height = 120
        left = self.background.get_rect().width / 2 - width / 2
        top = self.background.get_rect().height / 2 - height / 2
        rect = Rect(left, top, height, width)

        self.overSound.play()
        begin = pygame.time.get_ticks()
        tsize = 20
        timediff = 0
        lasttimediff = 0
        while timediff < 6000:

            timediff = pygame.time.get_ticks() - begin

            # Catch QUIT key event
            for event in pygame.event.get():
                if event.type == QUIT:
                    return self.GAMESTATE_QUIT

                    # Create info box
            infobox = pygame.Surface((width, height))
            infobox = infobox.convert()
            infobox.fill((255, 246, 143))

            # Add texts to infobox
            self.addText("Game over!", infobox, 0, 18, THECOLORS["black"], (255, 246, 143), 25, True)
            self.addText("Final score: " + str(self.score), infobox, 0, 55, THECOLORS["black"], (255, 246, 143), 23,
                         True)

            # Highscore
            if self.score > self.highscore:
                self.addText("A new highscore!", infobox, 0, 85, THECOLORS["black"], (255, 246, 143), 20, True)

                # Change ready text size
            if timediff - lasttimediff > 50:
                tsize += 1
                if tsize > 30: tsize = 20
                lasttimediff = timediff

                # Draw infobox
            self.screen.blit(infobox, (left, top))
            pygame.display.flip()

            # Set new highscore
        if self.score > self.highscore:
            self.highscore = self.score

            # Main loop to control gameplay


    # play_step??
    def doMainLoop(self):

        # Fetch self.background from loaded map
        self.background = self.map.fetchLevelSurface()

        ##################################################
        ### Fetch sprite groups
        ##################################################
        gemgroup = self.map.fetchGemgroup()
        self.gemcnt = len(gemgroup)
        monstergroup = self.map.fetchMonstergroup()
        laddergroup = self.map.fetchLaddergroup()
        elevatorgroup = self.map.fetchElevatorgroup()
        firegroup = self.map.fetchFiregroup()
        doorgroup = self.map.fetchDoorgroup()
        batgroup = self.map.fetchBatgroup()
        collgroup = None

        # Draw screen
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

        ##################################################
        ### Main loop
        ##################################################
        clock = pygame.time.Clock()
        loopstate = 1
        doorsoundPlayed = False
        while self.lives > 0:

            # Create player sprite
            self.startSound.play()
            player = Player(40, 600, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
                            self.background, self.map)

            playergroup = pygame.sprite.RenderPlain()
            playergroup.add(player)

            self.bonus = self.beginbonus
            while loopstate == 1:
                clock.tick(100)  # fps

                # Decrease bonues
                time = pygame.time.get_ticks()
                if pygame.time.get_ticks() - self.lastBonusDecTime > 5000:
                    if self.bonus > 0:
                        self.bonusSound.play()
                        self.bonus -= 100
                        self.lastBonusDecTime = time
                if self.bonus == 0:
                    loopstate = 0  # Life lost

                ##################################################
                ### Handle input events
                ##################################################

                for event in pygame.event.get():
                    if event.type == QUIT:
                        return self.GAMESTATE_QUIT
                    if event.type == KEYDOWN:
                        if event.key == 32:  # up
                            if (player.jump == 0 and player.ymove == 0) \
                                    or player.doElevator == True:
                                self.jumpSound.play()
                                player.jump = -5.2
                                player.climbMove = 0
                                player.doClimb = False
                                player.doElevator = False
                                player.elevator = None
                        if event.key == 1073741904:  # left
                            player.xmove = -1
                        if event.key == 1073741903:  # right
                            player.xmove = 1
                        if event.key == 1073741906:  # up
                            if player.canClimb:
                                player.doClimb = True
                                player.climbMove = -1
                        if event.key == 1073741905:  # down
                            if player.canClimb:
                                player.doClimb = True
                                player.climbMove = 1
                    elif event.type == KEYUP:
                        if event.key == 1073741903 and player.xmove > 0:
                            player.xmove = 0
                        if event.key == 1073741904 and player.xmove < 0:
                            player.xmove = 0
                        if event.key == 1073741906 or event.key == 1073741905 and player.doClimb:
                            player.climbMove = 0
                            player.doClimb = False

                            ##################################################
                ### Update state of sprites
                ##################################################

                gemgroup.update()
                monstergroup.update()
                laddergroup.update()
                elevatorgroup.update()
                batgroup.update()
                playergroup.update()
                firegroup.update()

                ##################################################
                ### Print game state
                ##################################################

                self.addText("Bonus: " + str(self.bonus), self.background, 10, 5, THECOLORS['lightblue'],
                             THECOLORS['black'], 22, False, 30)
                self.addText("Score: " + str(self.score), self.background, 450, 5, THECOLORS['orange'])
                self.addText("Lives: " + str(self.lives), self.background, 950, 5, THECOLORS['green'])

                ##################################################
                ### Draw self.background and sprites on screen
                ##################################################

                self.screen.blit(self.background, (0, 0))
                laddergroup.draw(self.screen)
                playergroup.draw(self.screen)
                elevatorgroup.draw(self.screen)
                gemgroup.draw(self.screen)
                firegroup.draw(self.screen)
                monstergroup.draw(self.screen)
                batgroup.draw(self.screen)
                if (self.gemcnt == 0):
                    if not doorsoundPlayed:
                        self.doorSound.play()
                        doorsoundPlayed = True
                    doorgroup.draw(self.screen)
                pygame.display.flip()

                ##################################################
                ### Perform collision handling
                ##################################################

                # Check if player has fallen too long
                if player.jumpDead == True:
                    loopstate = 0

                # Check player with gem collisions
                collgroup = pygame.sprite.spritecollide(player, gemgroup, 0)
                pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
                if len(pixelgroup):
                    self.gemSound.play()
                    self.gemcnt -= 1
                    self.score += 100
                    self.bonusscore += 100
                    if self.bonusscore >= 5000:
                        self.bonusscore -= 5000
                        self.lives += 1
                    gemgroup.remove(pixelgroup[0])

                # Check player with fire collisions
                collgroup = pygame.sprite.spritecollide(player, firegroup, 0)
                pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
                if len(pixelgroup):
                    print("fire collision")
                    loopstate = 0

                # Check player with bat collisions
                collgroup = pygame.sprite.spritecollide(player, batgroup, 0)
                pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
                if len(pixelgroup):
                    print("bat collision")
                    loopstate = 0

                # Check player with door collisions
                if self.gemcnt == 0:
                    collgroup = pygame.sprite.spritecollide(player, doorgroup, 0)
                    if len(collgroup):
                        print("door collision")
                        return self.GAMESTATE_DOOR

                # Check player with ladder collisions
                tile1 = self.map.fetchTileForPosition(player.rect.left + 5, int(player.rect.top + 40 + 1), False)
                tile2 = self.map.fetchTileForPosition(player.rect.left + 35, int(player.rect.top + 40 + 1), False)
                collgroup = pygame.sprite.spritecollide(player, laddergroup, 0)
                if len(collgroup) > 0:
                    # Collision with ladder sprite
                    player.canClimb = True
                elif (tile1 == "l" and tile2 == "l") or (tile1 == "y" and tile2 == "y"):
                    # Ladder is right below player
                    player.canClimb = True
                else:
                    # No ladder
                    player.canClimb = False
                    player.doClimb = False
                    player.climbMove = 0

                # Check player with monster collisions
                collgroup = pygame.sprite.spritecollide(player, monstergroup, 0)
                pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
                if len(pixelgroup) > 0:
                    print("monster collision")
                    loopstate = 0

                # Check player with elevator collisions
                collgroup = pygame.sprite.spritecollide(player, elevatorgroup, 0)
                if len(collgroup) > 0:
                    # Calculate check coordinates
                    xcheck1 = player.rect.left + 10
                    xcheck2 = player.rect.left + player.rect.width - 10
                    ycheck = player.rect.top + player.rect.height + 1

                    # Check against elevator
                    elevator = collgroup[0]
                    pix1 = self.background.get_at((xcheck1 + 5, int(player.rect.top + 41)))
                    pix2 = self.background.get_at((xcheck2 - 5, int(player.rect.top + 41)))
                    if ycheck < elevator.rect.top + elevator.rect.height / 4 and \
                            xcheck1 < elevator.rect.left + elevator.rect.width and \
                            xcheck2 > elevator.rect.left and \
                            pix1 == THECOLORS["black"] and \
                            pix2 == THECOLORS["black"]:
                        player.doElevator = True
                        player.elevator = elevator
                        player.rect.top = elevator.rect.top - player.rect.height + 1
                        if (player.jump > player.deadJumpCnt):
                            loopstate = 0
                        player.jump = 0
                    else:
                        player.doElevator = False
                        player.elevator = None
                else:
                    player.doElevator = False
                    player.elevator = None

            # end while loopstate = 1 loop
            self.lives -= 1  # deduct one life

            # Skull sprite
            self.deadSound.play()
            skull = Skull(player.rect.left, player.rect.top, "scull.png", self.background)
            skullgroup = pygame.sprite.RenderPlain()
            skullgroup.add(skull)

            # stop game for a certain time when player is dead
            begin = pygame.time.get_ticks()
            while 1:

                # Catch QUIT key event
                for event in pygame.event.get():
                    if event.type == QUIT:
                        return self.GAMESTATE_QUIT

                        # Check if loop will be left
                current = pygame.time.get_ticks()
                if current - begin > 2000:
                    break

                    ##################################################
                ### Draw Skull on screen
                ##################################################
                skull.update()
                skullgroup.draw(self.screen)
                self.addText("Lives: " + str(self.lives), self.screen, 950, 5, THECOLORS['green'])
                pygame.display.flip()

            if self.lives > 0:
                loopstate = 1  # continue game if lives are left
            else:
                # Game over
                return self.GAMESTATE_DEAD

    def doMainLoopAI(self):

        # Fetch self.background from loaded map
        self.background = self.map.fetchLevelSurface()

        ##################################################
        ### Fetch sprite groups
        ##################################################
        gemgroup = self.map.fetchGemgroup()
        self.gemcnt = len(gemgroup)
        monstergroup = self.map.fetchMonstergroup()
        laddergroup = self.map.fetchLaddergroup()
        elevatorgroup = self.map.fetchElevatorgroup()
        firegroup = self.map.fetchFiregroup()
        doorgroup = self.map.fetchDoorgroup()
        batgroup = self.map.fetchBatgroup()
        collgroup = None

        # Draw screen
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

        ##################################################
        ### Main loop
        ##################################################
        clock = pygame.time.Clock()
        loopstate = 1
        doorsoundPlayed = False
        while self.lives > 0:

            # Create player sprite
            self.startSound.play()
            player = Player(40, 600, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
                            self.background, self.map)

            playergroup = pygame.sprite.RenderPlain()
            playergroup.add(player)

            self.bonus = self.beginbonus
            while loopstate == 1:
                clock.tick(100)  # fps

                # Decrease bonues
                time = pygame.time.get_ticks()
                if pygame.time.get_ticks() - self.lastBonusDecTime > 5000:
                    if self.bonus > 0:
                        self.bonusSound.play()
                        self.bonus -= 100
                        self.lastBonusDecTime = time
                if self.bonus == 0:
                    loopstate = 0  # Life lost

                ##################################################
                ### Handle input events
                ##################################################

                for event in pygame.event.get():
                    if event.type == QUIT:
                        return self.GAMESTATE_QUIT
                    if event.type == KEYDOWN:
                        if event.key == 32:  # up
                            if (player.jump == 0 and player.ymove == 0) \
                                    or player.doElevator == True:
                                self.jumpSound.play()
                                player.jump = -5.2
                                player.climbMove = 0
                                player.doClimb = False
                                player.doElevator = False
                                player.elevator = None
                        if event.key == 1073741904:  # left
                            player.xmove = -1
                        if event.key == 1073741903:  # right
                            player.xmove = 1
                        if event.key == 1073741906:  # up
                            if player.canClimb:
                                player.doClimb = True
                                player.climbMove = -1
                        if event.key == 1073741905:  # down
                            if player.canClimb:
                                player.doClimb = True
                                player.climbMove = 1
                    elif event.type == KEYUP:
                        if event.key == 1073741903 and player.xmove > 0:
                            player.xmove = 0
                        if event.key == 1073741904 and player.xmove < 0:
                            player.xmove = 0
                        if event.key == 1073741906 or event.key == 1073741905 and player.doClimb:
                            player.climbMove = 0
                            player.doClimb = False

                            ##################################################
                ### Update state of sprites
                ##################################################

                gemgroup.update()
                monstergroup.update()
                laddergroup.update()
                elevatorgroup.update()
                batgroup.update()
                playergroup.update()
                firegroup.update()

                ##################################################
                ### Print game state
                ##################################################

                self.addText("Bonus: " + str(self.bonus), self.background, 10, 5, THECOLORS['lightblue'],
                             THECOLORS['black'], 22, False, 30)
                self.addText("Score: " + str(self.score), self.background, 450, 5, THECOLORS['orange'])
                self.addText("Lives: " + str(self.lives), self.background, 950, 5, THECOLORS['green'])

                ##################################################
                ### Draw self.background and sprites on screen
                ##################################################

                self.screen.blit(self.background, (0, 0))
                laddergroup.draw(self.screen)
                playergroup.draw(self.screen)
                elevatorgroup.draw(self.screen)
                gemgroup.draw(self.screen)
                firegroup.draw(self.screen)
                monstergroup.draw(self.screen)
                batgroup.draw(self.screen)
                if (self.gemcnt == 0):
                    if not doorsoundPlayed:
                        self.doorSound.play()
                        doorsoundPlayed = True
                    doorgroup.draw(self.screen)
                pygame.display.flip()

                ##################################################
                ### Perform collision handling
                ##################################################

                # Check if player has fallen too long
                if player.jumpDead == True:
                    loopstate = 0

                # Check player with gem collisions
                collgroup = pygame.sprite.spritecollide(player, gemgroup, 0)
                pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
                if len(pixelgroup):
                    self.gemSound.play()
                    self.gemcnt -= 1
                    self.score += 100
                    self.bonusscore += 100
                    if self.bonusscore >= 5000:
                        self.bonusscore -= 5000
                        self.lives += 1
                    gemgroup.remove(pixelgroup[0])

                # Check player with fire collisions
                collgroup = pygame.sprite.spritecollide(player, firegroup, 0)
                pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
                if len(pixelgroup):
                    print("fire collision")
                    loopstate = 0

                # Check player with bat collisions
                collgroup = pygame.sprite.spritecollide(player, batgroup, 0)
                pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
                if len(pixelgroup):
                    print("bat collision")
                    loopstate = 0

                # Check player with door collisions
                if self.gemcnt == 0:
                    collgroup = pygame.sprite.spritecollide(player, doorgroup, 0)
                    if len(collgroup):
                        print("door collision")
                        return self.GAMESTATE_DOOR

                # Check player with ladder collisions
                tile1 = self.map.fetchTileForPosition(player.rect.left + 5, int(player.rect.top + 40 + 1), False)
                tile2 = self.map.fetchTileForPosition(player.rect.left + 35, int(player.rect.top + 40 + 1), False)
                collgroup = pygame.sprite.spritecollide(player, laddergroup, 0)
                if len(collgroup) > 0:
                    # Collision with ladder sprite
                    player.canClimb = True
                elif (tile1 == "l" and tile2 == "l") or (tile1 == "y" and tile2 == "y"):
                    # Ladder is right below player
                    player.canClimb = True
                else:
                    # No ladder
                    player.canClimb = False
                    player.doClimb = False
                    player.climbMove = 0

                # Check player with monster collisions
                collgroup = pygame.sprite.spritecollide(player, monstergroup, 0)
                pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
                if len(pixelgroup) > 0:
                    print("monster collision")
                    loopstate = 0

                # Check player with elevator collisions
                collgroup = pygame.sprite.spritecollide(player, elevatorgroup, 0)
                if len(collgroup) > 0:
                    # Calculate check coordinates
                    xcheck1 = player.rect.left + 10
                    xcheck2 = player.rect.left + player.rect.width - 10
                    ycheck = player.rect.top + player.rect.height + 1

                    # Check against elevator
                    elevator = collgroup[0]
                    pix1 = self.background.get_at((xcheck1 + 5, int(player.rect.top + 41)))
                    pix2 = self.background.get_at((xcheck2 - 5, int(player.rect.top + 41)))
                    if ycheck < elevator.rect.top + elevator.rect.height / 4 and \
                            xcheck1 < elevator.rect.left + elevator.rect.width and \
                            xcheck2 > elevator.rect.left and \
                            pix1 == THECOLORS["black"] and \
                            pix2 == THECOLORS["black"]:
                        player.doElevator = True
                        player.elevator = elevator
                        player.rect.top = elevator.rect.top - player.rect.height + 1
                        if (player.jump > player.deadJumpCnt):
                            loopstate = 0
                        player.jump = 0
                    else:
                        player.doElevator = False
                        player.elevator = None
                else:
                    player.doElevator = False
                    player.elevator = None

            # end while loopstate = 1 loop
            self.lives -= 1  # deduct one life

            # Skull sprite
            self.deadSound.play()
            skull = Skull(player.rect.left, player.rect.top, "scull.png", self.background)
            skullgroup = pygame.sprite.RenderPlain()
            skullgroup.add(skull)

            # stop game for a certain time when player is dead
            begin = pygame.time.get_ticks()
            while 1:

                # Catch QUIT key event
                for event in pygame.event.get():
                    if event.type == QUIT:
                        return self.GAMESTATE_QUIT

                        # Check if loop will be left
                current = pygame.time.get_ticks()
                if current - begin > 2000:
                    break

                    ##################################################
                ### Draw Skull on screen
                ##################################################
                skull.update()
                skullgroup.draw(self.screen)
                self.addText("Lives: " + str(self.lives), self.screen, 950, 5, THECOLORS['green'])
                pygame.display.flip()

            if self.lives > 0:
                loopstate = 1  # continue game if lives are left
            else:
                # Game over
                return self.GAMESTATE_DEAD


def reset(self):
    self.frame_iteration = 0
    # Fetch self.background from loaded map
    self.background = self.map.fetchLevelSurface()

    ##################################################
    ### Fetch sprite groups
    ##################################################
    gemgroup = self.map.fetchGemgroup()
    self.gemcnt = len(gemgroup)
    monstergroup = self.map.fetchMonstergroup()
    laddergroup = self.map.fetchLaddergroup()
    elevatorgroup = self.map.fetchElevatorgroup()
    firegroup = self.map.fetchFiregroup()
    doorgroup = self.map.fetchDoorgroup()
    batgroup = self.map.fetchBatgroup()
    collgroup = None

    # Draw screen
    self.screen.blit(self.background, (0, 0))
    pygame.display.flip()

    ##################################################
    ### Main loop
    ##################################################
    clock = pygame.time.Clock()
    loopstate = 1
    doorsoundPlayed = False
    while self.lives > 0:

        # Create player sprite
        self.startSound.play()
        player = Player(40, 600, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
                        self.background, self.map)

        playergroup = pygame.sprite.RenderPlain()
        playergroup.add(player)

        self.bonus = self.beginbonus
        while loopstate == 1:
            clock.tick(100)  # fps

            # Decrease bonues
            time = pygame.time.get_ticks()
            if pygame.time.get_ticks() - self.lastBonusDecTime > 5000:
                if self.bonus > 0:
                    self.bonusSound.play()
                    self.bonus -= 100
                    self.lastBonusDecTime = time
            if self.bonus == 0:
                loopstate = 0  # Life lost

            ##################################################
            ### Handle input events ### play-step?
            ##################################################

            ## TO DO ACTION
            #self.play_step(self, player, action)

                        ##################################################
            ### Update state of sprites
            ##################################################

            gemgroup.update()
            monstergroup.update()
            laddergroup.update()
            elevatorgroup.update()
            batgroup.update()
            playergroup.update()
            firegroup.update()

            ##################################################
            ### Print game state
            ##################################################

            self.addText("Bonus: " + str(self.bonus), self.background, 10, 5, THECOLORS['lightblue'],
                         THECOLORS['black'], 22, False, 30)
            self.addText("Score: " + str(self.score), self.background, 450, 5, THECOLORS['orange'])
            self.addText("Lives: " + str(self.lives), self.background, 950, 5, THECOLORS['green'])

            ##################################################
            ### Draw self.background and sprites on screen
            ##################################################

            self.screen.blit(self.background, (0, 0))
            laddergroup.draw(self.screen)
            playergroup.draw(self.screen)
            elevatorgroup.draw(self.screen)
            gemgroup.draw(self.screen)
            firegroup.draw(self.screen)
            monstergroup.draw(self.screen)
            batgroup.draw(self.screen)
            if (self.gemcnt == 0):
                if not doorsoundPlayed:
                    self.doorSound.play()
                    doorsoundPlayed = True
                doorgroup.draw(self.screen)
            pygame.display.flip()

            ##################################################
            ### Perform collision handling
            ##################################################

            # Check if player has fallen too long
            if player.jumpDead == True:
                loopstate = 0

            # Check player with gem collisions
            collgroup = pygame.sprite.spritecollide(player, gemgroup, 0)
            pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
            if len(pixelgroup):
                self.gemSound.play()
                self.gemcnt -= 1
                self.score += 100
                self.bonusscore += 100
                if self.bonusscore >= 5000:
                    self.bonusscore -= 5000
                    self.lives += 1
                gemgroup.remove(pixelgroup[0])

            # Check player with fire collisions
            collgroup = pygame.sprite.spritecollide(player, firegroup, 0)
            pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
            if len(pixelgroup):
                print("fire collision")
                loopstate = 0

            # Check player with bat collisions
            collgroup = pygame.sprite.spritecollide(player, batgroup, 0)
            pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
            if len(pixelgroup):
                print("bat collision")
                loopstate = 0

            # Check player with door collisions
            if self.gemcnt == 0:
                collgroup = pygame.sprite.spritecollide(player, doorgroup, 0)
                if len(collgroup):
                    print("door collision")
                    return self.GAMESTATE_DOOR

            # Check player with ladder collisions
            tile1 = self.map.fetchTileForPosition(player.rect.left + 5, int(player.rect.top + 40 + 1), False)
            tile2 = self.map.fetchTileForPosition(player.rect.left + 35, int(player.rect.top + 40 + 1), False)
            collgroup = pygame.sprite.spritecollide(player, laddergroup, 0)
            if len(collgroup) > 0:
                # Collision with ladder sprite
                player.canClimb = True
            elif (tile1 == "l" and tile2 == "l") or (tile1 == "y" and tile2 == "y"):
                # Ladder is right below player
                player.canClimb = True
            else:
                # No ladder
                player.canClimb = False
                player.doClimb = False
                player.climbMove = 0

            # Check player with monster collisions
            collgroup = pygame.sprite.spritecollide(player, monstergroup, 0)
            pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
            if len(pixelgroup) > 0:
                print("monster collision")
                loopstate = 0

            # Check player with elevator collisions
            collgroup = pygame.sprite.spritecollide(player, elevatorgroup, 0)
            if len(collgroup) > 0:
                # Calculate check coordinates
                xcheck1 = player.rect.left + 10
                xcheck2 = player.rect.left + player.rect.width - 10
                ycheck = player.rect.top + player.rect.height + 1

                # Check against elevator
                elevator = collgroup[0]
                pix1 = self.background.get_at((xcheck1 + 5, int(player.rect.top + 41)))
                pix2 = self.background.get_at((xcheck2 - 5, int(player.rect.top + 41)))
                if ycheck < elevator.rect.top + elevator.rect.height / 4 and \
                        xcheck1 < elevator.rect.left + elevator.rect.width and \
                        xcheck2 > elevator.rect.left and \
                        pix1 == THECOLORS["black"] and \
                        pix2 == THECOLORS["black"]:
                    player.doElevator = True
                    player.elevator = elevator
                    player.rect.top = elevator.rect.top - player.rect.height + 1
                    if (player.jump > player.deadJumpCnt):
                        loopstate = 0
                    player.jump = 0
                else:
                    player.doElevator = False
                    player.elevator = None
            else:
                player.doElevator = False
                player.elevator = None

        # end while loopstate = 1 loop
        self.lives -= 1  # deduct one life

        # Skull sprite
        self.deadSound.play()
        skull = Skull(player.rect.left, player.rect.top, "scull.png", self.background)
        skullgroup = pygame.sprite.RenderPlain()
        skullgroup.add(skull)

        # stop game for a certain time when player is dead
        begin = pygame.time.get_ticks()
        while 1:

            # Catch QUIT key event
            for event in pygame.event.get():
                if event.type == QUIT:
                    return self.GAMESTATE_QUIT

                    # Check if loop will be left
            current = pygame.time.get_ticks()
            if current - begin > 2000:
                break

                ##################################################
            ### Draw Skull on screen
            ##################################################
            skull.update()
            skullgroup.draw(self.screen)
            self.addText("Lives: " + str(self.lives), self.screen, 950, 5, THECOLORS['green'])
            pygame.display.flip()

        if self.lives > 0:
            loopstate = 1  # continue game if lives are left
        else:
            # Game over
            #reward = -10
            return self.GAMESTATE_DEAD


def play_step(self, action):
    self.frame_iteration += 1
    for event in pygame.event.get():
        if event.type == QUIT:
            return self.GAMESTATE_QUIT
        # if event.type == KEYDOWN:
        #     if event.key == 32:  # up
        #         if (player.jump == 0 and player.ymove == 0) \
        #                 or player.doElevator == True:
        #             self.jumpSound.play()
        #             player.jump = -5.2
        #             player.climbMove = 0
        #             player.doClimb = False
        #             player.doElevator = False
        #             player.elevator = None
        #     if event.key == 1073741904:  # left
        #         player.xmove = -1
        #     if event.key == 1073741903:  # right
        #         player.xmove = 1
        #     if event.key == 1073741906:  # up
        #         if player.canClimb:
        #             player.doClimb = True
        #             player.climbMove = -1
        #     if event.key == 1073741905:  # down
        #         if player.canClimb:
        #             player.doClimb = True
        #             player.climbMove = 1
        # elif event.type == KEYUP:
        #     if event.key == 1073741903 and player.xmove > 0:
        #         player.xmove = 0
        #     if event.key == 1073741904 and player.xmove < 0:
        #         player.xmove = 0
        #     if event.key == 1073741906 or event.key == 1073741905 and player.doClimb:
        #         player.climbMove = 0
        #         player.doClimb = False




# Entrypoint
def main():
    game = ForbiddenCave()
    game.start()


# this calls the 'main' function when this script is executed
if __name__ == '__main__': main()