import argparse
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import itertools

TIME_COL_ID = 'Time sequence'
RULE_COL_ID = 'Rule'
ID_COL_ID = 'id'
DEBUG_ENABLED = True


def get_movie_in_data_frame(file_path):
    """
    Args:
        file_path(string): absolute path to file.
    Returns:
        map<string, list<int(seconds duration from start)>>
    """

    # Return map of rule to occurences
    #   map<string, list<int(seconds duration from start)>>
    filtered_occurence_map = dict()

    with open(file_path, encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file)

        # Iterate over each row in the csv using reader object
        is_first_row = True

        # must be updated. hacky.
        rule_index = 0
        occcurence_index = 0

        column_id_list = []

        for row in csv_reader:
            if is_first_row:
                column_id_list = row
                is_first_row = False
                
                assert TIME_COL_ID in row
                assert RULE_COL_ID in row
                rule_index = row.index(RULE_COL_ID)
                occcurence_index = row.index(TIME_COL_ID)
                continue
            
            # Base case, ignore row if it has no rule or occurences
            if DEBUG_ENABLED:
                print("Row object: {}".format(len(row)))
                print("row rule index: {},  row occurence index: {}".format(rule_index, occcurence_index))
            if len(row) < 2:
                print("Something is likely wrong with parse... row: {}".format(row))
            else:
                if len(row[rule_index]) != 0 and len(row[occcurence_index]) != 0:
                    if DEBUG_ENABLED:
                        print("Rule:  [{}],  Occurences: [{}]".format(row[rule_index], row[occcurence_index]))

                        raw_timestamp_list = row[occcurence_index].split('\n')
            
                        if DEBUG_ENABLED:
                            print("num occurences: {}".format(len(raw_timestamp_list)))

                        assert row[rule_index] not in filtered_occurence_map.keys()

                        filtered_occurence_list = []
                        for raw_timestamp in raw_timestamp_list:
                            if DEBUG_ENABLED:
                                print("Raw time string: {}".format(raw_timestamp))
                            if len(raw_timestamp) < 4:
                                print("bad input.. skipping")
                                continue
                            date_time = datetime.strptime(raw_timestamp.strip(), "%H:%M:%S")
                            a_timedelta = date_time - datetime(1900, 1, 1)
                            seconds = a_timedelta.total_seconds()
                            if DEBUG_ENABLED:
                                print("Parsed Seconds: {}".format(seconds))
                            filtered_occurence_list.append(seconds)
                        
                        filtered_occurence_map[row[rule_index]] = filtered_occurence_list
            

    return filtered_occurence_map

# Function to sort the list of tuples by its second item
def sort_tuple(tup): 
      
    # getting length of list of tuples
    lst = len(tup) 
    for i in range(0, lst): 
          
        for j in range(0, lst-i-1): 
            if (tup[j][1] > tup[j + 1][1]): 
                temp = tup[j] 
                tup[j]= tup[j + 1] 
                tup[j + 1]= temp 
    return tup 

# Function to do insertion sort
def insertion_sort_tuple_by_second_value(tuple_list, largest_first=False):
  
    # Traverse through 1 to len(tuple_list)
    for i in range(1, len(tuple_list)):
  
        key = tuple_list[i]
  
        if (not largest_first):
            # Move elements of arr[0..i-1], that are
            # greater than key, to one position ahead
            # of their current position
            j = i-1
            while j >=0 and key[1] < tuple_list[j][1] :
                    tuple_list[j+1] = tuple_list[j]
                    j -= 1
            tuple_list[j+1] = key
        else:
            j = i-1
            while j >=0 and key[1] > tuple_list[j][1] :
                    tuple_list[j+1] = tuple_list[j]
                    j -= 1
            tuple_list[j+1] = key


def get_closest_n_rule_combinations(rule_map, desired_drink_count, equal_consideration_count, combination_cap, prefer_more_rules, max_viable_combinations=5):
    """
    Args:
        rule_map: map<string, list<int(seconds duration from start)>>
    """
    values_as_count = []
    values_as_count_map = {}
    for key, val in rule_map.items():
        values_as_count_map[key] = len(val)
        values_as_count.append(len(val))

    rule_count = len(rule_map.keys())

    # list of tuples in form  [(rule_combination, abs_num_off_ideal)]
    # We want the lowest value, closest to 0
    combination_tuples = list()

    # combination tuples of top N
    top_n_rule_sets = list()

    # Absolutely brute forcing this. 
    min_rule_count = 1

    range_func = range(min_rule_count, combination_cap)
    if prefer_more_rules:
        range_func = range(combination_cap, min_rule_count, -1)


    print("Chugging on combinations... from size {} to {} for total rule count: {}".format(min_rule_count, combination_cap, rule_count))
    # for n in range(1, 3):
    for n in range_func:
        # For Each rule (get all possible combinations of length n)
        for subset in itertools.combinations(values_as_count_map.keys(), n):
            #print(subset)
            # Each subset should be a tuple / list of keys
            total_occurences = 0
            for key in subset:
                total_occurences += values_as_count_map[key]
            # print("Occurences: {}".format(total_occurences))
            
            # base case            
            how_far_off = abs(desired_drink_count - total_occurences)
            if len(top_n_rule_sets) < max_viable_combinations:
                top_n_rule_sets.append((subset, how_far_off))
                insertion_sort_tuple_by_second_value(top_n_rule_sets)
                continue
            
            if how_far_off < top_n_rule_sets[max_viable_combinations - 1][1]:
                print("Removing farther: {} for shorter: {}".format(top_n_rule_sets.pop()[1], how_far_off))
                top_n_rule_sets.append((subset, how_far_off))
                insertion_sort_tuple_by_second_value(top_n_rule_sets)
                continue

            # If we have a mega tie, don't want to lose precision...  fix this...
            if len(top_n_rule_sets) < equal_consideration_count and how_far_off == top_n_rule_sets[0][1]:
                top_n_rule_sets.append((subset, how_far_off))
                insertion_sort_tuple_by_second_value(top_n_rule_sets)


    print("Done chugging on combinations.. (total combinations: {}). Time to sort...".format(len(top_n_rule_sets)))
    return top_n_rule_sets

def get_longest_dryspell(list_of_events_seconds, movie_end_seconds):
    list_of_events_seconds.append(movie_end_seconds)
    list_of_events_seconds.sort()
    biggest_diff = 0
    for i, x in enumerate(list_of_events_seconds):
        previous_val = 0
        if i > 0:
            previous_val = list_of_events_seconds[i - 1]
        
        if x - previous_val > biggest_diff:
            biggest_diff = x - previous_val
    return biggest_diff


def format_and_print_ideal_n(mega_list, max_rules_to_choose_from):
    print("Variations:\n")
    for i in range(0, max_rules_to_choose_from):
        print("Rule set {}: ".format(i + 1))
        j = 1
        for rule in mega_list[i][0]:
            print("  ({}) {}".format(j, rule))
            j += 1
        # print("Rules: {}".format(mega_list[i][0]))
        print("Sips off target: {}".format(mega_list[i][2]))
        print("Longest dryspell in seconds: {}".format(mega_list[i][1]))
        print("\n------------------ \n")

def run_script(movie_csv, drinks, sips_per_drink, choices, equal_consideration_count, variation_rule_cap, prefer_more_rules, prefer_chaos):
    """
    Args:
        movie_csv(string): String file assumed to be in datasets dir
        drinks(int): Num desired drinks
        sips_per_drink(int): Sips per drink
        choices(int): Number of variation choices
        equal_consideration_count(int): If there are ties for hitting our drink target, how many do we consider in the first pass
        variation_rule_cap(int): Max rules combinations for one <variation>
        prefer_more_rules(bool): If true we look for more rules first, else we look for less
        prefer_chaos(bool): If true optimize for longest gap in satisfying rules. Else optimize for shortest gap
    """
    full_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datasets", movie_csv)
    raw_table_dict = get_movie_in_data_frame(full_filepath)
    # raw_table_dict = get_movie_in_data_frame(MOVIE_FILE_PATH)

    sips_for_me = drinks * sips_per_drink

    # map<string, list<int(seconds duration from start)>>
    
    # want to get the end time of the movie, given the last recorded rule.
    latest_rule = 0
    values_as_count = []
    for _, val in raw_table_dict.items():
        values_as_count.append(len(val))
        for dur in val:
            if dur > latest_rule:
                latest_rule = dur

    # plt.bar(raw_table_dict.keys(), values_as_count)
    # plt.show()

    # currently not actually N
    n_closest_list = get_closest_n_rule_combinations(raw_table_dict, sips_for_me, equal_consideration_count, variation_rule_cap, prefer_more_rules, choices)

    # Keep a list of tuples  [(string id list, longest dry spell)]
    n_closest_with_dryspell_tuple_list = list()

    # Get the closest 5 combinations of rules to my desired count
    print("Now to evaluate based on {} targets, what are the dryspell times...".format(len(n_closest_list)))
    for close_tuple in n_closest_list:
        list_of_appended_event_times = []
        for str_event_key in close_tuple[0]:
            list_of_appended_event_times += raw_table_dict[str_event_key]
        
        # Now check for largest dryspell
        n_closest_with_dryspell_tuple_list.append( ( close_tuple[0], get_longest_dryspell(list_of_appended_event_times, latest_rule), close_tuple[1]) )


    print("Done getting dryspells, now to sort and grab first {}".format(choices))
    insertion_sort_tuple_by_second_value(n_closest_with_dryspell_tuple_list, prefer_chaos)
    print("Done\n\n\n---------------------------------------------------")

    format_and_print_ideal_n(n_closest_with_dryspell_tuple_list, choices)

    rule_set_index = 0
    while (rule_set_index != -1):
        print("Which one do you choose? (Type the 'Rule Set' number).  Choose -1 to exit.")
        rule_set_index = int(input()) -1
        assert 0 <= rule_set_index < len(n_closest_with_dryspell_tuple_list)


        fig, ax = plt.subplots()
        x_axis = np.arange(0, latest_rule, 30)

        list_of_appended_event_times = []
        num_occurrences_before_time = 0 
        for event_key in n_closest_with_dryspell_tuple_list[rule_set_index][0]:
            list_of_appended_event_times += raw_table_dict[event_key]
        list_of_appended_event_times.sort()


        y_axis_list = []
        for timestamp in x_axis:        
            num_occurrences = 0 
            for event_time in list_of_appended_event_times:
                if event_time <= timestamp:
                    num_occurrences += 1
                else:
                    break
            y_axis_list.append(num_occurrences)

        y_axis = np.array(y_axis_list)
        ax.set_title('Movie: {}, Drinks: {}, Rules: {}'.format(movie_csv, drinks, len(n_closest_with_dryspell_tuple_list[rule_set_index][0])))
        ax.plot(y_axis, color='blue', label='Drinks over time')
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create your optimal drinking game experience for a movie!')
    parser.add_argument('--movie_csv', metavar='[MOVIE.csv]', type=str,
                        help='Name of file in DrinkingGames/datasets/')
    parser.add_argument('--drinks', nargs='?', const=1, type=int, default=6, help='Desired number of drinks')
    parser.add_argument('--sips_per_drink', nargs='?', const=1, type=int, default=15, help='Sips per drink (for calculation)')
    parser.add_argument('--choices', nargs='?', const=1, type=int, default=10, help='Number of variations to choose from')
    parser.add_argument('--equal_consideration_count', nargs='?', const=1, type=int, default=2000, help='If there are ties for the first stage of drink equality checks, how many should we consider. (Higher the number more compute but more diverse results)')
    parser.add_argument('--variation_rule_cap', nargs='?', const=1, type=int, default=6, help='Rule combination cap (recommend < 7 for performance)')
    parser.add_argument('--prefer_more_rules', action='store_true', help='If enabled, we look for as many rules as we can to fill the drink criteria first. (We wearch until we hit a cap of "equal_consideration_count"). Otherwise we search for the shortest first by default.')
    parser.add_argument('--prefer_chaos', action='store_true', help='If you opt in to "prefer_chaos", you will reverse sort on the second pass when selecting a rule set priority based on the longest gap between rules. This implicitly suggests your rule set comes all at once for a "chaotic" experience..')

    args = parser.parse_args()
    print(args)
    run_script(**vars(args))



# BUGS:
#  - After setting time (while paused) and trying to record, it doesn't update the actual time (uses the old running time)