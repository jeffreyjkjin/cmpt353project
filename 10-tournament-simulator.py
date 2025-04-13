"""
Simulates a single-elimination UFC-style tournament using a trained predictive model.
- Computes pairwise win probabilities between fighters
- Simulates multiple tournaments
- Tracks how often each fighter reaches each round
- Outputs results as win probability percentages
"""

import math
import random
import joblib
import pandas as pd
import sys

from itertools import combinations

predictor = __import__('07-predictor')

def simulate_matchup(fighter1, fighter2, prob_map):
    """Simulate a single matchup between two fighters based on the probability map."""
    prob_fighter1 = prob_map.get((fighter1, fighter2), prob_map.get((fighter2, fighter1), 0.5))  # Default 0.5 if no entry exists
    return fighter1 if random.random() < prob_fighter1 else fighter2

def generate_round_names(rounds):
    """Generate dynamic round names based on the number of fighters in the tournament."""
    round_names = []

    # Special case: For 1 round, use "Chance of Winning label"
    if rounds == 1:
        return ["Chance of Winning"]
    
    # For tournaments with 2 or more rounds, add certain pre-determined labels
    if rounds >= 2:
        round_names.append("win_tourney")
        round_names.append("finals")
    if rounds >= 3:
        round_names.append("qf")
    if rounds >= 4:
        round_names.append("sf")

    # Generate dynamic "Reach Round of X" names for tournaments with 5 or more rounds
    for r in range(5, rounds + 1):
        round_size = 2 ** (r - 1)
        round_names.append(f"reach_r_{round_size}")

    return round_names

def simulate_tournament(prob_map, fighters, num_simulations):
    """Simulate a tournament and count the number of times each fighter reaches a certain milestone."""
    rounds = int(math.log2(len(fighters)))
    round_names = generate_round_names(rounds)

    counts = {fighter: {label: 0 for label in round_names} for fighter in fighters}

    for _ in range(num_simulations):
        # Start simulation for a tournament
        bracket = fighters[:]

        for round_num in range(rounds):
            next_round = []
            # Track which round the winner reaches
            label = round_names[rounds - round_num - 1]
            for i in range(0, len(bracket), 2):
                f1, f2 = bracket[i], bracket[-1 - i]

                # Simulate matchup and advance winner
                winner = simulate_matchup(f1, f2, prob_map)
                next_round.append(winner)
                counts[winner][label] += 1

            bracket = next_round

    return counts

def write_output(counts, output, num_sims):
    """Write the simulation results to a file."""
    # Convert counts to percentage strings with 3 decimal places
    results = {}
    for fighter, outcomes in counts.items():
        results[fighter] = {
            label: round(count / num_sims, 4) for label, count in outcomes.items()
        }

    # Get all unique labels
    all_labels = sorted({label for fighter_stats in results.values() for label in fighter_stats})

    # Build header
    header = ["fighter"] + all_labels

    # Build rows of fighter stats for CSV output
    rows = []
    for fighter in sorted(results.keys()):
        row = [fighter]
        for label in all_labels:
            row.append(results[fighter].get(label, "0.000%"))
        rows.append(row)

    # Turn into dataframe and save
    df = pd.DataFrame(rows, columns=header)
    df = df.sort_values(by='win_tourney', ascending=False)

    df.to_csv(output, index=False)

def main(model, fighters, tournament, results, num_sims):
    # Check that the number of simulations is > 0
    if num_sims <= 0:
        print("Number of simulations must be greater than 0.")
        return
    
    # Load the model
    model = joblib.load(model)
    
    # Load the fighter data
    df = pd.read_csv(fighters)

    # Initialize the names list
    names = []

    # Open the file and read line by line
    with open(tournament, 'r') as file:
        for line in file:
            cleaned_line = line.strip()
            if cleaned_line:  # Only add non-empty lines
                names.append(cleaned_line)
                
    # Check if the number of fighters is a power of 2 and more than 2 players
    if len(names) < 4:
        print(f"Invalid number of fighters")
        return

    # Collect recognized and unrecognized names
    unrecognized = [name for name in names if name not in df['name'].values]

    # Print unrecognized names
    if unrecognized:
        print(f"Cannot find the following fighters: {', '.join(unrecognized)}")
        return

    # Filter rows based on recognized names
    fighters = df[df['name'].isin(names)].reset_index()

    # Create a dictionary to store matchup probabilities
    matchups_probs = {}

    # Generate all possible combinations of fighters
    for fighter1, fighter2 in combinations(fighters['name'], 2):
        # Get the row data for the fighters
        fighter1_data = fighters[fighters['name'] == fighter1].iloc[0]
        fighter2_data = fighters[fighters['name'] == fighter2].iloc[0]
                    
        # Predict the winner
        prob_fighter1 = predictor.compute_win_prob(fighter1_data, fighter2_data, model)
                    
        # Store the probabilities in the dictionary (fighter1 vs fighter2)
        matchups_probs[(fighter1, fighter2)] = prob_fighter1

    # Run tournament simulations and track round advancement for each fighter
    counts = simulate_tournament(matchups_probs, fighters['name'].tolist(), num_sims)

    write_output(counts, results, num_sims)  

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]))