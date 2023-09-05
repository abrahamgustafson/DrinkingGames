import csv
import random
import matplotlib.pyplot as plt

# Load movie data from CSV file
def load_movie_data(filename):
    movie_data = {}
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row[0] not in movie_data:
                movie_data[row[0]] = []
            movie_data[row[0]].append(float(row[1]))
    return movie_data

# Generate drinking game rules based on movie data
def generate_rules(movie_data, num_drinks, sips_per_drink, prefer_even_distribution, rule_cap):
    # Get total movie duration
    movie_duration = max([max(movie_data[m]) for m in movie_data])

    # Calculate drink frequency per minute
    drink_frequency = num_drinks / movie_duration

    # Calculate number of rules
    num_rules = min(int(movie_duration / 2), rule_cap)

    # Determine rule times
    if prefer_even_distribution:
        rule_times = [i * movie_duration / num_rules for i in range(num_rules)]
    else:
        rule_times = []
        while len(rule_times) < num_rules:
            time = random.uniform(0, movie_duration)
            if time not in rule_times:
                rule_times.append(time)

    # Sort rule times
    rule_times = sorted(rule_times)

    # Create rule set
    rule_set = {}
    for i in range(num_rules):
        rule = "Rule " + str(i+1)
        rule_time = rule_times[i]
        drink_count = int(drink_frequency * rule_time)
        if drink_count == 0:
            drink_count = 1
        rule_set[rule] = {
            "time": rule_time,
            "drinks": drink_count * sips_per_drink
        }

    # Generate plot of rule set over time
    plt.figure(figsize=(10, 5))
    plt.title("Drinking Game Rules Over Time")
    plt.xlabel("Time (minutes)")
    plt.ylabel("Drink Count")
    plt.xlim([0, movie_duration])
    plt.ylim([0, num_drinks * sips_per_drink])
    plt.xticks(range(0, int(movie_duration)+1, int(movie_duration/10)))
    plt.yticks(range(0, int(num_drinks * sips_per_drink)+1, int((num_drinks * sips_per_drink)/10))))
    plt.grid()
    plt.plot([movie_data[m][0] for m in movie_data], [0 for m in movie_data], "o", markersize=5)
    for rule in rule_set:
        rule_time = rule_set[rule]["time"]
        drinks = rule_set[rule]["drinks"]
        plt.axvline(x=rule_time, color="red", linestyle="dashed", linewidth=1)
        plt.text(rule_time+0.5, drinks+1, rule, rotation=90, fontsize=8, verticalalignment="bottom")
    plt.show()

    return rule_set
