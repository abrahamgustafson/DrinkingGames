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
        if self.length():
            return self.cards.pop()
        return None

    def length(self):
        return len(self.cards)


class Hand:
    cards = None

    def __init__(self, cards = None):
        if cards:
            self.cards = cards
        else:
            self.cards = []
    
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
        return str(self.cards)

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

class PlayExtension:
    first_value = None
    last_value = None
    suits = None
    round = None

    def __init__(self, round, suit, first_value, last_value = None):
        if last_value is not None and last_value <= first_value:
            raise Exception("Passed in invalid range to PlayExtension: {} -> {}".format(first_value, last_value))
        self.first_value = first_value
        self.last_value = last_value if last_value is not None else first_value
        self.suit = suit
        self.round = round
    
    def __contains__(self, item):
        if isinstance(item, Card):
            if item.is_wild(self.round):
                return True
            if self.suit != Suits.JOKER and item.suit != self.suit:
                return False
            return self._in(item.value)
        else:
            return self._in(item)
    
    def __repr__(self):
        if self.is_single_value():
            return "Extension {} {}".format(self.first_value, self.suit)
        else:
            return "Extension {} {} {}".format(self.first_value, self.last_value, self.suit)
    
    def is_single_value(self):
        return self.last_value != self.first_value
    
    def _in(self, value):
        return value >= self.first_value and value <= self.last_value

class Play:
    cards = None
    round = None
    _extensions = None

    def __init__(self, cards, round):
        self.cards = cards
        self.round = round
        self._extensions = self._calculate_extensions()

    def __repr__(self):
        return str(self.cards)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.cards == other.cards and self.round == other.round
        return False
    
    def get_possible_extensions(self):
        if not self._extensions:
            self._extensions = self._calculate_extensions()
        return self._extensions
    
    def add_cards(self, cards, grow_right):
        if grow_right:
            self.cards.extend(cards)
        else:
            self.cards = cards + self.cards
        self._extensions = self._calculate_extensions()
        if not self._extensions:
            if grow_right:
                raise Exception("Added invalid card to play: {} -> {}".format(self.cards, cards))
            else:
                raise Exception("Added invalid card to play: {} <- {}".format(cards, self.cards))
        return True
            
    def execute_on(self, hand, public_groups = None):
        for card in self.cards:
            if card.is_fixed:
                hand.remove(card.wild_card)
            else:
                hand.remove(card)
        self.fix_wilds()
        return self

class SetPlay(Play):
    def __init__(self, cards, round, min_set_length = MIN_SET_LENGTH):
        super().__init__(cards, round)
        if len(self.cards) < min_set_length or not self.get_possible_extensions():
            raise Exception("{} is not a valid set in round {}".format(self.cards, self.round))
    
    def can_add_card(self, card, grow_right):
        if card.is_wild(self.round):
            return True

        return card in self.get_possible_extensions()

    def fix_wilds(self, fix_value = 1):
        extension = self.get_possible_extensions()
        if fix_value in extension:
            value = fix_value
        else:
            value = extension.first_value
        for i, card in enumerate(self.cards):
            if card.is_wild(self.round):
                self.cards[i] = FixedCard(Card(Suits.CLUB, value), card, self.round)
    
    def _calculate_extensions(self):
        filter_cards = list(filter(lambda x: not x.is_wild(self.round), self.cards))
        if not filter_cards:
            return PlayExtension(self.round, Suits.JOKER, 1, 13)
        
        set_value = reduce(lambda x, y: x if x == y else 0, map(lambda x: x.value, filter_cards), filter_cards[0].value)
        if set_value:
            return PlayExtension(self.round, Suits.JOKER, set_value)
        return None

class RunPlay(Play):
    def __init__(self, cards, round, min_run_length = MIN_RUN_LENGTH):
        super().__init__(cards, round)
        if len(self.cards) < min_run_length or not self.get_possible_extensions():
            raise Exception("{} is not a valid run in round {}".format(self.cards, self.round))
    
    def get_suit(self):
        return self._get_first_represented_card().suit

    def can_add_card(self, card, grow_right = True):
        lower_extension, upper_extension = self.get_possible_extensions()

        if grow_right and upper_extension:
            return card in upper_extension
        elif not grow_right and lower_extension:
            return card in lower_extension
        return False

    def fix_wilds(self, fix_value = 1):
        lower_extension, upper_extension = self.get_possible_extensions()
        suit = Suits.CLUB
        if lower_extension:
            if fix_value - 1 in lower_extension:
                first_value = fix_value
            else:
                first_value = max(lower_extension.first_value, lower_extension.last_value) + 1
            if lower_extension.suit != Suits.JOKER:
                suit = lower_extension.suit
        elif upper_extension:
            if fix_value + len(self.cards) in upper_extension:
                first_value = fix_value
            elif upper_extension.first_value - len(self.cards) >= 1:
                first_value = upper_extension.first_value - len(self.cards)
            else:
                first_value = upper_extension.last_value - len(self.cards)
            if upper_extension.suit != Suits.JOKER:
                suit = upper_extension.suit
        else:
            first_value = 1
            non_wilds = self.cards.get_non_wilds(self.round)
            if non_wilds:
                suit = non_wilds[0].suit
        for i, card in enumerate(self.cards):
            if card.is_wild(self.round):
                self.cards[i] = FixedCard(Card(suit, first_value + i), card, self.round)

    def _get_first_represented_card(self):
        for i, card in enumerate(self.cards):
            if not card.is_wild(self.round):
                return Card(card.suit, card.value - i)
        return Card(Suits.JOKER, 14)

    def _calculate_extensions(self):
        # Figure out what the first card of the run must be, even if it's actually a wild.
        first_card = self._get_first_represented_card()
        if first_card.suit == Suits.JOKER:
            # All wilds.
            if (len(self.cards) > 13):
                # Invalid run.
                return None
            elif (len(self.cards) == 13):
                # Valid, but no extensions.
                return (None, None)
            elif (len(self.cards) == 12):
                # Valid, with one side able to be expanded.
                if first_card.value == 1:
                    return (None, PlayExtension(self.round, Suits.JOKER, 13))
                else:
                    return (PlayExtension(self.round, Suits.JOKER, 1), None)
            else:
                # Valid, with both sides able to be expanded.
                return (PlayExtension(self.round, Suits.JOKER, 1, 13 - len(self.cards)),
                        PlayExtension(self.round, Suits.JOKER, len(self.cards) + 1, 13))
        if first_card.value < 1:
            # A wild necessarily is representing an illegal value.
            return None
        for i, card in enumerate(self.cards):
            expected_value = first_card.value + i
            if expected_value > 13 or (not card.is_wild(self.round) and (card.value != expected_value or card.suit != first_card.suit)):
                return None
        # This is a valid run. Get the first and last values.
        return (PlayExtension(self.round, first_card.suit, first_card.value - 1) if first_card.value - 1 >= 1 else None,
                PlayExtension(self.round, first_card.suit, first_card.value + len(self.cards)) if first_card.value + len(self.cards) <= 13 else None)
    
    def select_possible_extensions_from_hand(self, hand):
        possible_lower_extensions, possible_upper_extensions = set(), set()
        for card in hand.cards:
            if self.can_add_card(card, True):
                possible_upper_extensions.add(card)
            if self.can_add_card(card, False):
                possible_lower_extensions.add(card)
        return possible_lower_extensions, possible_upper_extensions

class PublicGroupPlay(Play):
    group = None
    grow_right = False

    def __init__(self, cards, round, group, grow_right):
        self.group = group
        self.grow_right = grow_right
        super().__init__(cards, round)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.cards == other.cards and self.round == other.round and self.group == other.group and self.grow_right == other.grow_right
        return False
    
    def __repr__(self):
        if self.grow_right:
            return "{} <- {}".format(self.group, self.cards)
        else:
            return "{} -> {}".format(self.cards, self.group)
        
    def can_add_card(self, card, grow_right = True):
        if grow_right != self.grow_right:
            return False
        try:
            if grow_right:
                self._create_total_group(self.cards + card)
            else:
                self._create_total_group(card + self.cards)
        except:
            return False
        return True
        
    def fix_wilds(self, fix_value = 1):
        fixed_play = self._create_total_group(self.cards)
        fixed_play.fix_wilds(fix_value)

        if self.grow_right:
            self.cards = fixed_play.cards[-len(self.cards):]
        else:
            self.cards = fixed_play.cards[:len(self.cards)]

    def execute_on(self, hand, public_groups):
        if self.group not in public_groups:
            print("{} not in {}".format(self.group, public_groups))
        public_group = next(x for x in public_groups if x == self.group)
        public_group.add_cards(self.cards, self.grow_right)
        for card in self.cards:
            if card.is_fixed:
                hand.remove(card.wild_card)
            else:
                hand.remove(card)
        public_group.fix_wilds()
        return public_group

    def _create_total_group(self, cards):
        if self.grow_right:
            total_group = self.group.cards + cards
        else:
            total_group = cards + self.group.cards
        try:
            return SetPlay(total_group, self.round)
        except:
            try:
                return RunPlay(total_group, self.round)
            except:
                raise Exception("{} is not a valid play in round {}".format(cards, self.round))
    
    def _calculate_extensions(self):
        return self._create_total_group(self.cards).get_possible_extensions()

def get_runs(cards, round, starting_run = None, grow_right = True):
    if starting_run is None:
        starting_run = []

    def remove_card(to_remove):
        cards_copy = copy.deepcopy(cards)
        cards_copy.cards.remove(to_remove)
        return cards_copy

    if len(starting_run) >= MIN_RUN_LENGTH:
        yield starting_run
    
    lower_extension_cards, upper_extension_cards = RunPlay(starting_run, round, 0).select_possible_extensions_from_hand(cards)
    if grow_right:
        for card in upper_extension_cards:
            yield from get_runs(remove_card(card), round, starting_run + [card], grow_right)
    else:
        for card in lower_extension_cards:
            yield from get_runs(remove_card(card), round, [card] + starting_run, grow_right)

def _expand_sorted_non_wild_run_with_wilds(potential_run, wild_cards, round, minimum_run_length = MIN_RUN_LENGTH):
    if not potential_run:
        return None
    span = potential_run[-1].value - potential_run[0].value + 1
    critical_wild_count = max(span, minimum_run_length) - len(potential_run)

    if critical_wild_count > len(wild_cards):
        return None
    
    wild_copy = copy.deepcopy(wild_cards)
    def take_n_wilds(n):
        if n <= 0:
            return None
        n_wilds = wild_copy[-n:]
        del wild_copy[-n:]
        return n_wilds

    # Insert the required internal wilds.
    k = 1
    while k < len(potential_run):
        gap = (potential_run[k].value - potential_run[k - 1].value - 1)
        
        if gap < 0:
            raise Exception("Passed in run isn't sorted: {}".format(potential_run))
        elif gap:
            potential_run = potential_run[:k] + take_n_wilds(gap) + potential_run[k:]
        k += gap + 1

    # Insert the required external wilds.
    # Keep track of first and last non-wild index for bookkeeping purposes.
    external_wild_count = max(minimum_run_length - len(potential_run), 0)
    first_non_wild, last_non_wild = 0, len(potential_run)
    if external_wild_count:
        # Try and insert the whole pack either in the front or in the back.
        # Since we have a small MIN_RUN_LENGTH, this algorithm is fast and
        # works well enough. If it were larger, we would need to be more
        # careful.
        if (potential_run[-1].value <= 13 - external_wild_count):
            potential_run.extend(take_n_wilds(external_wild_count))
        elif (potential_run[0].value >= external_wild_count + 1):
            potential_run = take_n_wilds(external_wild_count) + potential_run
            first_non_wild += external_wild_count
            last_non_wild += external_wild_count
        else:
            # We should never hit this.
            return None

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

def get_non_redundant_runs(cards, round):
    non_wild_cards = sorted(list(set(cards.get_non_wilds(round))))
    wild_cards = cards.get_wilds(round)

    suit_groups = groupby(non_wild_cards, lambda x: x.suit)
    for _, non_wild_suited in suit_groups:
        non_wild_suited = sorted(list(non_wild_suited))
        for i in range(len(non_wild_suited)):
            for j in range(i, len(non_wild_suited)):
                yield from _expand_sorted_non_wild_run_with_wilds(non_wild_suited[i:j+1], wild_cards, round)

def get_non_redundant_run_group_extensions(cards, round, group):
    lower_extension, upper_extension = group.get_possible_extensions()
    group_suit = group.get_suit()
    non_wild_cards = sorted(list(filter(lambda x: x.suit == group_suit, set(cards.get_non_wilds(round)))))
    wild_cards = cards.get_wilds(round)
    
    possible_upper_extensions = []
    possible_lower_extensions = []
    if upper_extension:
        for top_value in range(upper_extension.first_value - 1, upper_extension.last_value):
            non_wild_set = list(filter(lambda x: x.value > top_value, non_wild_cards))
            for i in range(1, len(non_wild_set) + 1):
                for possible_extension in _expand_sorted_non_wild_run_with_wilds([Card(group_suit, top_value)] + non_wild_set[:i], wild_cards, round, 2):
                    possible_upper_extensions.append(possible_extension[1:])
    if lower_extension:
        for bottom_value in range(lower_extension.first_value + 1, lower_extension.last_value + 2):
            non_wild_set = list(filter(lambda x: x.value < bottom_value, non_wild_cards))
            for i in range(0, len(non_wild_set)):
                for possible_extension in _expand_sorted_non_wild_run_with_wilds(non_wild_set[i:] + [Card(group_suit, bottom_value)], wild_cards, round, 2):
                    possible_lower_extensions.append(possible_extension[:-1])
    
    return possible_lower_extensions, possible_upper_extensions

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
    set_groups = filter(lambda x: isinstance(x, SetPlay), groups)
    all_possible_sets = set([x.get_possible_extensions().first_value for x in set_groups])
    non_wild_cards = set(map(lambda x: x.value, cards.get_non_wilds(round)))
    return non_wild_cards.intersection(all_possible_sets)

def get_all_plays(cards, round, public_groups, line = None):
    if line is None:
        line = []

    def remove_cards(to_remove):
        cards_copy = copy.deepcopy(cards)
        for card in to_remove:
            cards_copy.cards.remove(card)
        return cards_copy

    def add_to_group(cards, target_group, grow_right):
        groups_copy = copy.deepcopy(public_groups)
        for group in groups_copy:
            if target_group == group:
                group.add_cards(cards, grow_right)
                group.fix_wilds()
                return groups_copy
        raise Exception("Failed to add card to group!")
    
    def add_to_line(play):
        line_copy = copy.deepcopy(line)
        line_copy.append(play)
        return line_copy
    
    # We can't be greedy here.
    for run in get_non_redundant_runs(cards, round):
        yield from get_all_plays(remove_cards(run), round, public_groups, add_to_line(RunPlay(run, round)))

    run_groups = list(filter(lambda x: isinstance(x, RunPlay), public_groups))
    if (run_groups):
        # Check all subplays on group runs first.
        # We can't be greedy here either.
        for group in run_groups:
            lower_extensions, upper_extensions = get_non_redundant_run_group_extensions(cards, round, group)

            for extension in lower_extensions:
                yield from get_all_plays(remove_cards(extension), round, add_to_group(extension, group, False), add_to_line(PublicGroupPlay(extension, round, group, False)))
            for extension in upper_extensions:
                yield from get_all_plays(remove_cards(extension), round, add_to_group(extension, group, True), add_to_line(PublicGroupPlay(extension, round, group, True)))

    # We can be greedy here.
    for set in get_sets(cards, round, True):
        yield from get_all_plays(remove_cards(set), round, public_groups, add_to_line(SetPlay(set, round)))

    # At this point, we can play out any cards we have, including wilds, onto public groups.
    # We can continue to be greedy here.
    remaining_cards = copy.deepcopy(cards)

    # Try and play on existing sets.
    set_groups = list(filter(lambda x: isinstance(x, SetPlay), public_groups))
    wilds = cards.get_wilds(round)
    if set_groups:
        for value in get_non_wild_set_values_on_groups(cards, round, set_groups):
           group = next(filter(lambda x: x.cards[0].value == value, set_groups))
           cards_to_play = list(filter(lambda x: x.value == value, cards.get_non_wilds(round)))
           line.append(PublicGroupPlay(cards_to_play, round, group, True))
           for card in cards_to_play:
               remaining_cards.remove(card)

    # We may have wilds left over at the end. We've already tried wilds against
    # all of our sets, but they can be played against any run we've made.
    # Greedily add them to any run we can.
    def add_wild_to_plays(wild):
        if not wild:
            return False
        for play in filter(lambda x: isinstance(x, RunPlay) or isinstance(x, PublicGroupPlay), line):
            for right in [True, False]:
                if play.can_add_card(wild, right):
                    remaining_cards.remove(wild)
                    play.add_cards([wild], right)
                    return True
        return False


    while wilds:
        if not add_wild_to_plays(wilds.pop()):
            break

    yield remaining_cards, line

def check_go_out(hand, round, groups):
    best_play = sorted(list(get_all_plays(hand, round, groups)), key = lambda x: x[0].get_score(round))[0]
    return best_play[0] == 0