"""Data structures"""

import random
from enum import Enum


CARD_POINT_MAP = {
    'A': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'J': 10,
    'Q': 10,
    'K': 10,
    'W': 0
}

CARD_TEXT_MAP = {
    1: 'A',
    2: '2',
    3: '3',
    4: '4',
    5: '5',
    6: '6',
    7: '7',
    8: '8',
    9: '9',
    10: '10',
    11: 'J',
    12: 'Q',
    13: 'K',
    14: 'W'
}

SUIT_TEXT_MAP = {
    0: '\u2663',
    1: '\u2660',
    2: '\u2661',
    3: '\u2662',
    4: '\u02B7'
}


class Suits(Enum):
    CLUB = 0
    SPADE = 1
    HEART = 2
    DIAMOND = 3
    JOKER = 4


class Card:
    suit = None
    value = None
    # Add visualization

    def __init__(self, suit, value):
        """
        Args:
            suit(Suits): suit of card
            value(int): int number of card (EG, Ace is 1)
        """
        self.suit = suit
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit and self.value == other.value
        return False
    
    def __sub__(self, other):
        return self.value - other.value
    
    def __str__(self):
        return "[{}{}]".format(SUIT_TEXT_MAP[self.suit.value], CARD_TEXT_MAP[self.value])
    
    def same_suit(self, other):
        return self.suit == other.suit
    
    def same_value(self, other):
        return self.value == other.value


class Deck:
    cards = None

    def __init__(self, decks=2):
        self.cards = []
        for _ in range(0, decks):
            for suit in Suits:
                if suit == Suits.JOKER:
                    continue
                for value in range(1,14):
                    self.cards.append(Card(suit, value))
                for _ in range(0, 2):
                    self.cards.append(Card(Suits.JOKER, 14))

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

    def length(self):
        return len(self.cards)


class Hand:
    cards = None
    player_name = None

    def __init__(self, player_name):
        self.cards = []
        self.player_name = player_name
    
    def add(self, card):
        """
        Args:
            card(Card): card to add to the hand
        """
        self.cards.append(card)

    def remove(self, card):
        """
        Args:
            card(Card): card to remove from your hand
        Returns: bool (success)
        """
        for c in self.cards:
            if c == card:
                self.cards.remove(card)
                return True
        return False
    
    def __str__(self):
        s = "{} : ".format(self.player_name)
        first = True
        for card in self.cards:
            if first:
                s += "<"
                first = False
            else:
                s += ", "
            s += "{}".format(str(card))
        s += ">"
        return s

    def sort(self):
        self.cards.sort(key=lambda x: x.value, reverse=True)
    

class DiscardPile:
    cards = None

    def __init__(self):
        self.cards = []
    
    def add(self, card):
        """
        Args:
            card(Card): card to add to the hand
        """
        self.cards.append(card)

    def pop(self):
        return self.cards.pop()
    
    def peek(self):
        return self.cards[len(self.cards) - 1]
    

def is_wild(card, round):
    """
    Is a card wild or not
    """
    return card.value == 14 or card.value == round or card.suit == Suits.JOKER


def is_valid_group(card_list, round):
    """
    Check if a grouping of cards is valid to combine together.
    Assumes cards are sorted (and that wilds are in the slot they need to be)

    Args:
        card_list(List(Card)): List of cards in a grouping to consider.
        round(int): Round of cards, aka, which card is wild
    """
    if len(card_list) < 3:
        return False
    if round < 3 or round > 13:
        return False
    
    last_non_wild = None
    is_duplicates = True
    is_run = True
    running_wild_counter = 0

    for idx, card in enumerate(card_list):
        if not last_non_wild:
            if is_wild(card, round):
                running_wild_counter += 1
            else:
                last_non_wild = card
                running_wild_counter = 0
            continue

        if is_wild(card, round):
            running_wild_counter += 1
            continue

        # If it is card 4 which is a 8*, card 3 was wild, and card 2 was a 6*
        last_card = card_list[idx - (running_wild_counter + 1)]

        if not card.same_value(last_card):
            is_duplicates = False

        if not card.same_suit(last_card):
            is_run = False
        else:
            if (card - last_card) != (running_wild_counter + 1):
                is_run = False

        if not is_duplicates and not is_run:
            return False

        # Implicitly not a wild if we hit this path.
        running_wild_counter = 0

    return True

    
    

def check_go_out(hand, existing_groups=None):
    """
    Check if you can go out. 
    TODO: Need to sort out how I will call this (if you can't go out, what do you discard?)

    Args:
        hand(Hand): hand with an assumed extra card drawn
        existing_groups(list): List of existing groups of cards that are out
    Returns:
        score(int): Implied to be 0, -5, or -15 based on the existence of existing_groups.
        discard: popped off the hand
    """
    if not existing_groups:
        existing_groups = list()

    pass


