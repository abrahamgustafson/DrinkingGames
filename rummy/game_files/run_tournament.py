import argparse
from game import *

from itertools import combinations
from random import shuffle
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
import numpy as np

class Elo:
    base_rating = 1000
    players = None
    def __init__(self):
        self.players = {}

    def getPlayerRating(self, name):
        return self.players[name]

    def contains(self, name):
        return name in self.players.keys()

    def addPlayer(self, name, rating=None):
        if rating == None:
            rating = self.base_rating

        self.players[name] = rating

    def _compare_rating(self, first, second):
        return (1 + 10 ** ((second - first) / 400.0 )) ** -1


    def recordMatch(self, name1, name2, winner=None):
        ratings = np.array([self.players[name1], self.players[name2]])
        expected = np.array([self._compare_rating(ratings[0], ratings[1]),
                             self._compare_rating(ratings[1], ratings[0])])
        
        k = len(self.players.keys()) * 42

        if not winner:
            scores = np.array([0.5, 0.5])
        elif winner == name1:
            scores = np.array([1.0, 0.0])
        elif winner == name2:
            scores = np.array([0.0, 1.0])
        else:
            raise Exception("Invalid winner supplied {}".format(winner))

        new_ratings = ratings + k * (scores - expected)

        if new_ratings[0] < 0:
            new_ratings = np.array([0, np.diff(ratings)])
        if new_ratings[1] < 0:
            new_ratings = np.array([np.diff(ratings.flip()), 0])

        self.players[name1], self.players[name2] = new_ratings

    def getRatingList(self):
        ratings = []
        for player, rating in self.players.items():
            ratings.append((player, rating))
        return ratings

class SlightlyBetterPlayer(Player):
    def should_draw_from_discard(self, round):
        potential_draw = round.discard_pile.peek()
        potential_hand = Hand(self.hand.player_name)
        potential_hand.cards = copy.deepcopy(self.hand.cards)
        potential_hand.add(potential_draw)

        potential_play = None
        if not round.player_is_out():
            best_play = sorted(self._search_for_n_seconds(potential_hand, round, 0.5), key = lambda x: (len(x[0].cards), x[0].get_score(round.round_number)))[0]
            if len(best_play[0].cards) <= 1:
                potential_play = best_play

        if potential_play:
            return True, potential_play
        else:
            return False, None

def run_script(args):
    all_players = [Player("Abe"), Player("Brenna"), SlightlyBetterPlayer("CardBot")]
    all_matchups = list(map(list, combinations(all_players, 2)))

    elo = Elo()
    for player in all_players:
        elo.addPlayer(player.hand.player_name)

    games = []
    for matchup in all_matchups:
        for i in range(args.num_games):
            if random.randint(0, 1):
                matchup.reverse()
            games.append(matchup)
    shuffle(games)

    logging.critical("Starting tournament between players {}".format(list(map(lambda x: x.hand.player_name, all_players))))
    for players in tqdm(games):
        rummy = Game(players, 2)
        rummy.play()
        scores = sorted(players, key = lambda x: x.score)
        winner = scores[0].hand.player_name if scores[0].score != scores[1].score else None
        elo.recordMatch(*map(lambda x: x.hand.player_name, players), winner = winner)

    logging.critical(elo.getRatingList())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test playground')
    parser.add_argument('--num_games', type=int, default=10, help='The number of games to be pair-wise played between players')
    
    logging.getLogger().setLevel(logging.INFO)

    args = parser.parse_args()
    with logging_redirect_tqdm():
        run_script(args)
