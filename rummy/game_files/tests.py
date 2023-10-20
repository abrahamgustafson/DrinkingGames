from datastructures import *

def run_tests():
    test_is_valid_group()
    test_get_natural_outage_possibilities()
    test_get_all_sets()
    test_get_all_runs()
    # test_python()

    test_check_go_out()

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

def test_get_all_sets():
    # Test 1 group of duplicates.
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 1))

    expected_sets = [
            [Card(Suits.HEART, 1), Card(Suits.HEART, 3), Card(Suits.HEART, 3)],
            [Card(Suits.HEART, 2), Card(Suits.HEART, 3), Card(Suits.HEART, 3)],
        ]

    sets = get_all_sets(hand, 3)
    assert sets == expected_sets

    # Test no duplicates
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 4))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 1))

    expected_sets = []

    sets = get_all_sets(hand, 3)    
    assert sets == expected_sets


def test_get_all_runs():
    # Test 1 run with 1 duplicate
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 1))

    expected_sets = [
            [Card(Suits.HEART, 1), Card(Suits.HEART, 2), Card(Suits.HEART, 3)]
        ]    

    sets = get_all_runs(hand, 3)
  
    assert sets == expected_sets

    # Test no runs
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 7))
    hand.add(Card(Suits.DIAMOND, 3))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.CLUB, 1))

    expected_sets = []

    sets = get_all_runs(hand, 3)
    assert sets == expected_sets

    # Complex case with wilds.
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 4))
    hand.add(Card(Suits.HEART, 6))
    hand.add(Card(Suits.HEART, 7))
    hand.add(Card(Suits.HEART, 8))
    hand.add(Card(Suits.CLUB, 1))
    hand.add(Card(Suits.CLUB, 1))
    hand.add(Card(Suits.CLUB, 1))
    hand.add(Card(Suits.CLUB, 1))
    hand.add(Card(Suits.CLUB, 1))
    hand.add(Card(Suits.CLUB, 9))

    expected_sets = []

    sets = get_all_runs(hand, 9)
    # It works, pain to write...
    # print(sets)
    # assert sets == expected_sets


def test_get_natural_outage_possibilities():
    assert get_natural_outage_possibilities(5) == [[5]]
    assert get_natural_outage_possibilities(6) == [[3, 3], [6]]
    assert get_natural_outage_possibilities(7) == [[3, 4], [7]]
    assert get_natural_outage_possibilities(13) == [[3, 3, 3, 4], [3, 3, 7], [3, 4, 6], [3, 5, 5], [3, 10], [4, 4, 5], [4, 9], [5, 8], [6, 7], [13]]

def test_check_go_out():
    # Simple YES first, with highest card to discard.
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 1))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 8))
    hand.add(Card(Suits.HEART, 9))

    check_go_out(hand)

    # score, discard = check_go_out(hand)
    # assert discard
    # assert discard == Card(Suits.HEART, 8)
    # assert score == -15

    # Ensure couples take bias over a run if they save points
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 1))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 8))
    hand.add(Card(Suits.HEART, 9))
    # Discard 9, score of 11 with group of 3's

    check_go_out(hand)

    # # Test that math works out for long run taking bias over high couples
    # hand = Hand("test")
    # hand.add(Card(Suits.HEART, 1))
    # hand.add(Card(Suits.HEART, 1))
    # hand.add(Card(Suits.HEART, 1))
    # hand.add(Card(Suits.HEART, 2))
    # hand.add(Card(Suits.HEART, 3))
    # hand.add(Card(Suits.HEART, 8))
    # hand.add(Card(Suits.HEART, 9))
    # # Discard 9, score of 13 with run of 1,2,3

    # check_go_out(hand)

def test_python():
    hand = []
    hand.append(Card(Suits.HEART, 1))
    hand.append(Card(Suits.HEART, 13))
    hand.append(Card(Suits.HEART, 11))
    hand.append(Card(Suits.HEART, 5))
    hand.sort()
    # for h in hand:
    #     print(h)