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
        logging.info("Cards in deck: {}".format(len(self.cards)))

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
    

class Group:
    cards = None
    # These cards are not ours.
    public_group = None

    def __init__(self, public_group=None):
        """
        Args:
            public_group(List(Card)): Existing group to play off which isn't ours.
                                      EG, [1h,2h,3h]
        """
        if not public_group:
            self.public_group = []
        else:
            self.public_group = public_group
        
        self.cards = public_group
    
    def append(self, card):
        self.cards.append(card)


class PublicGroup:
    total_group = None
    fixed_cards = None
    private_cards = None
    
    def __init__(self, total_group, fixed_cards):
        """
        ([1h,2h*,3h*,4h*] -> [1h,2h*,3h*,4h*])
        Args:
            total_group(list(Card)): List of cards in the group, including addons.
            fixed_cards(list(Card)): List of cards in the public group, excluding addons.
        """
        self.total_group = total_group
        self.fixed_cards = fixed_cards
        self.private_cards = copy.deepcopy(total_group)
        for card in fixed_cards:
            self.private_cards.remove(card)

    def __str__(self):
        return "<{}> -> <{}>".format(self.fixed_cards, self.total_group)
    
    def __repr__(self):
        return "<{}> -> <{}>".format(self.fixed_cards, self.total_group)
    
    def __eq__(self, other):
        if isinstance(other, PublicGroup):
            return self.total_group == other.total_group and self.fixed_cards == other.fixed_cards
        return False
    

    
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

def is_valid_run(group, round):
    """
    Check if this group is a valid run.
    Assumes the cards are sorted..
    """
    last_non_wild_idx = -1
    for idx, card in enumerate(group):
        if not is_wild(card, round):
            if last_non_wild_idx >= 0:
                last_card = group[last_non_wild_idx]
                if last_card.suit != card.suit or (last_card.value + idx - last_non_wild_idx) != card.value:
                    return False
            last_non_wild_idx = idx
    return True
    
def is_valid_set(group, round):
    """
    Check if this group is a valid set.
    """
    # If all cards are wild, it technically is a valid run..
    # [3h, w, 5h]  0, 2
    last_non_wild_idx = -1
    for idx, card in enumerate(group):
        if not is_wild(card, round):
            if last_non_wild_idx >= 0:
                last_card = group[last_non_wild_idx]
                if last_card.value != card.value:
                    return False
            last_non_wild_idx = idx
    return True

def get_all_sets(hand, round, existing_sets=None):
    """
    if input is [3,3,4], return []
    
    if input is [1,1,1,2,4], return [[1,1,1], [1,1,4]]

    Sets are duplicates of the same card including wilds
    """
    if not existing_sets:
        existing_sets = []
    
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

    def recurse_existing_set_extensions(ongoing_set, non_wilds, length, public_groups, public_group_ref):
        """
        Args:
            ongoing_set(list(Card)): List of cards in the run, (EG, starting would be [4h])
            non_wilds(list(Card)): Non wild cards, immutable
            desired_run_len
        Return when options exhausted
        """
        
        # Base case where we add
        # ASSUMED TO NOT START WITH 0,
        if length == 0:
            # I have something wrong here -- given that I can generate the same thing more than once.
            # For the time being though, just going to ignore it, as long as this function is quick.
            
            # Sort the cards we added, just so we don't add duplicates
            i = len(public_group_ref)
            j = len(ongoing_set)
            ongoing_set[i:j] = sorted(ongoing_set[i:j], key=lambda x: x.suit)
            public_group = PublicGroup(ongoing_set, public_group_ref)
            if public_group not in public_groups:
                public_groups.append(PublicGroup(ongoing_set, public_group_ref))
            return
            
        if length > 0:
            # Don't use wilds, it doesn't make sense
            first_non_wild = None

            for card in ongoing_set:
                if not is_wild(card, round):
                    first_non_wild = card
                    break
            
            if not first_non_wild:
                raise AssertionError("Should not be possible to have a set of all wilds {}".format(ongoing_set))

            needed_card_number = first_non_wild.value
            cards_that_work = []

            for card in non_wilds:
                if card.value == needed_card_number:
                    cards_that_work.append(card)
            
            logging.debug("length: {}, public_group_ref: {}, ongoing_set: {}, cards_that_work: {}".format(
                length, public_group_ref, ongoing_set, cards_that_work
            ))
            for card in cards_that_work:
                ongoing_set_copy = copy.deepcopy(ongoing_set)
                ongoing_set_copy.append(card)
                non_wilds_copy = copy.deepcopy(non_wilds)
                non_wilds_copy.remove(card)
                # Don't actually have to remove the card, because we won't be looking for it again.
                recurse_existing_set_extensions(
                    ongoing_set_copy,
                    non_wilds_copy,
                    length - 1,
                    public_groups,
                    public_group_ref)


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

    # list of PublicGroup's (Extensions of existing runs)
    # [ ([1h,2h*,3h*,4h*] -> [2h*,3h*,4h*]), ... ]
    public_groups = []

    # Logically there is no reason to put down a card on an existing set if you have 3 of them.
    # Only look through adding 1 or 2 cards to an existing set as a result..
    for existing_set in existing_sets:
        for additions in range(1, 3):
            non_wild_cards_copy_copy = copy.deepcopy(non_wild_cards)
            
            recurse_existing_set_extensions(
                existing_set,
                non_wild_cards_copy_copy,
                additions,
                public_groups,
                existing_set)
            
    return groups, public_groups
    

def get_all_runs(hand, round, existing_runs=None):
    """
    Runs are incrementing values of the same suit (excluding wilds)

    Could return:
        all_my_runs = [[1h,2h,3h],[...]]
        public_runs = [ ([1h,2h*,3h*,4h*] -> [2h*,3h*,4h*]), ... ]
    """
    if not existing_runs:
        existing_runs = []
    
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
    
        # existing_run, non_wild_cards_copy_copy, wilds, left_length, right_length, public_groups
    def recurse_existing_run_extensions(ongoing_run, non_wilds, available_wilds, left_length, right_length, public_groups, public_group_ref):
        """
        Args:
            ongoing_run(list(Card)): List of cards in the run, (EG, starting would be [4h])
            non_wilds(list(Card)): Non wild cards, immutable
            available_wilds(list(Card)): Wilds that are available for use. Copy and pop off if we consume one while recursing
            desired_run_len
        Return when options exhausted
        """
        
        # Base case where we add -- IFF left_length == 0 and right_length == 0
        # ASSUMED TO NOT START WITH 0,0
        if left_length == 0 and right_length == 0:
            # I have something wrong here -- given that I can generate the same thing more than once.
            # For the time being though, just going to ignore it, as long as this function is quick.
            public_group = PublicGroup(ongoing_run, public_group_ref)
            if public_group not in public_groups:
                public_groups.append(PublicGroup(ongoing_run, public_group_ref))
            return
            
        if left_length > 0:
            # Try to add a card to the left

            # Don't use wilds at the end, it doesn't make sense
            exclude_wilds = bool(left_length == 1)

            index_of_first_non_wild = -1
            first_non_wild = None

            for idx, card in enumerate(ongoing_run):
                if not is_wild(card, round):
                    index_of_first_non_wild = idx
                    first_non_wild = card
                    break
            
            if not first_non_wild:
                raise AssertionError("Should not be possible to have a run of all wilds, those are considered sets. {}".format(ongoing_run))

            needed_card = Card(first_non_wild.suit, first_non_wild.value - (1 + index_of_first_non_wild))

            card_exists = False
            for card in non_wilds:
                if card == needed_card:
                    card_exists = True
                    break
            
            if card_exists:
                ongoing_run_copy = copy.deepcopy(ongoing_run)
                ongoing_run_copy.insert(0, needed_card)
                # Don't actually have to remove the card, because we won't be looking for it again.
                recurse_existing_run_extensions(
                    ongoing_run_copy,
                    non_wilds,
                    available_wilds,
                    left_length - 1,
                    right_length,
                    public_groups,
                    public_group_ref)

            if not exclude_wilds and len(available_wilds) > 0:
                ongoing_run_copy = copy.deepcopy(ongoing_run)
                temp_available_wilds = copy.deepcopy(available_wilds)
                ongoing_run_copy.insert(0, temp_available_wilds.pop())
                recurse_existing_run_extensions(
                    ongoing_run_copy,
                    non_wilds,
                    temp_available_wilds,
                    left_length - 1,
                    right_length,
                    public_groups,
                    public_group_ref)
                
        if right_length > 0:
            # Try to add a card to the right

            # Don't use wilds at the end, it doesn't make sense
            exclude_wilds = bool(right_length == 1)

            index_of_first_non_wild = -1
            first_non_wild = None

            for idx, card in enumerate(reversed(ongoing_run)):
                if not is_wild(card, round):
                    index_of_first_non_wild = idx
                    first_non_wild = card
                    break
            
            if not first_non_wild:
                raise AssertionError("Should not be possible to have a run of all wilds, those are considered sets. {}".format(ongoing_run))

            needed_card = Card(first_non_wild.suit, first_non_wild.value + (1 + index_of_first_non_wild))

            card_exists = False
            for card in non_wilds:
                if card == needed_card:
                    card_exists = True
                    break
            if card_exists:
                ongoing_run_copy = copy.deepcopy(ongoing_run)
                ongoing_run_copy.append(needed_card)
                # Don't actually have to remove the card, because we won't be looking for it again.
                recurse_existing_run_extensions(
                    ongoing_run_copy,
                    non_wilds,
                    available_wilds,
                    left_length,
                    right_length - 1,
                    public_groups,
                    public_group_ref)

            if not exclude_wilds and len(available_wilds) > 0:
                ongoing_run_copy = copy.deepcopy(ongoing_run)
                temp_available_wilds = copy.deepcopy(available_wilds)
                ongoing_run_copy.append(temp_available_wilds.pop())
                recurse_existing_run_extensions(
                    ongoing_run_copy,
                    non_wilds,
                    temp_available_wilds,
                    left_length,
                    right_length - 1,
                    public_groups,
                    public_group_ref)


    # For round 3 (4 cards with discard) loop once...
    for run_length in range(3, len(hand.cards)):
        # Use each card as a starter to see if it can make a len 3 run.
        # Yes, this will include duplicates if we have 2 [3h],
        # TODO: Could optimize (but think it's okay)
        for starting_card in non_wild_cards_copy:

            starting_run_group = [starting_card]
            # Safe to pass wilds, it will copy before we remove..
            recurse_until_options_exhausted(starting_run_group, non_wild_cards, wilds, run_length, groups)

    # list of PublicGroup's (Extensions of existing runs)
    # [ ([1h,2h*,3h*,4h*] -> [2h*,3h*,4h*]), ... ]
    public_groups = []

    # Logically there is no reason to put down a card on an existing set if you have 3 of them.
    # Only look through adding 1 or 2 cards to an existing set as a result..
    for existing_run in existing_runs:
        for left_length in range(0,3):
            for right_length in range(0,3):
                if left_length == 0 and right_length == 0:
                    continue
        
                non_wild_cards_copy_copy = copy.deepcopy(non_wild_cards)
                
                recurse_existing_run_extensions(
                    existing_run,
                    non_wild_cards_copy_copy,
                    wilds,
                    left_length,
                    right_length,
                    public_groups,
                    existing_run)

    return groups, public_groups


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

def recursive_scenario_solve(group_order_so_far, remaining_cards, groups_left, groups_reference, truncated_groups, global_loop_count):
    """
    Probably want to evaluate before pushing whether the selected next index works..
    That way the caller can decide to push itself as <end of a tree>
    
    Args:
        group_order_so_far(list(idx)): List of indexes selected in this path (relative to the groups_reference)
        remaining_cards(list(Card)): List of cards left in the hand
        groups_left(list(idx)): List of indexes left unselected in this path (relative to the groups_reference)
        groups_reference(list(list(Card))): List of all groups (which you can use an idx to lookup)
        truncated_groups(list(list(idx))): Append the order of selected groups so far when no other group can work.
        global_loop_count(list(int)): Incrementing int to see how deep each scenario goes. Used for optimizing.
    """
    # Should it add each time a group doesn't work..? or just if nothing works?
    # If it was [1,2,3,4], and we were at [1] with [2,3,4] left, 
    # at [1]->[2] [3,4] we would at least want to consider the [3,4] as next steps, or each would add [1]..
    global_loop_count[0] += 1
    viable_next_indexes = []
    for group_idx in groups_left:
        group = groups_reference[group_idx]

        group_cards = []

        # If this group is >= remaining_cards, that means we ignore it. Have to have a discard.
        if isinstance(group, PublicGroup):
            group_length = len(group.private_cards)
            group_cards = group.private_cards
        else:
            group_length = len(group)
            group_cards = group

        if group_length >= len(remaining_cards):
            continue

        # Check to see if all cards are possible to remove, if they are, continue with this as viable.
        remaining_cards_copy = copy.deepcopy(remaining_cards)
        all_cards_work = True

        
        for card in group_cards:
            if card in remaining_cards_copy:
                remaining_cards_copy.remove(card)
            else:
                all_cards_work = False
                break
        if all_cards_work:
            viable_next_indexes.append(group_idx)
            group_order_so_far_copy = copy.deepcopy(group_order_so_far)
            # groups_left_copy = copy.deepcopy(groups_left)
            group_order_so_far_copy.append(group_idx)
            # groups_left_copy.remove(group_idx)

            recursive_scenario_solve(
                group_order_so_far_copy,
                remaining_cards_copy,
                # groups_left_copy,
                groups_left[1:],
                groups_reference,
                truncated_groups,
                global_loop_count)
    
    # If no scenarios were viable to continue with, this is the end of a tree.
    if not viable_next_indexes:
        if group_order_so_far not in truncated_groups:
            truncated_groups.append(group_order_so_far)
        
        # truncated_groups.append(group_order_so_far)

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
        card_groups(list(list(Card))): List of card groups we would go out with (if we were going out first)
        public_card_groups(list(PublicGroup)): List of PublicGroups we modified to go out
    """
    if not existing_groups:
        existing_groups = list()
    assert len(hand.cards) > 2 and len(hand.cards) < 15
    round = len(hand.cards) - 1
    hand.sort()

    existing_sets = []
    existing_runs = []
    for existing_group in existing_groups:
        is_set = is_valid_set(existing_group, round)
        is_run = is_valid_run(existing_group, round)
        if is_set and is_run or is_run:
            existing_sets.append(existing_group)
            continue
        if is_set:
            existing_sets.append(existing_group)
            continue
        raise AssertionError("Exising group is not valid: {}".format(existing_group))
    
    logging.debug("Existing sets: {}, Existing runs: {}".format(len(existing_sets), len(existing_runs)))

    logging.debug("Getting all runs")
    runs, public_runs = get_all_runs(hand, round, existing_runs)
    logging.debug("Getting all sets")
    sets, public_sets = get_all_sets(hand, round, existing_sets)
    
    logging.debug("Getting Starting check_go_out. Run options: {}, Set options: {}".format(len(runs), len(sets)))
    logging.debug("Public Run options: {}, Public Set options: {}".format(len(public_runs), len(public_sets)))
    # logging.debug(runs)
    # logging.debug(sets)
    groups = runs + sets
    public_groups = public_runs + public_sets
    combined_groups = groups + public_groups

    
    # TODO: Get good at python...
    combined_group_indexes = []
    for idx, _ in enumerate(combined_groups):
        combined_group_indexes.append(idx)

    # List(list(idx)): List of "groups" where each value in a group is an index ref to groups
    truncated_groups = []

    # Starter loop, we try each one as the starter..
    global_loop_count = [0]
    for idx, group in enumerate(combined_groups):
        # Should be impossible to have one of the starter groups not fit. Blind add them.
        group_order_so_far = [idx]
        cards_copy = copy.deepcopy(hand.cards)

        # Should be impossible to have a group that doesn't work, blindly remove.
        if isinstance(group, PublicGroup):
            for card in group.private_cards:   
                cards_copy.remove(card)
        else:
            for card in group:
                cards_copy.remove(card)
        
        groups_left = copy.deepcopy(combined_group_indexes)
        groups_left.remove(idx)

        recursive_scenario_solve(
                group_order_so_far,
                cards_copy,
                # groups_left,
                combined_group_indexes[1:],
                combined_groups,
                truncated_groups,
                global_loop_count)
        
    
    logging.info("Done with recursive_scenario_solve. Total cycles: {}, truncated_groups lenth: {}".format(
        global_loop_count, len(truncated_groups)))
        
    # Output result here is a list of viable orders


    # list(tuple(scenario_selection_group, discard, other_cards, score))
    outage_scenarios = []
    first_to_go_out = len(existing_groups) == 0

    # Loop through each, select a discard, and calculate a score
    # truncated_groups = list(list(group_indexes)) // group indexes in a scenario that reached the end.
    for truncated_group in truncated_groups:
        private_card_groups = []
        public_card_groups = []

        for group_index in truncated_group:
            group = combined_groups[group_index]
            if isinstance(group, PublicGroup):
                public_card_groups.append(group)
            else:
                private_card_groups.append(group)
        
        cards_copy = copy.deepcopy(hand.cards)
        for group in private_card_groups:
            for card in group:
                cards_copy.remove(card)
        for group in public_card_groups:
            for card in group.private_cards:
                cards_copy.remove(card)
        
        
        assert len(cards_copy) >= 1
        cards_copy.sort(key=lambda x: get_card_score(x, round))
        discard = cards_copy[len(cards_copy) - 1]
        
        # State invalidation.
        # It's viable to discard a wild IFF you are going out
        # if len(cards_copy) > 1:
        #     assert not is_wild(discard, round)        
        cards_copy.remove(discard)

        scenario_score = 0
        for card in cards_copy:
            scenario_score += get_card_score(card, round)

        if first_to_go_out and scenario_score == 0:
            # First to go out gets -5
            scenario_score -= 5
            if len(hand.wilds(round)) == 0:
                # If you go out first naturally, you get an additional -10
                scenario_score -= 10

        outage_scenarios.append((private_card_groups, discard, cards_copy, scenario_score, public_card_groups))

    # If there are no outage scenarios, we have jack shit... Make one with no groups
    if len(outage_scenarios) == 0:
        card_groups = []
        cards_copy = copy.deepcopy(hand.cards)
        assert len(cards_copy) >= 1
        cards_copy.sort(key=lambda x: CARD_POINT_MAP[CARD_TEXT_MAP[x.value]])
        discard = cards_copy[len(cards_copy) - 1]
        
        # State invalidation.
        # It's viable to discard a wild IFF you are going out
        if len(cards_copy) > 1:
            assert not is_wild(discard, round)
        
        cards_copy.remove(discard)

        scenario_score = 0
        for card in cards_copy:
            scenario_score += get_card_score(card, round)

        outage_scenarios.append((card_groups, discard, cards_copy, scenario_score, []))

    # Sort by the lowest value...
    outage_scenarios.sort(key = lambda x: x[3]) 

    # Greedy strategy, just discard the highest card that isn't in a run.
    chosen_scenario = outage_scenarios[0]
    hand.remove(chosen_scenario[1])

    return chosen_scenario[3], chosen_scenario[1], chosen_scenario[0], chosen_scenario[4]

    # Card discard strategy, return the highest card with the least combinations

    # Add a <play off others> mechanic after.
    """
    Just take sets / runs from the table, find some way to mark them as "not mine"
    put them into the sets function and runs function. Then when subtracting,
    just don't subtract those cards from my hand.
    """