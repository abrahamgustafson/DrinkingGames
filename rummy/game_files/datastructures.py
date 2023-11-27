"""Data structures"""

import copy
import logging
import random

from itertools import groupby, combinations
from ordered_enum import OrderedEnum
from functools import reduce

logging.basicConfig(level=logging.DEBUG)

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
    0: '♣',
    1: '♠',
    2: '♥',
    3: '♦',
    4: 'ʷ'
}

MIN_SET_LENGTH = 3
MIN_RUN_LENGTH = 3

class Suits(OrderedEnum):
    CLUB = 0
    SPADE = 1
    HEART = 2
    DIAMOND = 3
    JOKER = 4


class Card:
    suit = None
    value = None
    is_fixed = None
    # Add visualization

    def __init__(self, suit, value):
        """
        Args:
            suit(Suits): suit of card
            value(int): int number of card (e.g., Ace is 1)
        """
        self.suit = suit
        self.value = value
        self.is_fixed = False

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit and self.value == other.value
        return False
    
    def __lt__(self, other):
        return (self.value, self.suit) < (other.value, other.suit)
    
    def __sub__(self, other):
        return self.value - other.value
    
    def __repr__(self):
        return "{}{}".format(SUIT_TEXT_MAP[self.suit.value], CARD_TEXT_MAP[self.value])
    
    def __hash__(self):
        return hash(self.suit) + hash(self.value)
    
    def same_suit(self, other):
        return self.suit == other.suit
    
    def same_value(self, other):
        return self.value == other.value
    
    def is_wild(self, round):
        return self.value == round or self.suit == Suits.JOKER or self.value == 14
    
    def get_score(self, round):
        if self.is_wild(round):
            return 0
        return min(self.value, 10)

def create_all_card_suits_for_value(value):
    cards = []
    for suit in Suits:
        if suit != Suits.JOKER:
            cards.append(Card(suit, value))
    return cards

class FixedCard(Card):
    wild_card = None

    def __init__(self, fixed_card, wild_card, round):
        if not wild_card.is_wild(round):
            raise "Cannot fix value of non-wild card: {} -> {}".format(self, card)
        if fixed_card.suit == Suits.JOKER:
            raise "Cannot fix suit of wild card to Joker: {}".format(self)
        self.value = fixed_card.value
        self.suit = fixed_card.suit
        self.is_fixed = True
        self.wild_card = wild_card

    def __repr__(self):
        return "{}{}({}{})".format(SUIT_TEXT_MAP[self.suit.value], CARD_TEXT_MAP[self.value], SUIT_TEXT_MAP[self.wild_card.suit.value], CARD_TEXT_MAP[self.wild_card.value])

    def __hash__(self):
        return hash(self.suit) + hash(self.value) + hash(self.wild_card)
    
    def is_wild(self, round):
        return False
    
    def get_score(self, round):
        return 0

class Deck:
    cards = None

    def __init__(self, decks=2):
        self.cards = []
        for _ in range(0, decks):
            for suit in Suits:
                if suit == Suits.JOKER:
                    for _ in range(2):
                        self.cards.append(Card(Suits.JOKER, 14))
                else:
                    for value in range(1,14):
                        self.cards.append(Card(suit, value))
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
    
    def __repr__(self):
        return "{} : {}".format(self.player_name, self.cards)

    def clear(self):
        self.cards.clear()

    def sort(self):
        self.cards.sort()
    
    def get_non_wilds(self, round):
        """
        Return a temporary list of all the cards ignoring wilds.
        """
        non_wilds = sorted(list(filter(lambda x: not x.is_wild(round), self.cards)))
        return non_wilds
    
    def get_wilds(self, round):
        """
        Return a temporary list of all the cards ignoring non-wilds.
        """
        wilds = sorted(list(filter(lambda x: x.is_wild(round), self.cards)))
        return wilds
    
    def get_score(self, round):
        return sum(map(lambda x: x.get_score(round), self.cards))
    
    def get_highest_value_card(self, round):
        if self.cards:
            highest_value = sorted(self.cards, key = lambda x: x.get_score(round))[-1]
            return highest_value
        return None

    def discard_highest_value(self, round):
        highest_value = self.get_highest_value_card(round)
        self.remove(highest_value)
        return highest_value

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
        if self.cards:
            return self.cards[-1]
        return None

class Play:
    cards = None
    group = None
    grow_right = False

    def __init__(self, cards, group = None, grow_right = False):
        self.cards = cards
        self.group = group
        self.grow_right = grow_right

    def __repr__(self):
        if self.group:
            if self.grow_right:
                return "{} <- {}".format(self.group, self.cards)
            else:
                return "{} -> {}".format(self.cards, self.group)
        return str(self.cards)

    def fix_wilds(self, round, fix_value = 1):
        if not self.group:
            self.cards = fix_wilds(self.cards, round, fix_value)

    def execute(self, hand, public_groups, round):
        if self.group:
            public_group = next(x for x in public_groups if x == self.group)
            for card in self.cards:
                public_group.add_card(card, round, self.grow_right)
                if card.is_fixed:
                    hand.remove(card.wild_card)
                else:
                    hand.remove(card)
            return None
        else:
            new_group = PublicGroup(self.cards, round)
            for card in self.cards:
                if card.is_fixed:
                    hand.remove(card.wild_card)
                else:
                    hand.remove(card)
            return new_group


def fix_set(cards, round, fix_value):
    extensions = get_possible_set_extensions(cards, round)
    if not extensions:
        raise Exception("Passed in cards are not a set in round {}: {}".format(round, cards))
    if extensions[0].suit == Suits.JOKER:
        value = fix_value
    else:
        value = extensions[0].value
    fixed_set = []
    for card in cards:
        if card.is_wild(round):
            fixed_set.append(FixedCard(Card(Suits.CLUB, value), card, round))
        else:
            fixed_set.append(card)
    return fixed_set

def fix_run(cards, round, fix_value):
    extensions = get_possible_run_extensions(cards, round)
    if not extensions:
        raise Exception("Passed in cards are not a run in round {}: {}".format(round, cards))
    
    lower_extension, upper_extension = extensions

    if lower_extension:
        first_lower_extension = lower_extension[0]
        if first_lower_extension.suit == Suits.JOKER:
            first_value = fix_value
            suit = Suits.CLUB
        else:
            first_value = first_lower_extension.value + 1
            suit = first_lower_extension.suit
    elif upper_extension:
        first_upper_extension = upper_extension[0]
        if first_upper_extension.suit == Suits.JOKER:
            first_value = fix_value
            suit = Suits.CLUB
        else:
            first_value = first_upper_extension.value - len(cards)
            suit = first_upper_extension.suit
    else:
        first_value = 1
        non_wilds = cards.get_non_wilds(round)
        if non_wilds:
            suit = non_wilds[0].suit
        else:
            suit = Suits.CLUB
    fixed_run = []
    for i, card in enumerate(cards):
        if card.is_wild(round):
            fixed_run.append(FixedCard(Card(suit, first_value + i), card, round))
        else:
            fixed_run.append(card)
    return fixed_run

def fix_wilds(cards, round, fix_value = 1):
    if is_valid_run(cards, round):
        return fix_run(cards, round, fix_value)
    elif is_valid_set(cards, round):
        return fix_set(cards, round, fix_value)
    else:
        raise Exception("Passed in cards are neither a set nor a run in round {}: {}".format(round, cards))

class PublicGroup:
    cards = None
    is_run = None

    def __init__(self, cards, round):
        for card in cards:
            if (card.is_wild(round)):
                raise Exception("Cannot add a wild card to a public group - fix the value of the wild first: {}".format(card))
        self.cards = cards
        self.is_run = is_valid_run(cards, round)
        if not self.is_run and not is_valid_set(cards, round):
            raise Exception("Trying to produce an illegal group in round {}: {}".format(round, self.cards))
    
    def __repr__(self):
        return str(self.cards)
    
    def __eq__(self, other):
        if isinstance(other, PublicGroup):
            return self.cards == other.cards
        return False
    
    def add_card(self, card, round, grow_right, auto_fix = True):
        if isinstance(card, Card):
            if grow_right:
                new_cards = self.cards + [card]
            else:
                new_cards = [card] + self.cards
            if auto_fix:
                new_cards = fix_wilds(new_cards, round)
            self.__init__(new_cards, round)
            return
        raise Exception("Can only add cards to groups: {}".format(card))

def get_possible_run_extensions(cards, round):
    """
    Check if this group is a valid run.
    Assumes the cards are sorted.
    """
    def get_first_represented_card(cards):
        for i, card in enumerate(cards):
            if not card.is_wild(round):
                return Card(card.suit, card.value - i)
        return Card(Suits.JOKER, 14)
    
    # Figure out what the first card of the run must be, even if it's actually a wild.
    first_card = get_first_represented_card(cards)
    if first_card.suit == Suits.JOKER:
        # All wilds.
        if (len(cards) > 13):
            # Invalid run.
            return None
        elif (len(cards) == 13):
            # Valid, but no extensions.
            return (None, None)
        elif (len(cards) == 12):
            # Valid, with one side able to be expanded.
            if first_card.value == 1:
                return (None, create_all_card_suits_for_value(13))
            else:
                return (create_all_card_suits_for_value(1), None)
        else:
            # Valid, with both sides able to be expanded.
            return ([Card(Suits.JOKER, 14)], [Card(Suits.JOKER, 14)])
    if first_card.value < 1:
        # A wild necessarily is representing an illegal value.
        return None
    for i, card in enumerate(cards):
        expected_value = first_card.value + i
        if expected_value > 13 or (not card.is_wild(round) and (card.value != expected_value or card.suit != first_card.suit)):
            return None
    # This is a valid run. Get the first and last values.
    return ([Card(first_card.suit, first_card.value - 1)] if first_card.value - 1 >= 1 else None,
            [Card(first_card.suit, first_card.value + len(cards))] if first_card.value + len(cards) <= 13 else None)

def is_valid_run(cards, round):
    """
    Check if this group is a valid run.
    Assumes the cards are sorted.
    """
    return (len(cards) >= MIN_RUN_LENGTH) and get_possible_run_extensions(cards, round) != None

def get_cards_that_can_extend_run_by_one(cards, round, starting_run = None, grow_right = True):
    if starting_run is None:
        starting_run = []
    def get_possible_extensions(extension):
        possible_cards = []
        for card in extension:
            if not card:
                continue
            # If we have a non-wild card we can use...
            non_wild_set = sorted(list(set(cards.get_non_wilds(round))))
            if card.suit == Suits.JOKER:
                possible_cards.extend(non_wild_set)
            elif card in non_wild_set:
                possible_cards.append(card)

            # If we have a wild...
            wild_cards = cards.get_wilds(round)
            if wild_cards:
                possible_cards.append(wild_cards[0])
        return possible_cards

    extensions = get_possible_run_extensions(starting_run, round)
    if extensions:
        lower_extension, upper_extension = extensions
        if grow_right and upper_extension:
            return get_possible_extensions(upper_extension)
        elif not grow_right and lower_extension:
            return get_possible_extensions(lower_extension)
        return []
    else:
        return None

def get_runs(cards, round, starting_run = None, grow_right = True):
    if starting_run is None:
        starting_run = []
    def remove_card(to_remove):
        cards_copy = copy.deepcopy(cards)
        cards_copy.cards.remove(to_remove)
        return cards_copy

    extension_cards = get_cards_that_can_extend_run_by_one(cards, round, starting_run, grow_right)
    if extension_cards is None:
        return
    if len(starting_run) >= MIN_RUN_LENGTH:     
        yield starting_run
    for card in extension_cards:
        if grow_right:
            yield from get_runs(remove_card(card), round, starting_run + [card], grow_right)
        else:
            yield from get_runs(remove_card(card), round, [card] + starting_run, grow_right)

def get_non_redundant_runs(cards, round):
    non_wild_cards = sorted(list(set(cards.get_non_wilds(round))))
    wild_cards = cards.get_wilds(round)

    suit_groups = groupby(non_wild_cards, lambda x: x.suit)
    for suit, non_wild_suited in suit_groups:
        non_wild_suited = sorted(list(non_wild_suited))
        for i in range(len(non_wild_suited)):
            for j in range(i, len(non_wild_suited)):
                potential_run = non_wild_suited[i:j+1]
                span = potential_run[-1].value - potential_run[0].value + 1
                critical_wild_count = max(span, MIN_RUN_LENGTH) - len(potential_run)

                if critical_wild_count > len(wild_cards):
                    continue
                
                wild_copy = copy.deepcopy(wild_cards)

                def take_n_wilds(wild_list, n):
                    if n <= 0:
                        return []
                    n_wilds = wild_list[-n:]
                    del wild_list[-n:]
                    return n_wilds

                # Insert the required internal wilds.
                k = 1
                while k < len(potential_run):
                    gap = (potential_run[k].value - potential_run[k - 1].value - 1)
                    
                    if not gap:
                        k += 1
                        continue
                    potential_run = potential_run[:k] + take_n_wilds(wild_copy, gap) + potential_run[k:]
                    k += gap + 1

                # Insert the required external wilds.
                # Keep track of first and last non-wild index for bookkeeping purposes.
                external_wild_count = max(MIN_RUN_LENGTH - len(potential_run), 0)
                first_non_wild, last_non_wild = 0, len(potential_run)
                if external_wild_count:
                    # Try and insert the whole pack either in the front or in the back.
                    # Since we have a small MIN_RUN_LENGTH, this algorithm is fast and
                    # works well enough. If it were larger, we would need to be more
                    # careful.
                    if (potential_run[-1].value <= 13 - external_wild_count):
                        potential_run.extend(take_n_wilds(wild_copy, external_wild_count))
                    elif (potential_run[0].value >= external_wild_count + 1):
                        potential_run = take_n_wilds(wild_copy, external_wild_count) + potential_run
                        first_non_wild += external_wild_count
                        last_non_wild += external_wild_count
                    else:
                        # We should never hit this.
                        continue

                # Now we have some non-critical wilds that we can replace elements of the list with.
                # Only internal elements should ever be replaced; replacing wilds is redundant.
                # We should end up with (span - 2) choose (extra_wild_count) runs from this.
                # First, get the indices of all internal elements that can be replaced.
                internal_non_wild_indices = []
                for k in range(first_non_wild + 1, last_non_wild - 1):
                    if not potential_run[k].is_wild(round):
                        internal_non_wild_indices.append(k)
                for wilds in range(len(wild_copy) + 1):
                    for g in combinations(internal_non_wild_indices, wilds):
                        output_run = copy.deepcopy(potential_run)
                        for wild_idx, idx in enumerate(g):
                            output_run[idx] = copy.deepcopy(wild_copy[wild_idx])
                        yield output_run

def get_single_runs_on_groups(cards, round, groups):
    all_possible_extensions = []
    run_groups = filter(lambda x: x.is_run, groups)
    for group in run_groups:
        for grow_right in [False, True]:
            extension_cards = get_cards_that_can_extend_run_by_one(cards, round, group.cards, grow_right)
            for card in extension_cards:
                all_possible_extensions.append((card, group, grow_right))
    
    return all_possible_extensions

def get_possible_set_extensions(cards, round):
    filter_cards = list(filter(lambda x: not x.is_wild(round), cards))
    if (len(filter_cards) == 0):
        return [Card(Suits.JOKER, 14)]
    elif (len(filter_cards) == 1):
        return create_all_card_suits_for_value(cards[0].value)
    else:
        set_value = reduce(lambda x, y: x if x == y else 0, map(lambda x: x.value, filter_cards))
        if set_value != 0:
            return create_all_card_suits_for_value(set_value)
        else:
            return None

def is_valid_set(cards, round):
    """
    Check if this group is a valid set.
    """
    return (len(cards) >= MIN_SET_LENGTH) and get_possible_set_extensions(cards, round) != None

def get_sets(cards, round, only_maximum_size = False):
    non_wild_cards = cards.get_non_wilds(round)
    wild_cards = cards.get_wilds(round)

    # Differentiating between wilds is meaningless, so we will not.
    # Return sets that can be made with all wilds.
    if len(wild_cards) >= MIN_SET_LENGTH:
        start_bound = len(wild_cards) if only_maximum_size else MIN_SET_LENGTH
        for i in range(start_bound, len(wild_cards) + 1):
            yield wild_cards[:i]

    # Return all sets with at least one real card.
    possible_sets = groupby(non_wild_cards, lambda x: x.value)
    for _, group in possible_sets:
        possible_set = list(group)
        if only_maximum_size and (len(possible_set) + len(wild_cards) >= MIN_SET_LENGTH):
            yield possible_set + wild_cards
        else:
            for card_count in range(1, len(possible_set) + 1):
                for wild_count in range(max(MIN_SET_LENGTH - card_count, 0), len(wild_cards) + 1):
                    yield possible_set[0:card_count] + wild_cards[:wild_count]

def get_non_wild_set_values_on_groups(cards, round, groups):
    set_groups = filter(lambda x: not x.is_run, groups)

    all_possible_sets = set()
    for group in set_groups:
        # This is guaranteed to not be None, and it's okay that it might be wild.
        all_possible_sets.add(get_possible_set_extensions(group.cards, round)[0].value)
    
    non_wild_cards = set(map(lambda x: x.value, cards.get_non_wilds(round)))
    return all_possible_sets.intersection(non_wild_cards)

def get_all_plays(cards, round, groups, line = None):
    if line is None:
        line = []

    def remove_first_wild(cards_to_copy=cards):
        cards_copy = copy.deepcopy(cards_to_copy)
        for card in cards_copy.cards:
            if card.is_wild(round):
                cards_copy.cards.remove(card)
                return card, cards_copy
        return None, None

    def remove_cards(to_remove):
        cards_copy = copy.deepcopy(cards)
        for card in to_remove:
            cards_copy.cards.remove(card)
        return cards_copy

    def add_to_group(card, target_group, grow_right):
        groups_copy = copy.deepcopy(groups)
        for group in groups_copy:
            if target_group == group:
                group.add_card(card, round, grow_right)
                return groups_copy
        raise Exception("Failed to add card to group!")
    
    def add_to_line(play):
        line_copy = copy.deepcopy(line)
        line_copy.append(play)
        return line_copy
    
    # We can't be greedy here.
    for run in get_non_redundant_runs(cards, round):
        yield from get_all_plays(remove_cards(run), round, groups, add_to_line(Play(run)))

    run_groups = list(filter(lambda x: x.is_run, groups))
    if (run_groups):
        # Check all subplays on group runs first.
        # We can't be greedy here either.
        for card, group, grow_right in get_single_runs_on_groups(cards, round, run_groups):
            if card.is_fixed:
                card.wild_card, remaining_cards = remove_first_wild()
                if card.wild_card:
                    yield from get_all_plays(remaining_cards, round, add_to_group(card, group, grow_right), add_to_line(Play([card], group, grow_right)))
            else:
                yield from get_all_plays(remove_cards([card]), round, add_to_group(card, group, grow_right), add_to_line(Play([card], group, grow_right)))

    # We can be greedy here.
    for set in get_sets(cards, round, True):
        yield from get_all_plays(remove_cards(set), round, groups, add_to_line(Play(set)))

    # At this point, we can play out any cards we have, including wilds, onto public groups.
    # We can continue to be greedy here.
    remaining_cards = copy.deepcopy(cards)
    set_groups = list(filter(lambda x: not x.is_run, groups))
    
    line = copy.deepcopy(line)
    if set_groups:
        for value in get_non_wild_set_values_on_groups(cards, round, set_groups):
           group = next(filter(lambda x: x.cards[0].value == value, set_groups))
           cards_to_play = list(filter(lambda x: x.value == value, cards.get_non_wilds(round)))
           line.append(Play(cards_to_play, group))
           for card in cards_to_play:
               remaining_cards.remove(card)
        wilds = cards.get_wilds(round)
        if wilds:
            line.append(Play(wilds, set_groups[0]))
            for card in wilds:
                remaining_cards.remove(card)

    yield remaining_cards, line

def check_go_out(hand, round, groups):
    best_play = sorted(list(get_all_plays(hand, round, groups)), key = lambda x: x[0].get_score(round))[0]
    return best_play[0] == 0