from collections import namedtuple
from math import dist
from operator import itemgetter

import pygame
import copy
import pygame.gfxdraw
import pygame.surface
import pygame.color
from pygame.colordict import THECOLORS
from pygame.locals import *
import numpy as np
import time

from AIPlayerDeadException import AIPlayerDeadException
from EndGameException import EndGameException
from ExitLoopException import ExitLoopException
from GameState import GameState
from LevelMap import LevelMap
from Player import Player
from PlayerAI import PlayerAI
from Skull import Skull


class GameAI:
    def __init__(self):
        pygame.init()  # Initialize pygame environment

        self.screen = None
        self.background = None
        self.map = None
        self.yoff = 40

        # Game state variables
        self.gemcnt = 0
        self.lives = 1
        self.levelcnt = -1
        self.totallevelcnt = 0
        self.bonus = 0
        self.beginbonus = 3000
        self.lastBonusDecTime = 0
        self.score = 0
        self.bonusscore = 0
        self.highscore = 0

        self.frame_iteration=0

        # Level maps
        self.maps = ["level1.txt", "level2.txt", "level3.txt", "level4.txt", \
                     "level5.txt", "level6.txt", "level7.txt", "level8.txt"]

        # Sounds
        # self.gemSound = self.loadSound("gem.wav")
        # self.jumpSound = self.loadSound("jump.wav")
        # self.deadSound = self.loadSound("dead.wav")
        # self.bonusSound = self.loadSound("bonus.wav")
        # self.doorSound = self.loadSound("door.wav")
        # self.startSound = self.loadSound("start.wav")
        # self.doneSound = self.loadSound("done.wav")
        # self.overSound = self.loadSound("over.wav")

        self.initWindow(1040, 680)

        self.reset()

    # def loadSound(self, name):
    #
    #     class NoneSound:
    #         def play(self): pass
    #
    #     if not pygame.mixer or not pygame.mixer.get_init():
    #         return NoneSound()
    #     fullname = name
    #     try:
    #         sound = pygame.mixer.Sound(fullname)
    #     except pygame.error as message:
    #         print('Cannot load sound:', fullname)
    #         raise SystemExit(message)
    #     return sound
    #
    #     # Initialize the game window

    def initWindow(self, width, height):

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Forbidden Cave')
        pygame.mouse.set_visible(1)

    def start(self):

            # game loop
            while True:

        # Next level #czy to powinno tu być???

                self.lastBonusDecTime = pygame.time.get_ticks()
                self.levelcnt += 1
                self.totallevelcnt += 1
                if self.levelcnt >= len(self.maps):
                    self.levelcnt = 0
                    self.beginbonus -= 500
                self.map = LevelMap("wall.png", "wall1.png", "wall2.png", self.maps[self.levelcnt], self.yoff)

                # 2. Prepare the map (Im not sure if it should be here)

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

    def reset(self):
        # Start game
        self.lives = 1
        self.score = 0
        self.bonusscore = 0
        self.levelcnt = -1
        self.totallevelcnt = 0
        self.frame_iteration = 0

        self.lastBonusDecTime = pygame.time.get_ticks()
        self.levelcnt += 1
        self.totallevelcnt += 1
        if self.levelcnt >= len(self.maps):
            self.levelcnt = 0
            self.beginbonus -= 500
        self.map = LevelMap("wall.png", "wall1.png", "wall2.png", self.maps[self.levelcnt], self.yoff)

    def reset_with_return(self, game):
        # Start game
        self.lives = 1
        self.score = 0
        self.bonusscore = 0
        self.levelcnt = -1
        self.totallevelcnt = 0

        self.lastBonusDecTime = pygame.time.get_ticks()
        self.levelcnt += 1
        self.totallevelcnt += 1
        if self.levelcnt >= len(self.maps):
            self.levelcnt = 0
            self.beginbonus -= 500
        self.map = LevelMap("wall.png", "wall1.png", "wall2.png", self.maps[self.levelcnt], self.yoff)

        game.init_ui()  # lvl0
        playerai = PlayerAI(40, 600, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
                            game.background, game.map)  # size 40x40

        return playerai

    def abort_if_quit_or_dead(self):
        pass

    def play_step2(self, playerai, action):
        self.frame_iteration += 1

        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                raise EndGameException

        # 2. move
        # I need playerAI
        self._move(playerai, action)

        self._update_ui3(playerai)

        reward = 0
        game_over = False
        reward = self.punish_for_wall_collisions(playerai, reward)

        # 3. check for gameover
        reward, game_over = self.check_for_game_over(playerai, reward)
        if game_over is True:
            return reward, game_over, self.calculate_end_score()

        if self.check_for_gem_collision(playerai) == True:
            reward = reward + 30

        return reward, game_over, self.calculate_end_score()

    def check_for_game_over(self, playerai, reward):
        game_over = False
        # if self.lives <= 0 or self.check_for_single_dead(playerai) == 0:
        #     game_over = True
        #     reward = -10
        #     return reward, game_over
        # return reward, game_over
        if self.score == 0:
            amount_of_steps_to_do_without_reward = 10000
        else:
            amount_of_steps_to_do_without_reward = self.score * 100
        if self.check_for_single_dead(playerai) == 0 or self.frame_iteration > amount_of_steps_to_do_without_reward:
            game_over = True
            reward = reward - 10
            return reward, game_over
        return reward, game_over

    def check_for_jump_dead(self, player_ai):
        # Check if player has fallen too long
        if player_ai.jumpDead == True:
            loopstate = 0 #life lost
            self.lives -= 1

    def get_scaled_position_of_the_player(self, player_ai):
        position = [0.0666, 0.8823]
        if player_ai is not None:
            x_position = player_ai.rect.left / 1040
            y_position = player_ai.rect.top / 680
            position[0] = x_position
            position[1] = y_position

        return position

    def check_for_gem_collision(self, player_ai):
        # Check player with gem collisions
        if player_ai is not None:
            gemgroup = self.get_gems_group()
            collgroup = pygame.sprite.spritecollide(player_ai, gemgroup, 0)
            pixelgroup = pygame.sprite.spritecollide(player_ai, collgroup, 0, pygame.sprite.collide_mask)
            if len(pixelgroup):
                # self.gemSound.play()
                self.gemcnt -= 1
                self.score += 100
                self.bonusscore += 100
                if self.bonusscore >= 5000:
                    self.bonusscore -= 5000
                    self.lives += 1
                gemgroup.remove(pixelgroup[0])
                del collgroup
                del pixelgroup
                del gemgroup
                return True
            del collgroup
            del pixelgroup
            del gemgroup
            return False

    def check_for_incoming_gem_collision(self, player_ai):
        if player_ai is not None:
            gemgroup = self.get_gems_group()
            collgroup = pygame.sprite.spritecollide(player_ai, gemgroup, 0)
            pixelgroup = pygame.sprite.spritecollide(player_ai, collgroup, 0, pygame.sprite.collide_mask)
            if len(pixelgroup):
                # self.gemSound.play()
                del collgroup
                del pixelgroup
                del gemgroup
                return True

            del collgroup
            del pixelgroup
            del gemgroup
            return False

    def calculate_end_score(self):
        return self.score + self.bonus + self.bonusscore

    def init_ui(self):
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

        # self.startSound.play()
        player = Player(40, 600, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
                        self.background, self.map)

        playergroup = pygame.sprite.RenderPlain()
        playergroup.add(player)

        # clock = pygame.time.Clock()
        # loopstate = 1
        # doorsoundPlayed = False
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

        # self.addText("Bonus: " + str(self.bonus), self.background, 10, 5, THECOLORS['lightblue'],
        #              THECOLORS['black'], 22, False, 30)
        # self.addText("Score: " + str(self.score), self.background, 450, 5, THECOLORS['orange'])
        # self.addText("Lives: " + str(self.lives), self.background, 950, 5, THECOLORS['green'])

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
        pygame.display.flip()

    def _update_ui3(self, player):
        # Fetch self.background from loaded map
        # self.background = self.map.fetchLevelSurface()

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

        # # Draw screen
        # self.screen.blit(self.background, (0, 0))
        # pygame.display.flip()

        # Create player sprite
        # self.startSound.play()
        # player = PlayerAI(xpos, ypos, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
        #                   self.background, self.map)
        playergroup = pygame.sprite.RenderPlain()
        if player is not None:
            playergroup.add(player)

            self.check_if_player_on_the_ladder(player)

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

            # self.addText("Bonus: " + str(self.bonus), self.background, 10, 5, THECOLORS['lightblue'],
            #              THECOLORS['black'], 22, False, 30)
            # self.addText("Score: " + str(self.score), self.background, 450, 5, THECOLORS['orange'])
            # self.addText("Lives: " + str(self.lives), self.background, 950, 5, THECOLORS['green'])

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
                # if not doorsoundPlayed:
                #     self.doorSound.play()
                #     doorsoundPlayed = True
                doorgroup.draw(self.screen)

            pygame.display.flip()

    def check_for_single_dead(self, player):
        try:
            if player is not None:
                self.check_for_falling(player)
                self.check_for_fire_collision(player)
                self.check_for_bat_collision(player)
                self.check_for_monster_collision(player)
                self.check_for_jump_dead(player)
            # self.check_for_time_up()
            # self.check_for_too_long_playing_without_effect()
            return 1
        except AIPlayerDeadException:
            return 0

    def check_for_incoming_collision(self, player):
        try:
            self.check_for_fire_collision(player)
            self.check_for_bat_collision(player)
            self.check_for_monster_collision(player)
            return False
        except AIPlayerDeadException:
            return True

    def check_for_falling(self, player):
        # Check if player has fallen too long
        if player is not None:
            if player.jumpDead == True:
                raise AIPlayerDeadException()

    def check_for_fire_collision(self, player):
        # Check player with fire collisions
        firegroup = self.get_fire_group()
        collgroup = pygame.sprite.spritecollide(player, firegroup, 0)
        pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
        if len(pixelgroup):
            # print("fire collision")
            del firegroup
            del collgroup
            del pixelgroup
            raise AIPlayerDeadException()

    def check_for_bat_collision(self, player):
        # Check player with bat collisions
        batgroup = self.get_fire_group()
        collgroup = pygame.sprite.spritecollide(player, batgroup, 0)
        pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
        if len(pixelgroup):
            # print("bat collision")
            del batgroup
            del collgroup
            del pixelgroup
            raise AIPlayerDeadException()

    def check_for_monster_collision(self, player):
        # Check player with monster collisions
        monstergroup = self.get_monster_group()
        collgroup = pygame.sprite.spritecollide(player, monstergroup, 0)
        pixelgroup = pygame.sprite.spritecollide(player, collgroup, 0, pygame.sprite.collide_mask)
        if len(pixelgroup) > 0:
            # print("monster collision")
            del monstergroup
            del collgroup
            del pixelgroup
            raise AIPlayerDeadException()

    def check_for_wall(self, player):
        wall = [0, 0, 0]
        if player is not None:
            playergroup = pygame.sprite.RenderPlain()
            player_right_point = player.rect.right
            player_left_point = player.rect.left

            player_checkright = PlayerAI(player.rect.left, player.rect.top, "playerLeft.png", "playerRight.png", "playerClimb.png",
                                         "scull.png", self.background, self.map)
            playergroup.add(player_checkright)
            player_checkright.xmove = 1
            player_checkright.setXMove()
            playergroup.update()

            if player_checkright.rect.right == player_right_point:
                # print("Wall collision on the right")
                wall[1] = 1
            del player_checkright

            player_checkleft = PlayerAI(player.rect.left, player.rect.top, "playerLeft.png", "playerRight.png", "playerClimb.png",
                                         "scull.png", self.background, self.map)
            playergroup.add(player_checkleft)
            player_checkleft.xmove = -1
            player_checkleft.setXMove()
            playergroup.update()
            if player_checkleft.rect.left == player_left_point:
                # print("Wall collision on the left")
                wall[0] = 1
            del player_checkleft

            player_checkup = PlayerAI(player.rect.left, player.rect.top, "playerLeft.png", "playerRight.png", "playerClimb.png",
                                         "scull.png", self.background, self.map)
            playergroup.add(player_checkup)

            player_checkup.jump = -5.2
            player_checkup.climbMove = 0
            player_checkup.doClimb = False
            player_checkup.doElevator = False
            player_checkup.elevator = None

            playergroup.update()
            if player_checkup.checkUpCollision() is True:
                wall[2] = 1
                # print("Head Collision")

            del player_checkup
            del playergroup

        return wall

    def punish_for_wall_collisions(self, player, reward):
        if player.checkUpCollision() is True:
            reward = reward - 0.2
        return reward

    def check_for_gems(self, player):
        position = [0, 0, 0, 0]
        if player is not None:
            gem_to_player_distances = []
            gems = self.get_gems_group()

            #calculate distances of gems to player
            for gem in gems:
                distance = self.rect_distance(player.rect, gem.rect)
                distance_rect_list = [distance, gem.rect]

                if distance > 0:
                    gem_to_player_distances.append(distance_rect_list)

            gem_to_player_distances = sorted(gem_to_player_distances, key=itemgetter(0))

            #calculate position of the closest gem in relation to the player
            position = self.calculate_position_of_rectangle_in_relation_to_another_rectangle(player.rect, gem_to_player_distances[0][1])

        del gem_to_player_distances
        del distance_rect_list
        return position

    def check_for_ladders(self, player):
        position = [0, 0, 0, 0, 0]
        if player is not None:
            object_to_player_distances = []
            usable_objects = self.get_ladder_group()

            # calculate distances of gems to player
            for usable_object in usable_objects:
                distance = self.rect_distance(player.rect, usable_object.rect)
                distance_rect_list = [distance, usable_object.rect]

                if distance > 0:
                    object_to_player_distances.append(distance_rect_list)

            gem_to_player_distances = sorted(object_to_player_distances, key=itemgetter(0))

            # calculate position of the closest gem in relation to the player
            position = self.calculate_position_of_rectangle_in_relation_to_another_rectangle(player.rect,
                                                                                             gem_to_player_distances[0][1], False)
        del object_to_player_distances
        del usable_objects
        del distance_rect_list
        return position

    def check_for_elevators(self, player):
        position = [0, 0, 0, 0, 0]
        # elevators_to_player_distances = [0, 0, 0, 0, 0]
        # usable_objects = self.get_elevators_group()
        #
        # if player is not None:
        #     # calculate distances of gems to player
        #     for usable_object in usable_objects:
        #         distance = self.rect_distance(player.rect, usable_object.rect)
        #         distance_rect_list = [distance, usable_object.rect]
        #
        #         if distance > 0:
        #             elevators_to_player_distances.append(distance_rect_list)
        #
        #     gem_to_player_distances = sorted(elevators_to_player_distances, key=itemgetter(0))
        #
        #     # calculate position of the closest gem in relation to the player
        #     if elevators_to_player_distances:
        #         position = self.calculate_position_of_rectangle_in_relation_to_another_rectangle(player.rect,
        #                                                                                      elevators_to_player_distances[0][1], False)
        #     else:
        #         return [0, 0, 0, 0, 0]

        return position

    def check_for_doors(self, player):
        position = [0, 0, 0, 0, 0]
        doors_to_player_distances = []
        usable_objects = self.get_door_group()

        # calculate distances of gems to player
        for usable_object in usable_objects:
            distance = self.rect_distance(player.rect, usable_object.rect)
            distance_rect_list = [distance, usable_object.rect]

            if distance > 0:
                doors_to_player_distances.append(distance_rect_list)

        gem_to_player_distances = sorted(doors_to_player_distances, key=itemgetter(0))

        # calculate position of the closest gem in relation to the player
        if doors_to_player_distances:
            position = self.calculate_position_of_rectangle_in_relation_to_another_rectangle(player.rect,
                                                                                             gem_to_player_distances[
                                                                                                 0][1], False)
        else:
            return [0, 0, 0, 0, 0]

        del gem_to_player_distances
        del doors_to_player_distances
        del usable_objects
        del usable_object
        return position

    '''returns 4 element list [left, right, top, down] filled with zeros or ones'''
    def calculate_position_of_rectangle_in_relation_to_another_rectangle(self, rect1, rect2, have_to_exist=True) -> []:
        #left, right, up, down
        gem_position = [0, 0, 0, 0]

        if have_to_exist is False:
            gem_position.append(0)

        if rect1.left < rect2.left:
            gem_position[1] = 1
        elif rect1.left > rect2.left:
            gem_position[0] = 1
        else:
            pass

        if rect1.top < rect2.top:
            gem_position[3] = 1
        elif rect1.top > rect2.top:
            gem_position[2] = 1
        else:
            pass

        if have_to_exist is False and gem_position[0] + gem_position[1] + gem_position[2] + gem_position[3] > 0:
            gem_position[4] = 1

        if have_to_exist is False and gem_position[0] + gem_position[1] + gem_position[2] + gem_position[3] == 0:
            gem_position[4] = 0

        return gem_position

    def rect_distance(self, rect1, rect2):
        x1, y1 = rect1.topleft
        x1b, y1b = rect1.bottomright
        x2, y2 = rect2.topleft
        x2b, y2b = rect2.bottomright
        left = x2b < x1
        right = x1b < x2
        bottom = y2b < y1
        top = y1b < y2
        if top and left:
            return dist((x1, y1b), (x2b, y2))
        elif left and bottom:
            return dist((x1, y1), (x2b, y2b))
        elif bottom and right:
            return dist((x1b, y1), (x2, y2b))
        elif right and top:
            return dist((x1b, y1b), (x2, y2))
        elif left:
            return x1 - x2b
        elif right:
            return x2 - x1b
        elif bottom:
            return y1 - y2b
        elif top:
            return y2 - y1b
        else:  # rectangles intersect
            return 0.

    def is_gem_close(self, player):
        gem_close_to_player = [0]
        if player is not None:
            player_checkright = PlayerAI(player.rect.right + 5, player.rect.top, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
                                self.background, self.map)

            gem_close = self.check_for_incoming_gem_collision(player_checkright)
            if gem_close:
                # print("Collision in a right in a moment")
                return [1]
            del player_checkright

            player_checkleft = PlayerAI(player.rect.left - 5, player.rect.top, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
                                self.background, self.map)
            gem_left = self.check_for_incoming_gem_collision(player_checkleft)
            if gem_left:
                # print("Collision in a left in a moment")
                return [1]
            del player_checkleft

            player_checkup = PlayerAI(player.rect.left, player.rect.top - 10, "playerLeft.png", "playerRight.png",
                                        "playerClimb.png", "scull.png", \
                                        self.background, self.map)
            gem_up = self.check_for_incoming_gem_collision(player_checkup)
            if gem_up:
                # print("Collision above")
                return [1]
            del player_checkup

            player_checkdown = PlayerAI(player.rect.left, player.rect.top + 10, "playerLeft.png", "playerRight.png",
                                      "playerClimb.png", "scull.png", \
                                      self.background, self.map)
            gem_down = self.check_for_incoming_gem_collision(player_checkdown)
            if gem_down:
                # print("Collision below")
                return [1]
            del player_checkdown

            return gem_close_to_player

    def check_for_danger(self, player) -> []:
        '''[left, right, up, down]'''
        danger = [0, 0, 0, 0]
        if player is not None:
            player_checkright = PlayerAI(player.rect.right + 2, player.rect.top, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
                                self.background, self.map)

            danger_right = self.check_for_incoming_collision(player_checkright)
            if danger_right:
                # print("Collision in a right in a moment")
                return [0, 1, 0, 0]
            del player_checkright

            player_checkleft = PlayerAI(player.rect.left - 2, player.rect.top, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
                                self.background, self.map)
            danger_left = self.check_for_incoming_collision(player_checkleft)
            if danger_left:
                # print("Collision in a left in a moment")
                return [1, 0, 0, 0]
            del player_checkleft

            player_checkup = PlayerAI(player.rect.left, player.rect.top - 5, "playerLeft.png", "playerRight.png",
                                        "playerClimb.png", "scull.png", \
                                        self.background, self.map)
            danger_up = self.check_for_incoming_collision(player_checkup)
            if danger_up:
                # print("Collision above")
                return [0, 0, 1, 0]
            del player_checkup

            player_checkdown = PlayerAI(player.rect.left, player.rect.top + 5, "playerLeft.png", "playerRight.png",
                                      "playerClimb.png", "scull.png", \
                                      self.background, self.map)
            danger_down = self.check_for_incoming_collision(player_checkdown)
            if danger_down:
                # print("Collision below")
                return [0, 0, 0, 1]
            del player_checkdown

        return danger

    def check_for_danger_right(self, point):
        player = PlayerAI(point.x, point.y, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
                            self.background, self.map)
        danger = False
        try:
            self.check_for_fire_collision(player)
            self.check_for_bat_collision(player)
            self.check_for_monster_collision(player)
        except AIPlayerDeadException:
            danger = True
        finally:
            del player
        return danger

    def check_for_time_up(self):
        # check player time, if time is up he is dead
        if self.bonus == 0:
            raise AIPlayerDeadException()

    def check_for_too_long_playing_without_effect(self):
        if self.frame_iteration > 100:
            raise AIPlayerDeadException()

    def reset_player_position(self, game, player):
        gemgroup = self.map.fetchGemgroup()
        self.gemcnt = len(gemgroup)
        monstergroup = self.map.fetchMonstergroup()
        laddergroup = self.map.fetchLaddergroup()
        elevatorgroup = self.map.fetchElevatorgroup()
        firegroup = self.map.fetchFiregroup()
        doorgroup = self.map.fetchDoorgroup()
        batgroup = self.map.fetchBatgroup()
        collgroup = None

        # # Draw screen
        # self.screen.blit(self.background, (0, 0))
        # pygame.display.flip()

        # Create player sprite
        # self.startSound.play()
        # player = PlayerAI(xpos, ypos, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
        #                   self.background, self.map)
        # player = PlayerAI(40, 600, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
        #                     game.background, game.map)
        playergroup = pygame.sprite.RenderPlain()

        playergroup.add(player)

        self.check_if_player_on_the_ladder(player)

        # gemgroup.update()
        # monstergroup.update()
        # laddergroup.update()
        # elevatorgroup.update()
        # batgroup.update()
        # playergroup.update()
        # firegroup.update()

        ##################################################
        ### Print game state
        ##################################################

        game.addText("Bonus: " + str(game.bonus), game.background, 10, 5, THECOLORS['lightblue'],
                     THECOLORS['black'], 22, False, 30)
        game.addText("Score: " + str(game.score), game.background, 450, 5, THECOLORS['orange'])
        game.addText("Lives: " + str(game.lives), game.background, 950, 5, THECOLORS['green'])

        ##################################################
        ### Draw self.background and sprites on screen
        ##################################################

        game.screen.blit(game.background, (0, 0))
        laddergroup.draw(game.screen)
        playergroup.draw(game.screen)
        elevatorgroup.draw(game.screen)
        gemgroup.draw(game.screen)
        firegroup.draw(game.screen)
        monstergroup.draw(game.screen)
        batgroup.draw(game.screen)

        del monstergroup
        del batgroup
        del firegroup
        del gemgroup
        del elevatorgroup
        del playergroup
        del laddergroup

        if (game.gemcnt == 0):
            # if not doorsoundPlayed:
            #     self.doorSound.play()
            #     doorsoundPlayed = True
            doorgroup.draw(game.screen)

        pygame.display.flip()

    def check_if_player_on_the_ladder(self, player):
        # Check player with ladder collisions
        laddergroup = self.get_ladder_group()
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

        del laddergroup
        del tile2
        del tile1

    def _move(self, playerAI, action):
        # [left, right up, down, jump]
        # action = [1, 0, 0, 0, 0, 0]
        if playerAI is not None:
            if not np.array_equal(action, [0, 0, 0, 0, 0]): #???
                if np.array_equal(action, [0, 0, 0, 0, 1]):  # up
                    if (playerAI.jump == 0 and playerAI.ymove == 0) \
                            or playerAI.doElevator == True:
                        # self.jumpSound.play()
                        playerAI.jump = -5.2
                        playerAI.climbMove = 0
                        playerAI.doClimb = False
                        playerAI.doElevator = False
                        playerAI.elevator = None
                if np.array_equal(action, [1, 0, 0, 0, 0]):  # left
                    playerAI.xmove = -1
                if np.array_equal(action, [0, 1, 0, 0, 0]):  # right
                    playerAI.xmove = 1
                if np.array_equal(action, [0, 0, 1, 0, 0]):  # up
                    if playerAI.canClimb:
                        playerAI.doClimb = True
                        playerAI.climbMove = -1
                if np.array_equal(action, [0, 0, 0, 1, 0]):  # down
                    if playerAI.canClimb:
                        playerAI.doClimb = True
                        playerAI.climbMove = 1
            else:
                if np.array_equal(action, [0, 1, 0, 0, 0]) and playerAI.xmove > 0: #right
                    playerAI.xmove = 0
                if np.array_equal(action, [1, 0, 0, 0, 0]) and playerAI.xmove < 0: #left
                    playerAI.xmove = 0
                if np.array_equal(action, [0, 0, 1, 0, 0]) or np.array_equal(action, [0, 0, 0, 1, 0, 0]) and playerAI.doClimb: #up or down
                    playerAI.climbMove = 0
                    playerAI.doClimb = False

    def _update_ui(self):
        pass

    def init_ui2(self, game):
        game.lastBonusDecTime = pygame.time.get_ticks()
        # game.levelcnt += 1
        game.totallevelcnt += 1
        if game.levelcnt >= len(game.maps):
            game.levelcnt = 0
            game.beginbonus -= 500
        game.map = LevelMap("wall.png", "wall1.png", "wall2.png", game.maps[game.levelcnt], game.yoff)

    def get_playerai_beginning_position(self):
        return PlayerAI(40, 600, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
                            self.background, self.map)

    def get_fire_group(self):
        return self.map.fetchFiregroup()

    def get_bat_group(self):
        return self.map.fetchBatgroup()

    def get_monster_group(self):
        return self.map.fetchMonstergroup()

    def get_gems_group(self):
        return self.map.fetchGemgroup()

    def get_ladder_group(self):
        return self.map.fetchLaddergroup()

    def get_elevators_group(self):
        return self.map.fetchElevatorgroup()

    def get_door_group(self):
        return self.map.fetchDoorgroup()