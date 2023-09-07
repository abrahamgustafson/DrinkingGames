import argparse
from datastructures import *

class Round:

    player_list = None
    deck = None
    discard_pile = None
    player_to_hand_map = dict()
    next_player_index = 0


    def __init__(self, player_list, round, decks=2):
        """
        Args:
            player_list(list(string)): list of string player names. Ordered by turn order.
        """
        if round < 3 or round > 13:
            raise Exception("Round must be between 3 and 13")
        if len(player_list) < 2:
            raise Exception("Must have at lest 2 players")
        
        print("Round {} beginning. First player: {}".format(round, player_list[0]))
        
        self.player_list = player_list
        self.deck = Deck(decks)
        self.deck.shuffle()
        self.discard_pile = DiscardPile()
        
        for player in player_list:
            self.player_to_hand_map[player] = Hand(player)

        for _ in range(0, round):
            for player in player_list:
                self.player_to_hand_map[player].add(self.deck.deal())

        self.discard_pile.add(self.deck.deal())

    def print_state(self):
        for _, hand in self.player_to_hand_map.items():
            print(hand)

    def get_next_player(self):
        return self.next_player_index
    
    def draw_from_deck(self):
        # Don't let someone draw twice.
        self.player_to_hand_map[self.player_list[self.get_next_player()]].add(self.deck.deal())

    def draw_from_discard(self):
        self.player_to_hand_map[self.player_list[self.get_next_player()]].add(self.discard_pile.pop())

    def peek_discard(self):
        return self.discard_pile.peek()


class Game:
    player_list = None
    player_score_map = dict()
    active_round = None
    decks = 0

    def __init__(self, player_list, decks=2):
        """
        Args:
            player_list(list(string)): list of string player names
        """
        print("Starting game with players: {}".format(player_list))
        self.player_list = player_list
        self.decks = decks
        for player in player_list:
            self.player_score_map[player] = 0

    def initialize_round(self, round):
        # Todo, rotate next starter...
        self.active_round = Round(self.player_list, round, self.decks)
        return self.active_round
        

def run_script():

    player_list = ["Abe", "Brenna"]
    game = Game(player_list, 2)
    round = game.initialize_round(3)

    # print("Player hands:\n{}".format(round.player_to_hand_map))
    round.print_state()
    print(round.peek_discard())
    round.draw_from_discard()
    round.draw_from_deck()
    round.print_state()
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test playground')
    # parser.add_argument('--game_csv', metavar='[GAME.csv]', type=str,
    #                     help='Name of file in DrinkingGames/rummy/datasets/')
    args = parser.parse_args()
    print(args)

    # load_all_games()
    # run_script(**vars(args))
    run_script()