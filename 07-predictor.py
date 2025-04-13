"""
Predicts the outcome of a fight between two UFC fighters using a trained model.
- Loads a saved model and preprocessed fighter stats
- Reads two fighter names from a file
- Computes win probabilities based on fighter stats and Glicko ratings
- Outputs formatted win probabilities
"""
import joblib
import math
import pandas as pd
import sys

columns = ['red_tot_str_pct', 'blue_tot_str_pct', 'red_td_pct', 'blue_td_pct', 'red_sig_str_pct', 
           'blue_sig_str_pct', 'red_head_sig_str_pct', 'blue_head_sig_str_pct', 
           'red_body_sig_str_pct', 'blue_body_sig_str_pct', 'red_leg_sig_str_pct', 
           'blue_leg_sig_str_pct', 'red_dist_sig_str_pct', 'blue_dist_sig_str_pct', 
           'red_clch_sig_str_pct', 'blue_clch_sig_str_pct', 'red_gnd_sig_str_pct', 
           'blue_gnd_sig_str_pct', 'red_avg_kd', 'blue_avg_kd', 'red_avg_tot_str_lnd',
           'blue_avg_tot_str_lnd', 'red_avg_td_lnd', 'blue_avg_td_lnd', 'red_avg_sub_att', 
           'blue_avg_sub_att', 'red_avg_rev', 'blue_avg_rev', 'red_avg_ctrl', 'blue_avg_ctrl', 
           'red_avg_sig_str_lnd', 'blue_avg_sig_str_lnd', 'red_avg_head_sig_str_lnd',
           'blue_avg_head_sig_str_lnd', 'red_avg_body_sig_str_lnd', 'blue_avg_body_sig_str_lnd', 
           'red_avg_leg_sig_str_lnd', 'blue_avg_leg_sig_str_lnd', 'red_avg_dist_sig_str_lnd',
           'blue_avg_dist_sig_str_lnd', 'red_avg_clch_sig_str_lnd', 'blue_avg_clch_sig_str_lnd', 
           'red_avg_gnd_sig_str_lnd', 'blue_avg_gnd_sig_str_lnd', 'exp_red_outcome', 'red_height',
           'red_reach', 'red_stance', 'blue_height', 'blue_reach', 'blue_stance']

def expectedGlickoOutcome(r, rd, opp_r, opp_rd):
    # Calculates probability that a fighter will beat their opponent
    # Adapted from https://www.glicko.net/glicko/glicko.pdf
    q = math.log(10)/400
    g = 1/math.sqrt(1 + ((3*q**2) * (rd**2 + opp_rd**2)/(math.pi**2))) 
    exp = (-g*(r - opp_r))/400

    return 1/(1 + 10**exp)

def compute_win_prob(fighter1, fighter2, model):
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
            
    fighter_data['exp_red_outcome'] = expectedGlickoOutcome(
        fighter1['red_rating'].iloc[0], 
        fighter1['red_rd'].iloc[0], 
        fighter2['blue_rating'].iloc[0], 
        fighter2['blue_rd'].iloc[0]
    )

    fighter_data = fighter_data[columns]
    
    # Predict the class probabilities then return the probability of fighter1 winning
    return model.predict_proba(fighter_data)[0][1]

def main(model_path, fighter_data, matchup):
    # Load the model
    model = joblib.load(model_path)
    
    # Load the fighter data
    df = pd.read_csv(fighter_data)
    
    names = []

    # Read fighter names from input file (2 lines expected)
    with open(matchup, 'r') as file:
        names.extend([file.readline().strip(), file.readline().strip()])

    if len(names) != 2:
        print("Invalid number of fighters")
        return            
    
    # Verify both fighters are present in the dataset
    unrecognized = [name for name in names if name not in df['name'].values]

    # Print unrecognized names
    if unrecognized:
        print(f"Cannot find the following fighters: {', '.join(unrecognized)}")
        return

    # Get the row data for the fighters
    fighter1 = df[df['name'] == names[0]].iloc[0]
    fighter2 = df[df['name'] == names[1]].iloc[0]
                    
    # Calculate probability that fighter1 wins
    prob_f1 = compute_win_prob(fighter1, fighter2, model)
    prob_f2 = 1 - prob_f1

    # Print results
    max_len = max(len(names[0]), len(names[1]))

    print(f'Fighter{" " * (max_len-6)}| Chances of Winning')
    print(f'{"-" * (max_len+1)}+------------------')
    print(f'{names[0]}{" " * (max_len+1-len(names[0]))}| {prob_f1*100:.3f}%')
    print(f'{names[1]}{" " * (max_len+1-len(names[1]))}| {prob_f2*100:.3f}%')
            
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])