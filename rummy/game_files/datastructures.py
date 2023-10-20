"""Data structures"""

import copy
import logging
import random

from enum import Enum
from ordered_enum import OrderedEnum

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


class Suits(OrderedEnum):
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
        self.cards.sort(key=lambda x: x.value)

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
    if input is [3,3,4], return []
    
    if input is [1,1,1,2,4], return [[1,1,1], [1,1,4]]

    Sets are duplicates of the same card including wilds
    """
    
    groups = []
    non_wild_cards = hand.sorted_cards_minus_wilds(round)
    wilds = hand.wilds(round)

    non_wild_cards_copy = copy.deepcopy(non_wild_cards)

    def recurse_until_options_exhausted(ongoing_set, non_wilds, available_wilds, desired_set_len, groups):
        """
        Args:
            ongoing_set(list(Card)): List of cards in the set, (EG, starting would be [4h])
            non_wilds(list(Card)): Non wild cards, immutable
            available_wilds(list(Card)): Wilds that are available for use. Copy and pop off if we consume one while recursing
            desired_set_len
        Return when options exhausted
        """
        # Infinite recursion possibility...
        if len(ongoing_set) == desired_set_len:
            # TODO: Fix bug some other way? If we have [3h, 3h, 3d], we have 3 duplicate groups.
            # Really there should be one. (Combination, not permutation). Going to sort and check if it exists
            # prior to adding..
            ongoing_set.sort(key=lambda x: x.suit)
            if ongoing_set not in groups:
                groups.append(ongoing_set)
            return
        
        # We should never call this with a wild as the starter
        last_non_wild_card = None
        for card in reversed(ongoing_set):
            if not is_wild(card, round):
                last_non_wild_card = card
                break
        if not last_non_wild_card:
            raise Exception("State invalidation, cannot enter with a list of only wilds")
        
        # 6h 0 back means we need any 6.
        needed_card_value = last_non_wild_card.value
        found_card = None
        for card in non_wilds:
            if card.value == needed_card_value:
                found_card = card
                break

        if found_card:
            # We do have to remove this card from the available cards in this equation...
            temp_run = copy.deepcopy(ongoing_set)
            temp_run.append(found_card)
            non_wilds_copy = copy.deepcopy(non_wilds)
            non_wilds_copy.remove(found_card)
            recurse_until_options_exhausted(temp_run, non_wilds_copy, available_wilds, desired_set_len, groups)
        if len(available_wilds) > 0:
            temp_run = copy.deepcopy(ongoing_set)
            temp_available_wilds = copy.deepcopy(available_wilds)
            # Pop is from the back, but it doesn't matter..
            temp_run.append(temp_available_wilds.pop())
            recurse_until_options_exhausted(temp_run, non_wilds, temp_available_wilds, desired_set_len, groups)
        return


    # For round 3 (4 cards with discard) loop once...
    for set_length in range(3, len(hand.cards)):
        # Use each card as a starter to see if it can make a len 3 run.
        # Yes, this will include duplicates if we have 2 [3h],
        # TODO: Could optimize (but think it's okay)
        for starting_card in non_wild_cards_copy:

            starting_set_group = [starting_card]
            non_wild_cards_copy_copy = copy.deepcopy(non_wild_cards_copy)
            non_wild_cards_copy_copy.remove(starting_card)
            # Safe to pass wilds, it will copy before we remove..
            recurse_until_options_exhausted(starting_set_group, non_wild_cards_copy_copy, wilds, set_length, groups)
            
    return groups


def get_all_runs(hand, round):
    """
    if input is [3h,3d,4h], return [[3h,4h],[3d]]
    Runs are incrementing values of the same suit (excluding wilds)
    """
    
    groups = []
    non_wild_cards = hand.sorted_cards_minus_wilds(round)
    wilds = hand.wilds(round)

    non_wild_cards_copy = copy.deepcopy(non_wild_cards)

    def recurse_until_options_exhausted(ongoing_run, non_wilds, available_wilds, desired_run_len, groups):
        """
        Args:
            ongoing_run(list(Card)): List of cards in the run, (EG, starting would be [4h])
            non_wilds(list(Card)): Non wild cards, immutable
            available_wilds(list(Card)): Wilds that are available for use. Copy and pop off if we consume one while recursing
            desired_run_len
        Return when options exhausted
        """
        # Infinite recursion possibility...
        if len(ongoing_run) == desired_run_len:
            groups.append(ongoing_run)
            return
        
        # We should never call this with a wild as the starter
        last_non_wild_card = None
        last_non_wild_cards_back = 0
        for i, card in enumerate(reversed(ongoing_run)):
            if not is_wild(card, round):
                last_non_wild_card = card
                last_non_wild_cards_back = i
                break
        if not last_non_wild_card:
            raise Exception("State invalidation, cannot enter with a list of only wilds")
        
        # 6h 0 back means we need 7h. 6h 1 back means we need 8h.
        needed_card = Card(last_non_wild_card.suit, last_non_wild_card.value + last_non_wild_cards_back + 1)
        found_card = False
        for card in non_wilds:
            if card == needed_card:
                found_card = True
                break

        if found_card:
            temp_run = copy.deepcopy(ongoing_run)
            temp_run.append(needed_card)
            recurse_until_options_exhausted(temp_run, non_wilds, available_wilds, desired_run_len, groups)
        if len(available_wilds) > 0:
            temp_run = copy.deepcopy(ongoing_run)
            temp_available_wilds = copy.deepcopy(available_wilds)
            # Pop is from the back, but it doesn't matter..
            temp_run.append(temp_available_wilds.pop())
            recurse_until_options_exhausted(temp_run, non_wilds, temp_available_wilds, desired_run_len, groups)
        return


    # For round 3 (4 cards with discard) loop once...
    for run_length in range(3, len(hand.cards)):
        # Use each card as a starter to see if it can make a len 3 run.
        # Yes, this will include duplicates if we have 2 [3h],
        # TODO: Could optimize (but think it's okay)
        for starting_card in non_wild_cards_copy:

            starting_run_group = [starting_card]
            # Safe to pass wilds, it will copy before we remove..
            recurse_until_options_exhausted(starting_run_group, non_wild_cards, wilds, run_length, groups)
            
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
        discard(Card): popped off the hand
        Groups(List(List(Card))): List of list of cards we would go out with (if this were the round to go out)
    """
    if not existing_groups:
        existing_groups = list()
    assert len(hand.cards) > 2 and len(hand.cards) < 14
    round = len(hand.cards) - 1
    hand.sort()

    non_wild_cards = hand.sorted_cards_minus_wilds(round)
    num_wilds = len(hand.cards) - len(non_wild_cards)
    logging.debug("Getting all runs")
    runs = get_all_runs(hand, round)
    logging.debug("Getting all sets")
    sets = get_all_sets(hand, round)
    
    logging.debug("Getting Starting check_go_out. Run options: {}, Set options: {}".format(len(runs), len(sets)))
    logging.debug(runs)
    logging.debug(sets)
    combined_groups = runs + sets

    # if runs are [a,b,c] and sets are [1,2], iterate assuming something over 3 is a set.
    group_permutation_order = list(permutations(range(len(runs) + len(sets))))

    # Other strategy:
    # Loop through each <runs> and <sets> with a wild count. Try to string them together in every
    # possible combination to get the lowest sum value.
    # Could bias to start with higher combinations of cards and all that, or could brute force..
    # Really we should consider everything, so may as well brute force.

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

    # TODO: Optimize to return early if we get something with a 0 score...
    # TODO: Ignore the case where you could discard a wild to get -15...
    
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
            # is_run_group = bool(order[group_index] < len(runs))

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
        
        # Sort by value of card, and return the one with the highest value...?
        # hand_copy.sort()  # last card should be highest?
        hand_copy.sort(key=lambda x: CARD_POINT_MAP[CARD_TEXT_MAP[x.value]])
        discard = hand_copy[len(hand_copy) - 1]

        # State invalidation.
        # logging.debug("INVALID: hand_copy: {},  discard: {}".format(hand_copy, discard))
        # It's viable to discard a wild IFF you are going out
        if len(hand_copy) > 1:
            assert not is_wild(discard, round)

        hand_copy.remove(discard)
        for card in hand_copy:
            scenario_score += get_card_score(card, round)

        outage_scenarios.append((scenario_selection_groups, discard, hand_copy, scenario_score))

    # On looking closer... I think I can keep this same model, I just need to add all wild cards to the combinations...
    logging.debug("Total cycles: {}".format(total_cycles))

    # Sort by the lowest value...
    outage_scenarios.sort(key = lambda x: x[3]) 
    # print(" -- Best scenario, given hand: ")
    # for card in non_wild_cards:
    #     print(card)
    # print("-- Is:")
    # for group in outage_scenarios[0][0]:
    #     print(" - Group: ")
    #     for card in group:
    #         print(card)
    # print(" - Discard: {}".format(outage_scenarios[0][1]))
    # print(" - Score: {}".format(outage_scenarios[0][3]))

    # Greedy strategy, just discard the highest card that isn't in a run.
    # list(tuple(scenario_selection_group, discard, other_cards, score))
    """
        Returns:
        score(int): Implied to be 0, -5, or -15 based on the existence of existing_groups.
        discard(Card): popped off the hand
        Groups(List(List(Card))): List of list of cards we would go out with (if this were the round to go out)
    """
    chosen_scenario = outage_scenarios[0]
    hand.remove(chosen_scenario[1])

    return chosen_scenario[3], chosen_scenario[1], chosen_scenario[0]

    # Card discard strategy, return the highest card with the least combinations

    # Add a <play off others> mechanic after.