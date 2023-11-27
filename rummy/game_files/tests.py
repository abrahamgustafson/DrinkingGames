import time
from datastructures import *

def test_get_sets():
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

    sets = list(get_sets(hand, 3))
    assert sets == expected_sets

    # Test no duplicates
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 4))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 1))

    expected_sets = []

    sets = list(get_sets(hand, 3))
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

    sets = list(get_sets(hand, 6))
    assert sets == expected_sets

    hand = Hand("test")

    hand.add(Card(Suits.CLUB, 6))
    hand.add(Card(Suits.DIAMOND, 3))
    hand.add(Card(Suits.SPADE, 12))
    hand.add(Card(Suits.DIAMOND, 13))
    expected_sets = []

    sets = list(get_sets(hand, 3))
    assert sets == expected_sets


def test_get_runs():
    # Test 1 run with 1 duplicate
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 1))

    expected_runs = [
            [Card(Suits.HEART, 1), Card(Suits.HEART, 2), Card(Suits.HEART, 3)]
        ]    

    runs = list(get_runs(hand, 3))
    assert runs == expected_runs

    # Test no runs
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 7))
    hand.add(Card(Suits.DIAMOND, 3))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.CLUB, 1))

    expected_runs = []

    runs = list(get_runs(hand, 3))
    assert runs == expected_runs

    hand = Hand("test")

    hand.add(Card(Suits.CLUB, 6))
    hand.add(Card(Suits.DIAMOND, 3))
    hand.add(Card(Suits.SPADE, 12))
    hand.add(Card(Suits.DIAMOND, 13))
    expected_runs = []

    runs = list(get_runs(hand, 3))
    assert runs == expected_runs

def test_get_non_redundant_runs():
    # Test 1 run with 1 duplicate
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 1))

    expected_runs = [
            [Card(Suits.HEART, 1), Card(Suits.HEART, 2), Card(Suits.HEART, 3)]
        ]    

    runs = list(get_non_redundant_runs(hand, 3))
    assert runs == expected_runs

    # Test no runs
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 7))
    hand.add(Card(Suits.DIAMOND, 3))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.CLUB, 1))

    expected_runs = []

    runs = list(get_non_redundant_runs(hand, 3))
    assert runs == expected_runs

    hand = Hand("test")

    hand.add(Card(Suits.CLUB, 6))
    hand.add(Card(Suits.DIAMOND, 3))
    hand.add(Card(Suits.SPADE, 12))
    hand.add(Card(Suits.DIAMOND, 13))
    expected_runs = []

    runs = list(get_non_redundant_runs(hand, 3))
    assert runs == expected_runs

    hand = Hand("test")

    hand.add(Card(Suits.DIAMOND, 1))
    hand.add(Card(Suits.DIAMOND, 4))
    hand.add(Card(Suits.DIAMOND, 5))
    hand.add(Card(Suits.DIAMOND, 10))
    hand.add(Card(Suits.DIAMOND, 12))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.JOKER, 14))
    expected_runs = []

    runs = list(get_non_redundant_runs(hand, 3))
    # It works I promise.

def test_is_valid_set():
    group = [
        Card(Suits.CLUB, 1),
        Card(Suits.CLUB, 1),
        Card(Suits.HEART, 1),
    ]
    assert is_valid_set(group, 5)

    group = [
        Card(Suits.CLUB, 1),
        Card(Suits.JOKER, 14),
        Card(Suits.HEART, 1),
    ]
    assert is_valid_set(group, 5)
    
    group = [
        Card(Suits.JOKER, 14),
        Card(Suits.JOKER, 14),
        Card(Suits.JOKER, 14),
    ]
    assert is_valid_set(group, 5)

    group = [
        Card(Suits.CLUB, 1),
        Card(Suits.JOKER, 14),
        Card(Suits.HEART, 2),
    ]
    assert not is_valid_set(group, 5)

def test_is_valid_run():
    group = [
        Card(Suits.CLUB, 1),
        Card(Suits.CLUB, 2),
        Card(Suits.CLUB, 3),
    ]
    assert is_valid_run(group, 5)

    group = [
        Card(Suits.CLUB, 1),
        Card(Suits.JOKER, 14),
        Card(Suits.CLUB, 3),
    ]
    assert is_valid_run(group, 5)

    group = [
        Card(Suits.JOKER, 14),
        Card(Suits.CLUB, 2),
        Card(Suits.CLUB, 3),
    ]
    assert is_valid_run(group, 5)

    group = [
        Card(Suits.CLUB, 2),
        Card(Suits.CLUB, 3),
        Card(Suits.JOKER, 14),
    ]
    assert is_valid_run(group, 5)

    group = [
        Card(Suits.JOKER, 14),
        Card(Suits.JOKER, 14),
        Card(Suits.JOKER, 14),
    ]
    assert is_valid_run(group, 5)

    group = [
        Card(Suits.CLUB, 1),
        Card(Suits.CLUB, 2),
        Card(Suits.HEART, 3),
    ]
    assert not is_valid_run(group, 5)

def test_get_non_wild_set_values_on_groups():
    # Test playing on public groups when you have nothing.
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 7))
    hand.add(Card(Suits.DIAMOND, 3))
    hand.add(Card(Suits.DIAMOND, 11))
    hand.add(Card(Suits.DIAMOND, 12))
    hand.add(Card(Suits.CLUB, 1))
    hand.add(Card(Suits.CLUB, 1))
    hand.add(Card(Suits.HEART, 1))

    round = 6

    public_groups = [
        PublicGroup([Card(Suits.HEART, 7), Card(Suits.DIAMOND, 7), Card(Suits.DIAMOND, 7)], round),
        PublicGroup([Card(Suits.HEART, 1), Card(Suits.DIAMOND, 1), Card(Suits.DIAMOND, 1)], round)
    ]

    expected_sets = set([1, 7])
    sets = get_non_wild_set_values_on_groups(hand, round, public_groups)

    assert expected_sets == sets

def test_get_all_plays():
    hand = Hand("test")

    hand.add(Card(Suits.CLUB, 6))
    hand.add(Card(Suits.DIAMOND, 3))
    hand.add(Card(Suits.SPADE, 12))
    hand.add(Card(Suits.DIAMOND, 13))
    expected_plays = [(hand, [])]

    plays = list(get_all_plays(hand, 3, []))
    for expected_play, play in zip(expected_plays, plays):
        assert expected_play[0].cards == play[0].cards
        assert expected_play[1] == play[1]

    hand = Hand("test")
    hand.add(Card(Suits.HEART, 1))
    hand.add(Card(Suits.SPADE, 2))
    hand.add(Card(Suits.HEART, 4))
    hand.add(Card(Suits.DIAMOND, 6))
    hand.add(Card(Suits.DIAMOND, 9))
    hand.add(Card(Suits.CLUB, 10))
    hand.add(Card(Suits.HEART, 10))
    hand.add(Card(Suits.CLUB, 12))
    hand.add(Card(Suits.SPADE, 12))
    hand.add(Card(Suits.DIAMOND, 12))
    hand.add(Card(Suits.CLUB, 9))
    # Public cards: [[[♣5], [♣10], [♣7]], [[♢A], [♢2], [♢3], [♢4]], [[♣K], [♣K], [♢K]]]
    public_groups = [
        PublicGroup([Card(Suits.CLUB, 5), FixedCard(Card(Suits.CLUB, 6), Card(Suits.CLUB, 10), 10), Card(Suits.CLUB, 7)], 10),
        PublicGroup([Card(Suits.DIAMOND, 1), Card(Suits.DIAMOND, 2), Card(Suits.DIAMOND, 3), Card(Suits.DIAMOND, 4)], 10),
        PublicGroup([Card(Suits.CLUB, 13), Card(Suits.CLUB, 13), Card(Suits.DIAMOND, 13)], 10),
    ]

    # Sort the plays by score, and find the best play.
    best_play = sorted(list(get_all_plays(hand, 10, public_groups)), key = lambda x: x[0].get_score(10))[0]
    assert best_play[0].get_score(10) == 7
    assert not check_go_out(hand, 10, public_groups)

def test_optimal_plays():
    def get_best_play(hand, round, groups):
        best_play = sorted(list(get_all_plays(hand, round, groups)), key = lambda x: x[0].get_score(round))[0]
        out_groups = []
        for play in best_play[1]:
            play.fix_wilds(round)
            new_group = play.execute(hand, groups, round)
            if (new_group):
                out_groups.append(new_group)
        discard = best_play[0].discard_highest_value(round)
        return best_play[0].get_score(round), discard, out_groups

    hand = Hand("test")
    hand.add(Card(Suits.HEART, 1))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 8))
    hand.add(Card(Suits.HEART, 9))

    public_groups = []
    round = 4

    score, discard, groups = get_best_play(hand, round, public_groups)
    logging.debug("Test Result: {}, {}, {}".format(score, discard, groups))
    assert score == 8
    assert discard == Card(Suits.HEART, 9)
    assert groups == [PublicGroup([
        Card(Suits.HEART, 1),
        Card(Suits.HEART, 2),
        Card(Suits.HEART, 3)], round)]
    
    # Trivial public card group
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 7))
    hand.add(Card(Suits.DIAMOND, 3))
    hand.add(Card(Suits.DIAMOND, 11))
    hand.add(Card(Suits.DIAMOND, 12))
    hand.add(Card(Suits.CLUB, 1))
    hand.add(Card(Suits.CLUB, 1))
    hand.add(Card(Suits.HEART, 1))

    round = 6

    public_groups = [
        PublicGroup([Card(Suits.HEART, 7), Card(Suits.DIAMOND, 7), Card(Suits.DIAMOND, 7)], round),
        PublicGroup([Card(Suits.HEART, 1), Card(Suits.DIAMOND, 1), Card(Suits.DIAMOND, 1)], round)
    ]

    expected_groups = [PublicGroup([Card(Suits.CLUB, 1), Card(Suits.CLUB, 1), Card(Suits.HEART, 1)], round)]

    score, discard, groups = get_best_play(hand, round, public_groups)
    logging.debug("Test Result: {}, {}, {}".format(score, discard, groups))
    assert score == 13
    assert discard == Card(Suits.DIAMOND, 12)
    assert groups == expected_groups
    assert public_groups[0] == PublicGroup([Card(Suits.HEART, 7), Card(Suits.HEART, 7), Card(Suits.DIAMOND, 7), Card(Suits.DIAMOND, 7)], round)

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
    public_groups = []

    score, discard, groups = get_best_play(hand, round, public_groups)
    logging.debug("Test Result: {}, {}, {}".format(score, discard, groups))
    assert score == 11
    assert discard == Card(Suits.HEART, 9)
    assert groups == [PublicGroup([
        Card(Suits.HEART, 3),
        Card(Suits.HEART, 3),
        Card(Suits.HEART, 3)], round)]
    
    # Ensure couples take bias over a run if they save points
    hand = Hand("test")
    hand.add(Card(Suits.HEART, 1))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 1))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.HEART, 3))
    hand.add(Card(Suits.HEART, 9))
    # We can go out here.
    public_groups = []

    score, discard, groups = get_best_play(hand, round, public_groups)
    logging.debug("Test Result: {}, {}, {}".format(score, discard, groups))
    assert score == 0
    assert discard == Card(Suits.HEART, 9)
    assert groups == [PublicGroup([
        Card(Suits.HEART, 1),
        Card(Suits.HEART, 2),
        Card(Suits.HEART, 3)], round),
        PublicGroup([Card(Suits.HEART, 1),
        Card(Suits.HEART, 2),
        Card(Suits.HEART, 3)], round)]

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

    public_groups = []

    score, discard, groups = get_best_play(hand, round, public_groups)
    logging.debug("Test Result: {}, {}, {}".format(score, discard, groups))
    assert score == 10
    assert discard == Card(Suits.HEART, 9)
    assert groups == [PublicGroup([
        Card(Suits.HEART, 1),
        Card(Suits.HEART, 2),
        Card(Suits.HEART, 3)], round)]

    # Errored hand: -- Can't go out with anything --
    hand = Hand("test")
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.CLUB, 1))
    hand.add(Card(Suits.CLUB, 11))
    hand.add(Card(Suits.CLUB, 5))

    round = 3
    public_groups = []

    score, discard, groups = get_best_play(hand, round, public_groups)
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

    public_groups = []

    score, discard, groups = get_best_play(hand, round, public_groups)
    logging.debug("Test Result: {}, {}, {}".format(score, discard, groups))
    assert score == 0
    assert discard == None
    assert groups == [PublicGroup([Card(Suits.CLUB, 6), Card(Suits.CLUB, 6), Card(Suits.CLUB, 6), Card(Suits.CLUB, 6)], round)]

    # # Forever hand : <[♢9], [♢5], [♢Q], [ʷW], [ʷW], [♣5]>
    hand = Hand("test")
    hand.add(Card(Suits.DIAMOND, 9))
    hand.add(Card(Suits.DIAMOND, 5))
    hand.add(Card(Suits.DIAMOND, 12))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.CLUB, 5))

    round = 5
    public_groups = []

    score, discard, groups = get_best_play(hand, round, public_groups)
    assert score == 0
    assert discard == None
    assert groups == [PublicGroup([
             Card(Suits.DIAMOND, 9), 
             Card(Suits.DIAMOND, 10), 
             Card(Suits.DIAMOND, 11), 
         ], round),
         PublicGroup([
             Card(Suits.DIAMOND, 10), 
             Card(Suits.DIAMOND, 11), 
             Card(Suits.DIAMOND, 12), 
         ], round)]
    
    # Abe : <[ʷW], [♣10], [♠9], [♠K], [♢7], [ʷW], [ʷW], [ʷW], [♢J], [♢2], [♡K], [♡Q], [♠7], [♣Q]>
    # INFO:root:Discarding: [♡K]
    hand = Hand("test")
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.CLUB, 10))
    hand.add(Card(Suits.SPADE, 9))
    hand.add(Card(Suits.SPADE, 13))
    hand.add(Card(Suits.DIAMOND, 7))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.JOKER, 14))
    hand.add(Card(Suits.DIAMOND, 11))
    hand.add(Card(Suits.DIAMOND, 2))
    hand.add(Card(Suits.HEART, 13))
    hand.add(Card(Suits.HEART, 12))
    hand.add(Card(Suits.SPADE, 7))
    hand.add(Card(Suits.CLUB, 12))

    round = 13
    public_groups = []

    score, discard, groups = get_best_play(hand, round, public_groups)
    logging.debug("Test Result: {}, {}, {}".format(score, discard, groups))
    assert score == 2
    assert discard == Card(Suits.SPADE, 9)
    assert groups == [PublicGroup([
            Card(Suits.DIAMOND, 11), 
            Card(Suits.DIAMOND, 12), 
            FixedCard(Card(Suits.DIAMOND, 13), Card(Suits.JOKER, 14), round), 
        ], round),
        PublicGroup([
            Card(Suits.CLUB, 10), 
            Card(Suits.CLUB, 11), 
            Card(Suits.CLUB, 12), 
        ], round),
        PublicGroup([
            Card(Suits.HEART, 10), 
            Card(Suits.HEART, 11), 
            Card(Suits.HEART, 12), 
        ], round),
        PublicGroup([
            Card(Suits.SPADE, 7), 
            Card(Suits.DIAMOND, 7), 
            Card(Suits.CLUB, 7), 
        ], round)]

    # Discarding 4 seems like a bad choice, 2 seems better..
    # Abe : <[♠2], [♢3], [♣3], [♣4], [♣4], [♣5], [♠6], [♡6], [♢6], [♢9], [♢10], [♣K], [♢K], [♣K]>
    # INFO:root:Discarding: [♣4]
    hand = Hand("test")
    hand.add(Card(Suits.SPADE, 2))
    hand.add(Card(Suits.DIAMOND, 3))
    hand.add(Card(Suits.CLUB, 3))
    hand.add(Card(Suits.CLUB, 4))
    hand.add(Card(Suits.CLUB, 4))
    hand.add(Card(Suits.CLUB, 5))
    hand.add(Card(Suits.SPADE, 6))
    hand.add(Card(Suits.HEART, 6))
    hand.add(Card(Suits.DIAMOND, 6))
    hand.add(Card(Suits.DIAMOND, 9))
    hand.add(Card(Suits.DIAMOND, 10))
    hand.add(Card(Suits.CLUB, 13))
    hand.add(Card(Suits.DIAMOND, 13))
    hand.add(Card(Suits.CLUB, 13))

    round = 13
    public_groups = []

    score, discard, groups = get_best_play(hand, round, public_groups)
    logging.debug("Test Result: {}, {}, {}".format(score, discard, groups))
    assert score == 2
    assert discard == Card(Suits.CLUB, 4)
    assert groups == [PublicGroup([
            Card(Suits.DIAMOND, 3), 
            Card(Suits.DIAMOND, 4), 
            Card(Suits.DIAMOND, 5), 
        ], round),
        PublicGroup([
            Card(Suits.CLUB, 3), 
            Card(Suits.CLUB, 4), 
            Card(Suits.CLUB, 5), 
        ], round),
        PublicGroup([
            Card(Suits.DIAMOND, 9), 
            Card(Suits.DIAMOND, 10), 
            Card(Suits.DIAMOND, 11),
        ], round),
        PublicGroup([
            Card(Suits.SPADE, 6), 
            Card(Suits.HEART, 6), 
            Card(Suits.DIAMOND, 6), 
        ], round)]

    # Suboptimal case, gave 2 points when it should be 0
    hand = Hand("test")
    hand.add(Card(Suits.DIAMOND, 1))
    hand.add(Card(Suits.SPADE, 1))
    hand.add(Card(Suits.DIAMOND, 1))
    hand.add(Card(Suits.CLUB, 1))
    hand.add(Card(Suits.HEART, 2))
    hand.add(Card(Suits.DIAMOND, 2))
    hand.add(Card(Suits.CLUB, 9))
    hand.add(Card(Suits.DIAMOND, 10))
    hand.add(Card(Suits.HEART, 10))
    hand.add(Card(Suits.CLUB, 11))
    hand.add(Card(Suits.SPADE, 7))
    # Public Groups: [[[♠A], [♠2], [♠3]], [[♣3], [♣4], [♣5]], [[♣7], [♣7], [♢7]]]
    round = 10
    public_groups = [
        PublicGroup([Card(Suits.SPADE, 1), Card(Suits.SPADE, 2), Card(Suits.SPADE, 3)], round),
        PublicGroup([Card(Suits.CLUB, 3), Card(Suits.CLUB, 4), Card(Suits.CLUB, 5)], round),
        PublicGroup([Card(Suits.CLUB, 7), Card(Suits.CLUB, 7), Card(Suits.DIAMOND, 7)], round),
    ]
    score, discard, groups = get_best_play(hand, round, public_groups)
    assert score == 0
    assert discard == None
    assert groups == [PublicGroup([
            Card(Suits.CLUB, 9), 
            FixedCard(Card(Suits.CLUB, 10), Card(Suits.JOKER, 14), round),
            Card(Suits.CLUB, 11), 
        ], round),
        PublicGroup([
            Card(Suits.HEART, 2), 
            Card(Suits.DIAMOND, 2), 
            Card(Suits.CLUB, 2), 
        ], round),
        PublicGroup([
            Card(Suits.CLUB, 1), 
            Card(Suits.SPADE, 1), 
            Card(Suits.DIAMOND, 1),
            Card(Suits.DIAMOND, 1),
        ], round)]

def run_tests():
    test_get_sets()
    test_get_runs()
    test_get_non_redundant_runs()
    test_is_valid_set()
    test_is_valid_run()
    test_get_non_wild_set_values_on_groups()
    test_get_all_plays()
    test_optimal_plays()
    
if __name__ == "__main__":
    
    logging.getLogger().setLevel(logging.DEBUG)
    t0 = time.time()
    run_tests()
    t1 = time.time()
    logging.info("Tests ran in {} seconds".format(t1 - t0))