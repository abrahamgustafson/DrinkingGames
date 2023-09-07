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
        self.suit = suit
        self.value = value

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Card):
            return self.suit == other.suit and self.value == other.value
        return False
    
    def __str__(self):
        return "[{}{}]".format(SUIT_TEXT_MAP[self.suit.value], CARD_TEXT_MAP[self.value])


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
    
