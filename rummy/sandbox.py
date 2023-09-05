"""
ToDo: 
 - Build player filtering
 - Get Christine's data
 - Get Mom and Dad's data
 - 

Analysis ideas
 [ ] See which rounds are the bloodiest
 [ ] ^ But filtered by player count
 [ ] Probability of winning a game over time
 [ ] Who has the best relative end score (average points +/- relative to opponents)
"""

import argparse
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import itertools


DEBUG_ENABLED = False
ROUNDS = 11
ROUND_OFFSET = 3

class Game:
    """Data class for holding a single Game"""

    def __init__(self, user_to_score_map, file_name):
        """
        Args:
           user_to_score_map: map<string, list(score)>
        """
        self.user_to_score_map = user_to_score_map
        self.file_name = file_name
        print("loading:   [{}]".format(self.file_name))
        self._validate()
        print("validated: [{}]".format(self.file_name))

    def _validate(self):
        assert len(self.user_to_score_map) > 0
        for _, scores in self.user_to_score_map.items():
            if(DEBUG_ENABLED):
                print("File: {}, {}/{}".format(self.file_name, len(scores), ROUNDS))
            assert len(scores) == ROUNDS

    def player_count(self):
        return len(self.user_to_score_map)

    def players(self):
        return self.user_to_score_map.keys()

    def scores(self):
        return self.user_to_score_map

    def score_array(self):
        """
        Return a 2d array of scores
        """
        pass

    # map<string, list(score)>
    user_to_score_map = dict()


def load_game(file_path):
    """
    Args:
        file_path(string): absolute path to file.
    Returns:
        game
    """
    with open(file_path, encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file)

        # Iterate over each row in the csv using reader object
        is_first_row = True

        user_to_score_map = dict()
        user_order_map = dict()

        for row in csv_reader:
            if is_first_row:
                is_first_row = False
                for idx, person in enumerate(row):
                    user_to_score_map[person] = list()
                    user_order_map[idx] = person
                continue
            
            for idx, score in enumerate(row):
                user_to_score_map[user_order_map[idx]].append(int(score))

        game = Game(user_to_score_map, file_path)

    return game

def bloodiest_round_stats(games, player_count_filter=0):
    """
    Print out statistics by round for the average point differential.
    Going to divide by player count for now

    Args:
        games(list(Game)): list of games to analyze.
    """
    overall_round_score_change = [0] * ROUNDS
    overall_round_score_change_abs = [0] * ROUNDS

    for game in games:
        if (player_count_filter > 0 and game.player_count() != player_count_filter):
            continue

        round_score_change = [0] * ROUNDS
        round_score_change_abs = [0] * ROUNDS
    
        last_player_score = [0] * game.player_count()
        
        if (DEBUG_ENABLED):
            print("Game start ----")

        # Safe due to Game::_validate()
        for round in range(0, ROUNDS):
            this_round_score = [game.scores()[player][round] for player in game.players()]

            deviation_by_player = [0] * game.player_count()
            total_round_score_diff = 0
            total_round_score_diff_abs = 0

            for player_idx, score in enumerate(this_round_score):
                dev = score - last_player_score[player_idx]
                deviation_by_player[player_idx] = dev
                total_round_score_diff += dev
                total_round_score_diff_abs += abs(dev)
            
            if (total_round_score_diff != 0):
                round_score_change[round] = total_round_score_diff / game.player_count()
                overall_round_score_change[round] += total_round_score_diff / game.player_count()
            if (total_round_score_diff_abs != 0):
                round_score_change_abs[round] = total_round_score_diff_abs / game.player_count()
                overall_round_score_change_abs[round] += total_round_score_diff_abs / game.player_count()
            last_player_score = this_round_score

            if (DEBUG_ENABLED):
                print("[{}] - round_score_change: {}".format(round + ROUND_OFFSET, round_score_change[round]))
                print("[{}] - round_score_change_abs: {}".format(round + ROUND_OFFSET, round_score_change_abs[round]))
        
        if (DEBUG_ENABLED):
            print("Game end   ----")

    for round in range(0, ROUNDS):
        if (overall_round_score_change[round] != 0):
            print("[{}] - overall_round_score_change: {}".format(round + ROUND_OFFSET, overall_round_score_change[round] / len(games)))
        
        # if (overall_round_score_change_abs[round] != 0):
        #     print("[{}] - overall_round_score_change_abs: {}".format(round + ROUND_OFFSET, overall_round_score_change_abs[round] / len(games)))


def load_all_games():
    datasets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datasets")
    game_files = [f for f in os.listdir(datasets_dir) if os.path.isfile(os.path.join(datasets_dir, f))]

    games = []
    for game_file in game_files:
        games.append(load_game(os.path.join(datasets_dir, game_file)))
    return games

def run_script():
    """
    Args:
        game_csv(string): String file assumed to be in datasets dir
    """
    games = load_all_games()
    bloodiest_round_stats(games)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test playground')
    # parser.add_argument('--game_csv', metavar='[GAME.csv]', type=str,
    #                     help='Name of file in DrinkingGames/rummy/datasets/')
    args = parser.parse_args()
    print(args)

    # load_all_games()
    # run_script(**vars(args))
    run_script()



# BUGS:

