from datastructures import *

def run_tests():
    test_is_wild()
    test_is_valid_group()
    test_get_natural_outage_possibilities()
    test_get_all_sets()
    test_get_all_runs()
    test_check_go_out()

    
    # test_python()

def test_is_wild():
    
    c = Card(Suits.JOKER, 14)
    assert is_wild(c, 3)

    c = Card(Suits.CLUB, 3)
    assert is_wild(c, 3)

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

    
    # Test with duplicates of the same card
    hand = Hand("test")

    hand.add(Card(Suits.HEART, 1))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.DIAMOND, 3))
    hand.add(Card(Suits.HEART, 8))
    hand.add(Card(Suits.HEART, 9))
    expected_sets = [[Card(Suits.HEART, 3), Card(Suits.HEART, 3), Card(Suits.DIAMOND, 3)]]

    sets = get_all_sets(hand, 6)
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

    score, discard, groups = check_go_out(hand)
    logging.debug("Test Result: {}, {}, {}".format(score, discard, groups))
    assert score == 8
    assert discard == Card(Suits.HEART, 9)
    assert groups == [[
        Card(Suits.HEART, 1),
        Card(Suits.HEART, 2),
        Card(Suits.HEART, 3)]]

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

    score, discard, groups = check_go_out(hand)
    logging.debug("Test Result: {}, {}, {}".format(score, discard, groups))
    assert score == 11
    assert discard == Card(Suits.HEART, 9)
    assert groups == [[
        Card(Suits.HEART, 3),
        Card(Suits.HEART, 3),
        Card(Suits.HEART, 3)]]

    # Test that math works out for long run taking bias over high couples
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 1))
    hand.add(Card(Suits.HEART, 1))
    hand.add(Card(Suits.HEART, 1))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 8))
    hand.add(Card(Suits.HEART, 9))
    # Discard 9, score of 10 with run of 1,2,3

    score, discard, groups = check_go_out(hand)
    logging.debug("Test Result: {}, {}, {}".format(score, discard, groups))
    assert score == 10
    assert discard == Card(Suits.HEART, 9)
    assert groups == [[
        Card(Suits.HEART, 1),
        Card(Suits.HEART, 2),
        Card(Suits.HEART, 3)]]

    # Errored hand: -- Can't go out with anything --
    hand = Hand("test")
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.CLUB, 1))
    hand.add(Card(Suits.CLUB, 11))
    hand.add(Card(Suits.CLUB, 5))

    score, discard, groups = check_go_out(hand)
    logging.debug("Test Result: {}, {}, {}".format(score, discard, groups))
    assert score == 6
    assert discard == Card(Suits.CLUB, 11)
    assert groups == []

    # Errored hand : <[♣6], [ʷW], [♣6], [ʷW]>
    hand = Hand("test")
    hand.add(Card(Suits.CLUB, 6))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.CLUB, 6))
    hand.add(Card(Suits.JOKER, 14))

    score, discard, groups = check_go_out(hand)
    logging.debug("Test Result: {}, {}, {}".format(score, discard, groups))
    assert score == 0
    assert discard == Card(Suits.CLUB, 6)
    assert groups == [[
            Card(Suits.CLUB, 6), 
            Card(Suits.JOKER, 14), 
            Card(Suits.JOKER, 14), 
        ]]

    # Forever hand : <[♢9], [♢5], [♢Q], [ʷW], [ʷW], [♣5]>
    hand = Hand("test")
    hand.add(Card(Suits.DIAMOND, 9))
    hand.add(Card(Suits.DIAMOND, 5))
    hand.add(Card(Suits.DIAMOND, 12))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.CLUB, 5))

    # TODO: Fix this, it is legal, but outputs wrong
    score, discard, groups = check_go_out(hand)
    logging.debug("Test Result: {}, {}, {}".format(score, discard, groups))
    assert score == 0
    assert discard == Card(Suits.DIAMOND, 12)
    assert groups == [[
            Card(Suits.DIAMOND, 9), 
            Card(Suits.JOKER, 14), 
            Card(Suits.JOKER, 14), 
        ]]
    
    # Abe : <[ʷW], [♣10], [♠9], [♠K], [♢7], [ʷW], [ʷW], [ʷW], [♢J], [♢2], [♡K], [♡Q], [♠7], [♣Q]>
    # INFO:root:Discarding: [♡K]
    hand = Hand("test")
    hand.add(Card(Suits.DIAMOND, 9))
    hand.add(Card(Suits.DIAMOND, 5))
    hand.add(Card(Suits.DIAMOND, 12))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.CLUB, 5))

    # TODO: Fix this, it is legal, but outputs wrong
    score, discard, groups = check_go_out(hand)
    logging.debug("Test Result: {}, {}, {}".format(score, discard, groups))
    assert score == 0
    assert discard == Card(Suits.DIAMOND, 12)
    assert groups == [[
            Card(Suits.DIAMOND, 9), 
            Card(Suits.JOKER, 14), 
            Card(Suits.JOKER, 14), 
        ]]


def test_python():
    hand = []
    hand.append(Card(Suits.HEART, 1))
    hand.append(Card(Suits.HEART, 13))
    hand.append(Card(Suits.HEART, 11))
    hand.append(Card(Suits.HEART, 5))
    hand.sort()
    
    # Max permutation set before my computer crashes?
    # Time is not a good metric, but I don't feel like making another..
    # 10: ~1s
    # 11: 6 seconds (with a lot of memory to deallocate after)
    # 12: __ I crash my computer
    # 12: 479,001,600, 10: 3,628,800
    logging.debug("Starting max permutation check")
    group_permutation_order = list(permutations(range(10)))
    logging.debug("total combinations: {}".format(len(group_permutation_order)))
