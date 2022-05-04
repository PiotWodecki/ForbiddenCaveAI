import time

import pygame
import random
import numpy as np
import torch


from ExitLoopException import ExitLoopException
from GameAI import GameAI
from LevelMap import LevelMap
from PlayerAI import PlayerAI
from collections import deque
from Model import Linear_QNET, QTrainer
from Helper import plot


MAX_MEMORY = 1_000_000
BATCH_SIZE = 10000
LR = 0.02


class Agent:

    def __init__(self):
        self.number_of_games = 0
        self.epsilon = 0  #randomness
        self.gamma = 0.9 #discount rate (<1)
        self.memory = deque(maxlen=MAX_MEMORY) #after max memory - popleft()
        self.model = Linear_QNET(27, 256, 6)
        # self.model = Linear_QNET.load(self)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    # def load_model(self):
    #     if Linear_QNET.if_model_exists() is True:
    #         self.model = Linear_QNET.load()

    def get_state(self, game, player):
        '''
                states: =[
                Danger:
                left right up down

                Wall:
                left right up

                Gems:
                left right up down

                Is_Gem_Close
                Yes/No (1 value)

                Ladders: (check if exists)
                left right up down exists

                Elevators:
                left right up down  exists

                doors
                left right up down exists

                check for diaments and doors
                '''
        # get the position of the player
        dangers = game.check_for_danger(player)
        walls = game.check_for_wall(player)
        gems = game.check_for_gems(player)
        is_gem_close = game.is_gem_close(player)
        ladders = game.check_for_ladders(player)
        elevators = game.check_for_elevators(player)
        doors = game.check_for_doors(player)
        state = dangers + walls + gems + is_gem_close + ladders + elevators + doors
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over)) #popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) #list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, game_overs = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 1000 - self.number_of_games # 80 is hardcoded, we can experiment with it
        # [left, right, up, down, jump, stay]
        final_move = [0, 0, 0, 0, 0, 0]
        if random.randint(0, 2500) < self.epsilon:
            move = random.randint(0, 5)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = GameAI()
    t0 = time.time()
    init_game = True
    try:
        if init_game is True:
        # playerai = PlayerAI(40, 600, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
        #                     game.background, game.map)  # size 40x40
            game.init_ui() # lvl0
            playerai = PlayerAI(40, 600, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
                                game.background, game.map) # size 40x40
            init_game = False
        # while True:
        # Next level
        while True:
            if init_game is True:
                # playerai = PlayerAI(40, 600, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
                #                     game.background, game.map)
                pass

            #get_old_state
            old_state = agent.get_state(game, playerai)

            #get move
            final_move = agent.get_action(old_state)

            #permofm move and get new state
            reward, game_over, score = game.play_step2(playerai, final_move)
            new_state = agent.get_state(game, playerai)

            #train short memory
            agent.train_short_memory(old_state, final_move, reward, new_state, game_over)

            #remember
            agent.remember(old_state, final_move, reward, new_state, game_over)

            if game_over:
                # train the long memory (replay memory or replay experience)
                # plot results
                agent.number_of_games += 1
                agent.train_long_memory()
                game.reset()
                playerai = PlayerAI(40, 600, "playerLeft.png", "playerRight.png", "playerClimb.png", "scull.png", \
                                  game.background, game.map)
                game.reset_player_position(game, playerai)
                init_game = True

                if score > record:
                    record = score
                    agent.model.save()
                    t1 = time.time()
                    total_time =  t1-t0
                    t0 = time.time()

                print('Game: ', agent.number_of_games, '   Score:', score, '   Record:', record)

                plot_scores.append(score)
                total_score += total_score
                mean_score = total_score / agent.number_of_games
                plot_mean_scores.append(mean_score)
                plot(plot_scores, plot_mean_scores)

    except ExitLoopException:
        pass

if __name__ == '__main__':
    train()