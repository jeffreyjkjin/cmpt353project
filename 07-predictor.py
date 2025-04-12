import sys
import os
import random
import pandas as pd
import joblib
import math
from itertools import combinations

def compute_win_prob(fighter1, fighter2, model, column_list, scaler):
    """Returns the probability of fighter 1 winning"""
    fighter1 = fighter1.to_frame().T
    fighter2 = fighter2.to_frame().T
    
    # Add prefix to columns
    fighter1 = fighter1.add_prefix('red_')
    fighter2 = fighter2.add_prefix('blue_')
    
    fighter1.reset_index(drop=True, inplace=True)
    fighter2.reset_index(drop=True, inplace=True)
    
    # Concatenate the two fighters into a single DataFrame
    fighter_data = pd.concat([fighter1, fighter2], axis=1)
    
    fighter_data = fighter_data[column_list]
    
    # Scale the data
    if scaler is not None:
        fighter_data = scaler.transform(fighter_data)
        # Convert back to DataFrame to keep the column names
        fighter_data = pd.DataFrame(fighter_data, columns=column_list)
    
    # Predict the class probabilities then return the probability of fighter1 winning
    return model.predict_proba(fighter_data)[0][1]


def generate_round_names(rounds):
    """Generate dynamic round names based on the number of fighters in the tournament."""
    round_names = []

    # Special case: For 1 round, use "Chance of Winning label"
    if rounds == 1:
        return ["Chance of Winning"]
    
    # For tournaments with 2 or more rounds, add certain pre-determined labels
    if rounds >= 2:
        round_names.append("Win Tournament")
        round_names.append("Reach Finals")
    if rounds >= 3:
        round_names.append("Reach Quarterfinals")
    if rounds >= 4:
        round_names.append("Reach Semifinals")

    # Generate dynamic "Reach Round of X" names for tournaments with 5 or more rounds
    for r in range(5, rounds + 1):
        round_size = 2 ** (r - 1)
        round_names.append(f"Reach Round of {round_size}")

    return round_names

def simulate_matchup(fighter1, fighter2, prob_map):
    """Simulate a single matchup between two fighters based on the probability map."""
    prob_fighter1 = prob_map.get((fighter1, fighter2), prob_map.get((fighter2, fighter1), 0.5))  # Default 0.5 if no entry exists
    return fighter1 if random.random() < prob_fighter1 else fighter2

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
            label = round_names[rounds - round_num - 1]
            for i in range(0, len(bracket), 2):
                f1, f2 = bracket[i], bracket[i + 1]

                # Simulate matchup and advance winner
                winner = simulate_matchup(f1, f2, prob_map)
                next_round.append(winner)
                counts[winner][label] += 1

            bracket = next_round

    return counts

def write_output(counts, output_path, num_simulations):
    """Write the simulation results to a file."""
    # Convert counts to percentage strings with 3 decimal places
    results = {}
    for fighter, outcomes in counts.items():
        results[fighter] = {
            label: f"{(count / num_simulations * 100):.3f}%" for label, count in outcomes.items()
        }

    # Get all unique labels
    all_labels = sorted({label for fighter_stats in results.values() for label in fighter_stats})

    # Build header
    header = ["Fighter"] + all_labels

    # Create all rows
    rows = []
    for fighter in sorted(results.keys()):
        row = [fighter]
        for label in all_labels:
            row.append(results[fighter].get(label, "0.000%"))
        rows.append(row)

    # Determine column widths
    col_widths = [max(len(str(cell)) for cell in col) for col in zip(*([header] + rows))]

    # Construct formatted output lines
    lines = []
    header_line = " | ".join(f"{cell:<{col_widths[i]}}" for i, cell in enumerate(header))
    separator = "-+-".join("-" * col_widths[i] for i in range(len(header)))
    lines.append(header_line)
    lines.append(separator)
    for row in rows:
        lines.append(" | ".join(f"{cell:<{col_widths[i]}}" for i, cell in enumerate(row)))

    # Write to file
    with open(output_path, 'w') as f:
        for line in lines:
            f.write(line + "\n")


def main(model_path, fighter_data, input_dir, output_dir, num_simulations):
    # Check that the number of simulations is > 0
    if num_simulations <= 0:
        print("Number of simulations must be greater than 0.")
        return
    
    # Load the model
    model, scaler, column_list = joblib.load(model_path)
    
    # Load the fighter data
    df = pd.read_csv(fighter_data)
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Input directory does not exist: {input_dir}")
        return
    
    # Check if output directory exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Walk through the directory recursively
    for root, dirs, files in os.walk(input_dir):
        # Create the mirrored path for the output directory
        mirrored_root = root.replace(input_dir, output_dir)
        
        # Ensure the mirrored directory exists
        if not os.path.exists(mirrored_root):
            os.makedirs(mirrored_root)
        
        # Loop through all the files in the current directory
        for filename in files:
            input_path = os.path.join(root, filename)
            
            # Only process text files
            if not filename.endswith('.txt'):
                print(f"Skipping non-txt file: {filename}")
                continue

            try:
                # Initialize the names list
                names = []

                # Open the file and read line by line
                with open(input_path, 'r') as file:
                    for line in file:
                        cleaned_line = line.strip()
                        if cleaned_line:  # Only add non-empty lines
                            names.append(cleaned_line)
                
                # Check if the number of fighters is a power of 2 and more than 2 players
                if len(names) < 2 or (len(names) & (len(names) - 1)) != 0:
                    print(f"Skipping file: {filename} - Invalid number of fighters")
                    continue

                # Collect recognized and unrecognized names
                recognized_names = [name for name in names if name in df['name'].values]
                unrecognized_names = [name for name in names if name not in df['name'].values]

                # Print unrecognized names
                if unrecognized_names:
                    print(f"Cannot find the following fighters in {filename}: {', '.join(unrecognized_names)}")
                    continue

                # Filter rows based on recognized names
                fighters = df[[name in recognized_names for name in df['name']]]
                fighters = df.set_index('name').loc[recognized_names].reset_index()

                # Create a dictionary to store matchup probabilities
                matchups_probs = {}

                # Generate all possible combinations of fighters
                for fighter1, fighter2 in combinations(fighters['name'], 2):
                    # Get the row data for the fighters
                    fighter1_data = fighters[fighters['name'] == fighter1].iloc[0]
                    fighter2_data = fighters[fighters['name'] == fighter2].iloc[0]
                    
                    # Predict the winner
                    prob_fighter1 = compute_win_prob(fighter1_data, fighter2_data, model, column_list, scaler)
                    
                    # Store the probabilities in the dictionary (fighter1 vs fighter2)
                    matchups_probs[(fighter1, fighter2)] = prob_fighter1
                
                if fighters.shape[0] == 2:
                    # Just use calculated probability for counts without simulating
                    fighter1 = fighters['name'][0]
                    fighter2 = fighters['name'][1]
                    
                    prob_f1 = matchups_probs[(fighter1, fighter2)]
                    prob_f2 = 1 - prob_f1

                    # Multiply by num_simulations to match simulated structure (counts, not probabilities)
                    counts = {
                        fighter1: {'Chance of Winning': int(round(prob_f1 * num_simulations))},
                        fighter2: {'Chance of Winning': int(round(prob_f2 * num_simulations))}
                    }
                else:
                    # Simulate the tournament
                    counts = simulate_tournament(matchups_probs, fighters['name'].tolist(), num_simulations)
                    
                # Write the output to the mirrored directory
                output_path = os.path.join(mirrored_root, filename)
                write_output(counts, output_path, num_simulations)
                        
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                continue
            
if __name__ == '__main__':
    """
    Usage: python 07-predictor.py <model_path> <fighter_data> <input_path> <output_path>
    """
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]))