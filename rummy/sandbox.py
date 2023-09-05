import argparse
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import itertools


DEBUG_ENABLED = True


class Game:
    """Data class for holding a single Game"""

    def __init__(self, user_to_score_map, date, round):
        """
        Args:
           user_to_score_map: map<string, list(score)>
        """
        self.user_to_score_map = user_to_score_map
        self.date = date
        self.round = round

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
                print(row)
                for idx, person in enumerate(row):
                    user_to_score_map[person] = list()
                    user_order_map[idx] = person
                continue
            
            for idx, score in enumerate(row):
                user_to_score_map[user_order_map[idx]].append(score)

        game = Game(user_to_score_map, 0, 0)
    return game

def load_all_games():
    datasets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datasets")
    game_files = [f for f in os.listdir(datasets_dir) if os.path.isfile(os.path.join(datasets_dir, f))]

    games = []
    for game_file in game_files:
        games.append(load_game(os.path.join(datasets_dir, game_file)))
    print(games)

def run_script(game_csv):
    """
    Args:
        game_csv(string): String file assumed to be in datasets dir
    """
    full_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datasets", game_csv)
    game = load_game(full_filepath)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test playground')
    parser.add_argument('--game_csv', metavar='[GAME.csv]', type=str,
                        help='Name of file in DrinkingGames/rummy/datasets/')
    args = parser.parse_args()
    print(args)

    load_all_games()
    # run_script(**vars(args))



# BUGS: