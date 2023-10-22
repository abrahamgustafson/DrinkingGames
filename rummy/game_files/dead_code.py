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

    """
    This ends up being too big after getting up to 14 in size.. 
        | group_permutation_order = list(permutations(range(len(runs) + len(sets))))

            n! = 14!
            14! = 14 x 13 x 12 x 11 x 10 x 9 x 8 x 7 x 6 x 5 x 4 x 3 x 2 x 1
            14! = 87,178,291,200
            10! =      3,628,800
        11 is hard perf cap on my machine, 10 is a safer bet
    
    I really need to come up with a way to reduce or cap these, though I have to do it in
    a way that doesn't mean results are only so good.. 
    Ideas:
        1) [x] Loop through permutations instead of making a copy of that list and trying to go through it (?)
        2) [ ] Try to do some pre-filter of permutations to avoid the impossible cases. EG, make a graph of 
           mutually exclusive combinations (but I would need to come up with the permutation before then?)

    2)
        x: [1,2]
        y: [a,b,c]

            Order still matters while determining "Mutually exclusive", unless you limit to pairs...
            EG, starting with 1:
                1, [2,a,b,c] -> 2
                    [a,b,c] -> a            x
                        [b,c] -> b          |
                            [c] -> c        |
                        [b,c] -> c          |
                            [b] -> b        |
                    [a,b,c] -> b            o
                        [a,c] -> a          o
                            [c] -> c        x
                        [a,c] -> c          x
                            [a] -> a        |
                    [a,b,c] -> c            x
                        ...                 |
                1, [2,a,b,c] -> a
                    ...
                        ...
                            ...
                2, [1,a,b,c]
            BUT --> this could mean the permutations get significantly reduced,
            The scenarios where this blows up is typically when wilds are introduced.
                        

        [1]: [a]
        [2]: []
        [a]: [b]
        [c]: [a,2]

        then loop through just the permutations of the produced sets?
    """
    # group_permutation_order = list(permutations(range(len(runs) + len(sets))))

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
    
    # logging.debug('group permutation order length: {}'.format(len(group_permutation_order)))
    total_cycles = 0
    # for order in group_permutation_order:
    for order in list(permutations(range(len(runs) + len(sets)))):

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

    logging.debug("Total cycles: {}".format(total_cycles))

    # Sort by the lowest value...
    outage_scenarios.sort(key = lambda x: x[3]) 

    # Greedy strategy, just discard the highest card that isn't in a run.
    chosen_scenario = outage_scenarios[0]
    hand.remove(chosen_scenario[1])

    return chosen_scenario[3], chosen_scenario[1], chosen_scenario[0]

    # Card discard strategy, return the highest card with the least combinations

    # Add a <play off others> mechanic after.



    """
    Need a way to construct sets off of another players runs...
    # We actually need to look for up to length 4... up to 2 on either side.

    existing = [[2h*,3h*,4h*]]
    ours = [1h, 5h, 6h]
    desired_output = [
        [1h,2h*,3h*,4h*],
        [2h*,3h*,4h*,5h],
        [1h,2h*,3h*,4h*,5h],
        [2h*,3h*,4h*,5h,6h],
        [1h,2h*,3h*,4h*,5h,6h],
    ]

    for existing_run in existing_runs:
        for left_options in range(0,3):
            for right_options in range(0,3):
                [0-2][existing_run][0-2]

    
    Could do some smart assumption below... If you play anything on someone elses run or set,
    you take it out of play and edit that scenario to be pulbic_group: [1h,2h*,3h*,4h*,5h],

    Options:
        1) Return a group of [all our runs], [all runs building off existing]
            - where the latter 
        2) Return [all_sets], where each set has an indicator for each card saying it's ours or not.
    """


            # If the length on the left or right is == 1, do NOT put a wild on.
        # There is no point adding a wild to the end of a run.

        # I can't really do recursive here... If I did one card at a time, I would get the scenario:
            # left 2, right 2
            # left 1, right 2
            # left 0, right 2
            # left 0, right 1
            # left 0, right 0
        # Actually that does work. It doesn't need to be recursive though, first selection should be 
        # sufficient, given that each run I play off is mutually exclusive.
        # Simply loop through left until 0, and right until 0, adding if we reach zero, or returning if we can't reach it.

        # ONLY PROBLEM is that wilds are not interchangable..
        # Let's say I pick [1h, W1, 3h*, 4h*, 5h*], I may pick this option in the above strategy,
        # but that would take W1 out of the rotation for all other combinations.
        # TODO: I think this is still the best path to go down, but I have to build some interchangable wild check
        # In the outer loop.