"""Data structures"""

import copy
import logging
import random

from enum import Enum
from itertools import permutations


logging.basicConfig(level=logging.DEBUG)

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
    
    def __lt__(self, other):
        return self.value < other.value
    
    def __sub__(self, other):
        return self.value - other.value
    
    def __str__(self):
        return "[{}{}]".format(SUIT_TEXT_MAP[self.suit.value], CARD_TEXT_MAP[self.value])
    
    def __repr__(self):
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
        # TODO: Might have to make a secondary sort on the suit... 
        # Also I shouldn't have done reverse...
        self.cards.sort(key=lambda x: x.value, reverse=True)

    def sorted_cards_minus_wilds(self, round):
        """
        Return a temporary list of all the cards ignoring wilds.
        """
        # Should make sure we do insertion sort or something to avoid this.
        self.sort()
        cards = []
        for card in self.cards:
            if not is_wild(card, round):
                cards.append(card)

        return cards
    
    def wilds(self, round):
        # Should make sure we do insertion sort or something to avoid this.
        wilds = []
        for card in self.cards:
            if is_wild(card, round):
                wilds.append(card)

        return wilds


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

    
def get_card_score(card, round):
    if is_wild(card, round):
        return 0
    return CARD_POINT_MAP[CARD_TEXT_MAP[card.value]]
    

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
    
def get_all_sets(hand, round):
    """
    if input is [3,3,4], return [[3,3],[4]]

    if input is [1,1,2,4], return [[1,1], [1,1,4], [2], [2,4]]

    Sets are duplicates of the same card (excluding wilds).
    """
    def make_set_group(c, i):
        g = []
        while i < len(c) and c[i].value == c[i - 1].value:
            g.append(c[i - 1])
            i += 1
        g.append(c[i - 1])
        return i, g
    
    index = 1
    groups = []
    cards = hand.sorted_cards_minus_wilds(round)
    # Doing this because the inner loop has a break out, and that's how we add the last card.
    while index <= len(cards):
        index, group = make_set_group(cards, index)
        groups.append(group)
        index += 1

    # Go back and add wilds.. 
    # [[1,1], [2]]
    # [[1,1], [2], [1,1,4], [2,4]]
    # [[1,1], [2], [1,1,4], [2,4], [1,1,4,4], [2,4,4]]

    # TODO: If i'm incorporating wilds here, I really shouldn't do groups that are less than 3 in size...
    # If I play on 
  
    wilds = hand.wilds(round)
    non_wilds_group_copy = copy.deepcopy(groups)

    for idx, wild in enumerate(wilds):
        groups_copy = copy.deepcopy(non_wilds_group_copy)
        for group in groups_copy:
            group.append(wild)
            # Need to add additional wilds as combinations. Don't need permutation though.
            for i in range(0, idx):
                group.append(wilds[i])
            groups.append(group)

    return groups


def get_all_runs(hand, round):
    """
    if input is [3h,3d,4h], return [[3h,4h],[3d]]
    Runs are incrementing values of the same suit (excluding wilds)
    """

    # TODO: I gotta fix this actually... this should return differently.
    # If it is [3h, 4h, 5h, 6h], options should be:
    # [3h, 4h, 5h], [4h, 5h, 6h], [3h, 4h, 5h, 6h].. 
    def make_run(c):
        g = []
        current_card = c[0]
        g.append(current_card)

        i = 1
        while i < len(c):
            # If it's the same card, skip 
            if current_card.value == c[i].value:
                i += 1
                continue
            
            # If the card is in a run, add it.
            if current_card.suit == c[i].suit and current_card.value == c[i].value + 1:
                g.append(c[i])
                current_card = c[i]
                i += 1
                continue

            # Early break clause, if the value is two higher...
            if current_card.value < c[i].value + 1:
                break

            # Base case? We just increment and continue?
            i += 1
        return g
    
    groups = []
    cards = hand.sorted_cards_minus_wilds(round)
    
    # Need a copy of <cards left> and we iterate through with the first each time, 
    # Try to find something that follows this card, then follows the next card, then add them
    # as a contiguous set -- removing them from the cards...
    while len(cards) > 0:
        group = make_run(cards)
        groups.append(group)

        # Brute force, should make this more efficient.
        for c in group:
            cards.remove(c)

    # TODO: I gotta figure out how to do wilds as well
    # If it is [4h, 5h, 7h, 8h, W], options should be:
    # [W, 4h, 5h], [4h, 5h, W], [W, 7h, 8h], [7h, 8h, W]
    # [5h, W, 7h]
    # [4h, 5h, W, 7h], [5h, W, 7h, 8h]
    # [4h, 5h, W, 7h, 8h]

    wilds = hand.wilds(round)
    non_wilds_group_copy = copy.deepcopy(groups)

    return groups


def get_natural_outage_possibilities(round):
    assert round > 2 and round < 14

    def find_combinations(target, min_group):
        if target == 0:
            return [[]]
        if target < 0:
            return []
        combinations = []
        for i in range(min_group, target + 1):
            sub_combinations = find_combinations(target - i, i)
            combinations.extend([[i] + combo for combo in sub_combinations])
        return combinations

    return find_combinations(round, 3)
    

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
    assert len(hand.cards) > 2 and len(hand.cards) < 14
    round = len(hand.cards) - 1
    hand.sort()

    non_wild_cards = hand.sorted_cards_minus_wilds(round)
    num_wilds = len(hand.cards) - len(non_wild_cards)
    runs = get_all_runs(hand, round)
    sets = get_all_sets(hand, round)
    combined_groups = runs + sets

    # if runs are [a,b,c] and sets are [1,2], iterate assuming something over 3 is a set.
    group_permutation_order = list(permutations(range(len(runs) + len(sets))))

    # Other strategy:
    # Loop through each <runs> and <sets> with a wild count. Try to string them together in every
    # possible combination to get the lowest sum value.
    # Could bias to start with higher combinations of cards and all that, or could brute force..
    # Really we should consider everything, so may as well brute force.

    

    for wild_count in range(0, num_wilds):
        print("solve with a wild")
        # Solve with a wild.

    # Solve without wilds

    """
    x: [1,2]
    y: [a,b,c]

    for iy in range(len(y))
        for ix in range(len(x))
            loop through each combination, starting with x[0] going x+ first, then y+,
            Then do y[0] first, going x+ then y+

    outcome list:
     - [1,2,a,b,c]
     - [1,a,b,c,2]...

     No, just get a all unique combinations of x and y and run them...
    
     -- 
     Do a greedy alg to use wild count to chain together?
    """

    # list(tuple(scenario_selection_group, discard, other_cards, score))
    outage_scenarios = []

    
    logging.debug('group permutation order length: {}'.format(len(group_permutation_order)))
    total_cycles = 0
    for order in group_permutation_order:

        group_index = 0
        scenario_selection_groups = []
        scenario_score = 0
        hand_copy = hand.cards.copy()

        # a "group", aka combined_groups[order[group_index]] will be a list of dards that are either a run, or a set..
        # EG, [3h,4h,5h] or [3h,3d,3h]
        while group_index < len(order):
            total_cycles += 1

            # Get the group, regardless of type
            group = combined_groups[order[group_index]]
            is_run_group = bool(order[group_index] < len(runs))

            # Base base case... If the hand is empty, we have removed all the cards!
            if len(hand_copy) < 1:
                break

            # Base case, no wilds, continue if length doesn't fit.
            if len(group) < 3:  # Should probably do something other than hardcoded 3...
                group_index += 1
                continue

            # If here, implicitly it is 3 in a row. 
            # Ensure all cards here are available, otherwise skip to the next
            
            # We will try to remove before we actually remove... If we can't this group doesn't work
            temp_hand_copy = hand_copy.copy()
            all_good = True
            for card in group:
                if card not in temp_hand_copy:
                    all_good = False
                    break
                temp_hand_copy.remove(card)
            
            if not all_good:
                group_index +=1
                continue

            # We are good, add this as a group, and remove the cards from play
            scenario_selection_groups.append(group)
            hand_copy = temp_hand_copy
            group_index +=1

        # We have effectively consumed all the cards in this order, or we have gone out.
        # Add up the score and record this outcome.
        # Implicitly anything in a group is zero points, just have to count the extra cards
        
        hand_copy.sort()  # last card should be highest?
        discard = hand_copy[len(hand_copy) - 1]

        # State invalidation.
        assert not is_wild(discard, round)

        hand_copy.remove(discard)
        for card in hand_copy:
            scenario_score += get_card_score(card, round)

        outage_scenarios.append((scenario_selection_groups, discard, hand_copy, scenario_score))

    # On looking closer... I think I can keep this same model, I just need to add all wild cards to the combinations...
    logging.debug("Total cycles: {}".format(total_cycles))

    # Sort by the lowest value...
    outage_scenarios.sort(key = lambda x: x[3]) 
    print(" -- Best scenario, given hand: ")
    for card in non_wild_cards:
        print(card)
    print("-- Is:")
    for group in outage_scenarios[0][0]:
        print(" - Group: ")
        for card in group:
            print(card)
    print(" - Discard: {}".format(outage_scenarios[0][1]))
    print(" - Score: {}".format(outage_scenarios[0][3]))


    # One strategy:
    #  - Create all possible card combinations, based on sorted card order...
    #    EG: [0,1,2] for a hand of 3's, or for 6's: [[0,1,2],[3,4,5]], [[0,2,5],[2,3,4]]
    #  - Then loop throughand pick the one that has the lowest score.
    #     -- Note that jokers screw up the sort, so have to do any order... that could get too big
    

    # First priority should be to go out naturally, optimize for that..
    # natural_outage_possibilities = get_natural_outage_possibilities(round)

    # Card discard strategy, return the highest card with the least combinations

    # Add a <play off others> mechanic after.