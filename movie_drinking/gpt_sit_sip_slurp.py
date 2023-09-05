import csv
import random
from datetime import datetime, timedelta

# Load movie data from CSV file
def load_data(filename):
    data = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            timestamp = datetime.strptime(row['time'], '%H:%M:%S')
            rule = row['rule']
            count = int(row.get('count', 1))  # default to 1 if count column not present
            data.append((timestamp, rule, count))
    return data

# Generate drinking game rules based on movie data
def generate_rules(data, num_drinks, sips_per_drink, prefer_chaos=False, rule_cap=15):
    total_sips = num_drinks * sips_per_drink
    rule_weights = []
    for timestamp, rule, count in data:
        if count > 0:
            weight = (total_sips / count) ** (1.0 if prefer_chaos else -1.0)
            rule_weights.append((rule, weight))
    rule_weights.sort(key=lambda x: x[1], reverse=True)
    rule_weights = rule_weights[:rule_cap]
    total_weight = sum(weight for _, weight in rule_weights)
    rules = []
    for rule, weight in rule_weights:
        num_sips = int(round((weight / total_weight) * total_sips))
        rules.append((rule, num_sips))
        total_sips -= num_sips
        total_weight -= weight
    # Distribute any remaining sips randomly
    random.shuffle(rules)
    for i in range(total_sips):
        rule, num_sips = rules[i % len(rules)]
        rules[i % len(rules)] = (rule, num_sips + 1)
    return [(rule, num_sips, timedelta(seconds=0)) for rule, num_sips in rules]

# Save drinking game rules to CSV file
def save_rules(filename, rules):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['rule', 'num_sips', 'timestamp'])
        timestamp = timedelta(seconds=0)
        for rule, num_sips, duration in rules:
            writer.writerow([rule, num_sips, str(timestamp)])
            timestamp += duration

# Example usage
if __name__ == '__main__':
    movie_data = load_data('C:\projects\DrinkingGames\datasets\shrek_2_gpt.csv')
    rules = generate_rules(movie_data, num_drinks=4, sips_per_drink=5, prefer_chaos=True, rule_cap=10)
    save_rules('game_rules.csv', rules)
