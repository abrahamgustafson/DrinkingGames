import argparse
from datastructures import *
from tests import run_tests

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
    
    def print_player_state(self):
        print(self.player_to_hand_map[self.player_list[self.get_next_player()]])

    def get_next_player(self):
        return self.next_player_index
    
    def get_next_player_name(self):
        return self.player_list[self.next_player_index]
    
    def next_turn(self):
        if self.next_player_index + 1 >= len(self.player_list):
            self.next_player_index = 0
        else:
            self.next_player_index += 1
    
    def draw_from_deck(self):
        # Don't let someone draw twice.
        self.player_to_hand_map[self.player_list[self.get_next_player()]].add(self.deck.deal())

    def draw_from_discard(self):
        self.player_to_hand_map[self.player_list[self.get_next_player()]].add(self.discard_pile.pop())

    def get_player_hand(self):
        return self.player_to_hand_map[self.player_list[self.get_next_player()]]

    def peek_discard(self):
        return self.discard_pile.peek()
    
    def discard(self, card):
        self.discard_pile.add(card)


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
    round = game.initialize_round(13)  # Tried going up to 5 and it crashed..

    # print("Player hands:\n{}".format(round.player_to_hand_map))
    round.print_state()
    # print(round.peek_discard())

    player_out = False
    turn = 0
    while not player_out:
        turn += 1
        logging.info("---- Total turn: {}, Players turn: {}".format(turn, round.get_next_player_name()))
        logging.info("Drawing from top of deck")
        round.draw_from_deck()
        round.print_player_state()

        # score(int): Implied to be 0, -5, or -15 based on the existence of existing_groups.
        # discard(Card): popped off the hand
        # Groups(List(List(Card))): List of list of cards we would go out with (if this were the round to go out)
        score, discard, groups = check_go_out(round.get_player_hand())

        logging.info("Discarding: {}".format(discard))
        round.discard(discard)

        if score <= 0:
            player_out = True
            logging.info("{} is out! Hand:".format(round.get_next_player_name()))
            for group in groups:
                logging.info(group)


        round.next_turn()

    round.print_state()

    # try_go_out(round.player_to_hand_map["Abe"], 3)
    

"""
Model how to go out -- and calculate score

Thoughts:
  We want this to be able to be used in a play by play decision maker, not solely as a function to 
  go out and calculate score in the most efficient way.  

Primary inputs:
 1. Cards in hand  (regular, wild)
 2. Card to pick (face up, on top of deck)
 3. Cards of other person who went out first (null by default)
Secondary inputs (not needed, could be added at a later date):
 1. All cards in discard pile
 2. All cards that other people picked up off discard pile
 3. Score + situational awareness

Primary outputs:
 1. (Bool) Can you go first? (implied -5 or -15 points)
 2. (Int) How many points do you have?
 3. (Card) Card to discard

Alg options:
 1. Brute force loop.
 2. Construct a lookup index based on 
 3. Do some optimizer and break the problem up.
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test playground')
    # parser.add_argument('--game_csv', metavar='[GAME.csv]', type=str,
    #                     help='Name of file in DrinkingGames/rummy/datasets/')
    
    logging.getLogger().setLevel(logging.INFO)

    args = parser.parse_args()
    print(args)

    # run_tests()

    # load_all_games()
    # run_script(**vars(args))
    run_script()
