import argparse
from datastructures import *
from time import time

class Player:
    score = 0
    hand = None
    is_out = False
    name = None
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.is_out = False
        self.hand = Hand()
    
    def reset(self):
        self.score = 0
        self.new_round()

    def new_round(self):
        self.hand.clear()
        self.is_out = False

    def draw_card(self, card):
        self.hand.add(card)

    def should_draw_from_discard(self, round):
        return False, None

    def discard(self, round):
        return self.hand.discard_highest_value(round.round_number)
    
    def determine_play(self, hand, round):
        def check_score(hand):
            highest_value_card = hand.get_highest_value_card(round.round_number)
            if highest_value_card:
                return hand.get_score(round.round_number) - highest_value_card.value
            else:
                return hand.get_score(round.round_number)
        best_play = sorted(self._search_for_n_seconds(hand, round, 5), key = lambda x: check_score(x[0]))[0]
        return best_play

    def play_turn(self, round):
        draw_discard, determined_play = self.should_draw_from_discard(round)

        if (draw_discard):
            self.draw_card(round.draw_from_discard())
        else:
            self.draw_card(round.draw_from_deck())
            determined_play = self.determine_play(self.hand, round)

        if round.player_is_out() or len(determined_play[0].cards) <= 1:
            self._play(determined_play, round)
        
        round.discard(self.discard(round))

    def commit_score(self, round):
        this_round_score = self.hand.get_score(round.round_number)
        self.score += this_round_score
        logging.info("Final round {} score for player {}: {}; player total score: {}".format(round.round_number, self.name, this_round_score, self.score))

    def _play(self, play, round):
        going_out = not round.player_is_out()
        if going_out:
            logging.info("{} going out with play {}".format(self.name, play[1]))
        else:
            logging.info("{} playing {}".format(self.name, play[1]))
        new_public_groups = []
        for move in play[1]:
            move.fix_wilds(round.round_number)
            new_public_groups.append(move.execute_on(self.hand, round.public_groups))
        if going_out:
            round.public_groups.extend(new_public_groups)
        self.is_out = True

    def _search_for_n_seconds(self, hand, round, n):
        start = time()
        found_plays = []
        for play in get_all_plays(hand, round.round_number, round.public_groups):
            found_plays.append(play)

            # Stop the search early if we found a good enough solution
            if time() - start >= n or len(play[0].cards) <= 1:
                return found_plays
        return found_plays

    def __repr__(self):
        return "{}: {}, {}".format(self.name, self.hand, self.score)

class Round:
    player_list = None
    deck = None
    discard_pile = None
    round_number = None
    turn_index = 0
    # Cards on the table that all can play on
    public_groups = []
    turns_deck_empty = 0

    def __init__(self, player_list, round, deck_count=2):
        """
        Args:
            player_list(list(string)): list of string player names. Ordered by turn order.
        """
        if round < 3 or round > 13:
            raise Exception("Round must be between 3 and 13")
        if len(player_list) < 2:
            raise Exception("Must have at least 2 players")
        
        self.round_number = round
        self.public_groups = []
        self.player_list = player_list
        self.turn_index = 0
        self.turns_deck_empty = 0

        logging.info("Round {} beginning. First player: {}".format(round, player_list[self.turn_index]))
        
        self.deck = Deck(deck_count)
        self.deck.shuffle()
        self.discard_pile = DiscardPile()
        
        for player in player_list:
            player.new_round()

        for _ in range(0, round):
            for player in player_list:
                player.draw_card(self.draw_from_deck())

        self.discard_pile.add(self.draw_from_deck())

    def print_state(self):
        for player in self.player_list:
            logging.info(player)

    def player_is_out(self):
        return bool(self.public_groups)

    def get_current_player(self):
        return self.player_list[(self.turn_index + self.round_number) % len(self.player_list)]
    
    def draw_from_deck(self):
        card = self.deck.deal()
        if card:
            logging.info("Drawing from deck: {}".format(card))
        else:
            logging.info("Deck empty! Returning discard draw instead.")
            return self.draw_from_discard()
        return card

    def draw_from_discard(self):
        card = self.discard_pile.pop()
        logging.info("Drawing from discard: {}".format(card))
        return card
    
    def discard(self, card):
        if card:
            logging.info("Discarding: {}".format(card))
            self.discard_pile.add(card)

    def play(self):
        """
        Returns true if the round is over, false if not
        """
        current_player = self.get_current_player()
        logging.info("------------ Turn: {}, player: {} ------------".format(self.turn_index, current_player.name))
        logging.info(current_player)

        someone_out = bool(self.public_groups)
        current_player.play_turn(self)

        if not self.deck.length():
            self.turns_deck_empty += 1
            if self.turns_deck_empty > len(self.player_list):
                return True

        first_to_go_out = not someone_out and current_player.is_out
        
        if first_to_go_out:
            logging.info("First player to go out: {}".format(current_player))

        # We are out either way in this case.
        if first_to_go_out or someone_out:
            logging.info("Score: {}, Hand: {}".format(current_player.hand.get_score(self.round_number), current_player.hand.cards))

        # If there are public groups modified, that means someone has gone out. Log them.
        if first_to_go_out:
            for group in self.public_groups:
                logging.debug("Playing initial public group: {}".format(group))
        if self.player_is_out():
            logging.info("Public cards:\n{}".format(self.public_groups))
        
        deck_empty_too_long = self.turns_deck_empty > len(self.player_list)
        if all(map(lambda x: x.is_out, self.player_list)) or deck_empty_too_long:
            if deck_empty_too_long:
                logging.info("Each player has had a turn with the deck empty, ending the game.")
            for player in self.player_list:
                player.commit_score(self)
            return True
            
        self.turn_index += 1
        return False
    
    def play_until_round_over(self):
        """
        Returns score map
        """
        round_over = False
        self.print_state()
        while not round_over:
            round_over = self.play()

class Game:
    player_list = []
    deck_count = 0

    def __init__(self, players, deck_count=2):
        """
        Args:
            player_list(list(string)): list of string player names
        """
        self.player_list = []
        for player in players:
            self.player_list.append(player)
            player.reset()
        self.deck_count = deck_count

    def play_round(self, round_number):
        round = Round(self.player_list, round_number, self.deck_count)
        logging.info("======================= ROUND START {} =======================".format(round_number))
        round.play_until_round_over()
        logging.info("======================= ROUND OVER  {} =======================".format(round_number))
        logging.info("Round {} over, player scores:\n{}".format(round_number, list(map(lambda x: x.score, self.player_list))))

    def play(self):
        logging.info("Starting game with players: {}".format(self.player_list))
        for round in range(3,14):
            self.play_round(round)
    
    

def run_script():
    while True:
        game = Game([Player("Abe"), Player("Brenna"), Player("CardBot"), Player("Stinky")], 2)
        game.play()

    logging.info("Game over")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test playground')
    
    logging.getLogger().setLevel(logging.INFO)

    args = parser.parse_args()
    print(args)

    run_script()
