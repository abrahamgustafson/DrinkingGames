import argparse
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import itertools
import time

TIME_COL_ID = 'Time sequence'
RULE_COL_ID = 'Rule'
ID_COL_ID = 'id'
DEBUG_ENABLED = True


ACTION_MAP = {
    'help': "Help me out man!",
    'save': 'Save state',
    'pause': 'Pause / Play',
    'quit': 'Quit the recording',
    'add': "Add new rule, following prompt will be a string field to input the name of the rule",
    'records': "Print out all record keys (as mapped currently to rules)",
    'rules': "Print out all thet existing rules in order (and print ID's and keys for recording)",
    'undo': "Undo the last update",
    'time': "Print out the current time of the movie",
    'settime': "Set the time to something in the format  [x:xx:xx]",
    'freeadd': "Freely add to a rule and write out the desired time",
}

RECORD_KEYS = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '=', 
    'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',
    'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';',
    'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/',
    '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', 
    '20', '21', '22', '23', '24', '25', '26', '27', '28', '29'
]


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
                print("row rule index: {},  row occurence index: {}".format(rule_index, occcurence_index))
                continue
            
            # Base case, ignore row if it has no rule or occurences
            if DEBUG_ENABLED:
                print("Row object len: {}, obj: [{}]".format(len(row), row))
                # print("row rule index: {},  row occurence index: {}".format(rule_index, occcurence_index))
            if len(row) < 1:
                print("Something is likely wrong with parse... row: {}".format(row))
            # elif len(row) < 2:
            #     filtered_occurence_map[row[rule_index]] = []
            else:
                # if len(row[rule_index]) != 0 and len(row[occcurence_index]) != 0:
                if len(row[rule_index]) != 0:
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

def print_commands():
    print("--------- Commands ---------")
    for key, val in ACTION_MAP.items():
        print(" - [{}] : [{}]".format(key, val))
    
    print("--------- -------- ---------")
    
def add_record_association(rule_key, index, recording_dict):
    """
        Args:
            rule_key(string): key
            index(int): index of rule to add (eg what rull num is this)
            recording_dict(dict): Map of record key -> rule key reference / output
    """
    if (index >= len(RECORD_KEYS)):
        print("Cannot make new rule!!! index too high: {}".format(index))
        return
    
    recording_dict[RECORD_KEYS[index]] = rule_key

def get_input_command():
    """Prompt the user for input"""
    return input("Enter command: ").strip()

def write_out_rule_dict(rule_dict, full_filepath):
    """
    Args:
        rule_dict:  map<rule_key, list[seconds_from_start]>
        full_filepath:  full path to CSV, overwrite...
    """
    print("Saving file out to CSV...")
    csv_columns = [RULE_COL_ID, TIME_COL_ID]
#     TIME_COL_ID = 'Time sequence'
# RULE_COL_ID = 'Rule'
# csv_columns = ['No','Name','Country']
# dict_data = [
# {'No': 1, 'Name': 'Alex', 'Country': 'India'},
    try:
        with open(full_filepath, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()

            for key, time_list in rule_dict.items():
                row_as_dict = dict()
                row_as_dict[RULE_COL_ID] = key
                row_as_dict[TIME_COL_ID] = ''

                for t_seconds in time_list:
                    time_str = time.strftime('%H:%M:%S', time.gmtime(t_seconds))
                    row_as_dict[TIME_COL_ID] += time_str
                    row_as_dict[TIME_COL_ID] += "\n"

                writer.writerow(row_as_dict)
    except IOError:
        print("I/O error")

def print_records(recording_dict):
    print("--------------- Record Keys ----------------")
    for key, rule in recording_dict.items():
        print(' - {}: [{}]'.format(key, rule))
    print("--------------- ----------- ----------------")

def run_script(movie_csv):
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
    # raw_table_dict = get_movie_in_data_frame(full_filepath)
    # # raw_table_dict = get_movie_in_data_frame(MOVIE_FILE_PATH)

    # map<rule_key, list[seconds_from_start]>
    rule_dict = dict()

    # map<recorder_string, rule_key>
    recording_dict = dict()


    # Pick up from where we left off if we can.
    if (os.path.exists(full_filepath)):
        rule_dict = get_movie_in_data_frame(full_filepath)
        print("Loaded previous rules, count: {}".format(len(rule_dict.keys())))
    
    print("Loading existing rules into record keys..")
    for count, rule_key in enumerate(rule_dict.keys()):
        add_record_association(rule_key, count, recording_dict)

    duration_into_movie_s = 0
    time_of_start = 0
    is_paused = True

    last_rule_key_added = ''

    print('\n')
    print_commands()

    read_input = get_input_command()
    while(read_input != 'quit'):
        if read_input not in recording_dict.keys() and read_input not in ACTION_MAP.keys():
            print("[{}] is not a valid key, type: 'help' for help.".format(read_input))
            read_input = get_input_command()
            continue

        if read_input in recording_dict.keys():
            if time_of_start < 0:
                print("Can't record a record until the timer is started.")
                read_input = get_input_command()
                continue

            if is_paused:
                rule_dict[recording_dict[read_input]].append(duration_into_movie_s)
            else:
                duration_as_of_now = int(time.time() - time_of_start)
                rule_dict[recording_dict[read_input]].append(duration_as_of_now)
            last_rule_key_added = recording_dict[read_input]
            
            print_records(recording_dict)
            read_input = get_input_command()
            continue
        try:           
            # Implied to exist in ACTION_MAP
            if read_input == 'help':
                print_commands()
            if read_input == 'save':
                write_out_rule_dict(rule_dict, full_filepath)
            if read_input == 'pause':
                if is_paused:
                    if time_of_start == 0:
                        print("Time to start this shit... May the force be with you.")
                        time_of_start = time.time()
                    else:
                        # implies we are resuming, not outright starting.
                        print("Resuming.")
                        time_of_start = time.time() - duration_into_movie_s
                    is_paused = False
                else:
                    # Else we want to pause
                    duration_into_movie_s = int(time.time() - time_of_start)
                    nice_time_string = time.strftime('%H:%M:%S', time.gmtime(duration_into_movie_s))
                    print("Pausing at {} seconds into the movie.  [{}].".format(duration_into_movie_s, nice_time_string))
                    is_paused = True
            if read_input == 'quit':
                print("Are you sure you want to quit? Hit 'yes'  to confirm.")
                confirmation = get_input_command()
                if confirmation == 'yes':
                    break
                else:
                    print("Roger that, going to continue then...")
            if read_input == 'add':
                str_name = input("Enter new rule: ").strip()
                if (str_name in rule_dict.keys()):
                    print("Can't add this rule, it already exists!")
                else:
                    rule_dict[str_name] = list()
                    add_record_association(str_name, len(rule_dict.keys()) - 1, recording_dict)
            if read_input == 'rules':
                print("------------------ Rules -----------------")
                for rule_key, occurences in rule_dict.items():
                    print(" - [{}]: {}".format(rule_key, occurences))
                print("------------------ ----- -----------------")
            if read_input == 'undo':
                if last_rule_key_added not in rule_dict.keys():
                    print("Can't undo the last record, since there is no last record.")
                else:
                    rule_dict[last_rule_key_added].pop()
                    print("Removed last item from rule: [{}].  Don't remove again...".format(last_rule_key_added))
            if read_input == 'time':
                print("Is paused: {}".format(is_paused))
                if time_of_start == 0:
                    print("0")
                else:
                    if not is_paused:
                        duration_into_movie_s = int(time.time() - time_of_start)

                    nice_time_string = time.strftime('%H:%M:%S', time.gmtime(duration_into_movie_s))
                    print(nice_time_string)
            if read_input == "settime":
                try:
                    str_time = input("Enter a time to set in the format:    hh:mm:ss ").strip()
                    date_time = datetime.strptime(str_time.strip(), "%H:%M:%S")
                    a_timedelta = date_time - datetime(1900, 1, 1)
                    duration_into_movie_s = a_timedelta.total_seconds()
                except:
                    print("Failed to set time, didn't fit format...")
            if read_input == "freeadd":
                try:
                    str_record_key = input("Enter a record key: ").strip()
                    str_time = input("Enter a time to record an event in the format:    hh:mm:ss ").strip()
                    date_time = datetime.strptime(str_time.strip(), "%H:%M:%S")
                    a_timedelta = date_time - datetime(1900, 1, 1)
                    duration_into_movie_s = a_timedelta.total_seconds()
                    
                    rule_dict[recording_dict[str_record_key]].append(duration_into_movie_s)
                    last_rule_key_added = recording_dict[str_record_key]
                    print("successfully added at: {} seconds".format(duration_into_movie_s))
                except:
                    print("Failed to free add")
            if read_input == "records":
                print_records(recording_dict)
        except:
            print("Caught an error, whoops, try again?")
        finally:
        # else:
        #     print("[{}] is not a valid key, type: 'help' for help.".format(read_input))

        # print('test - to prompt again')
            read_input = get_input_command()
            continue
    # map<string, list<int(seconds duration from start)>>
    
#     'help': "Help me out man!",
#     'save': 'Save state',
#     'pause': 'Pause / Play',
#     'quit': 'Quit the recording',
#     'add': "Add new rule, following prompt will be a string field to input the name of the rule",
#     'rules': "Print out all thet existing rules in order (and print ID's and keys for recording)",
#     'undo': "Undo the last update",
#     'time': "Print out the current time of the movie",
#     'settime': "Set the time to something in the format  [x:xx:xx]",
#     'freeadd': "Freely add to a rule and write out the desired time",
# }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create your optimal drinking game experience for a movie!')
    parser.add_argument('--movie_csv', metavar='[MOVIE.csv]', type=str,
                        help='Name of file in DrinkingGames/datasets/')
    args = parser.parse_args()
    print(args)
    run_script(**vars(args))
