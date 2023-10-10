from datastructures import *

def run_tests():
    test_is_valid_group()


def test_is_valid_group():
    cards = []
    cards.append(Card(Suits.CLUB, 1))
    cards.append(Card(Suits.CLUB, 2))
    cards.append(Card(Suits.CLUB, 3))
    assert is_valid_group(cards, 3)
    
    cards = []
    cards.append(Card(Suits.JOKER, 14))
    cards.append(Card(Suits.CLUB, 2))
    cards.append(Card(Suits.CLUB, 3))
    assert is_valid_group(cards, 3)
    
    cards = []
    cards.append(Card(Suits.JOKER, 14))
    cards.append(Card(Suits.JOKER, 14))
    cards.append(Card(Suits.JOKER, 3))
    assert is_valid_group(cards, 3)

    cards = []
    cards.append(Card(Suits.HEART, 6))
    cards.append(Card(Suits.JOKER, 14))
    cards.append(Card(Suits.HEART, 8))
    assert is_valid_group(cards, 3)

    cards = []
    cards.append(Card(Suits.HEART, 6))
    cards.append(Card(Suits.JOKER, 14))
    cards.append(Card(Suits.CLUB, 8))
    assert not is_valid_group(cards, 3)

    cards = []
    cards.append(Card(Suits.HEART, 6))
    cards.append(Card(Suits.JOKER, 14))
    cards.append(Card(Suits.CLUB, 6))
    assert is_valid_group(cards, 3)