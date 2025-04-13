"""
Calculates Glicko2 ratings and career stats for UFC fighters.
- Updates fighter ratings after each fight
- Computes probability of win and rating decay
- Summarizes career averages and strike percentages
- Outputs enriched fight and fighter datasets
"""

import math
import pandas as pd
import sys

totals_columns = ['kd', 'tot_str_lnd', 'tot_str_att', 'td_lnd', 'td_att', 'sub_att', 'rev', 
                  'ctrl', 'sig_str_lnd', 'sig_str_att', 'head_sig_str_lnd', 'head_sig_str_att', 
                  'body_sig_str_lnd', 'body_sig_str_att', 'leg_sig_str_lnd', 'leg_sig_str_att', 
                  'dist_sig_str_lnd', 'dist_sig_str_att', 'clch_sig_str_lnd', 'clch_sig_str_att', 
                  'gnd_sig_str_lnd', 'gnd_sig_str_att']

percents_columns = ['tot_str', 'td', 'sig_str', 'head_sig_str', 'body_sig_str', 'leg_sig_str',
                    'dist_sig_str', 'clch_sig_str', 'gnd_sig_str']

averages_columns = ['kd', 'tot_str_lnd', 'td_lnd', 'sub_att', 'rev', 'ctrl', 'sig_str_lnd', 
                    'head_sig_str_lnd', 'body_sig_str_lnd', 'leg_sig_str_lnd', 'dist_sig_str_lnd', 
                    'clch_sig_str_lnd', 'gnd_sig_str_lnd',]

career_columns = ['name', 'tot_str_pct', 'td_pct', 'sig_str_pct', 'head_sig_str_pct', 
                  'body_sig_str_pct', 'leg_sig_str_pct', 'dist_sig_str_pct', 'clch_sig_str_pct', 
                  'gnd_sig_str_pct', 'avg_kd', 'avg_tot_str_lnd', 'avg_td_lnd', 
                  'avg_sub_att', 'avg_rev', 'avg_ctrl', 'avg_sig_str_lnd','avg_head_sig_str_lnd', 
                  'avg_body_sig_str_lnd', 'avg_leg_sig_str_lnd', 'avg_dist_sig_str_lnd', 
                  'avg_clch_sig_str_lnd', 'avg_gnd_sig_str_lnd']

red_columns = ['red' , 'red_height', 'red_reach', 'red_stance']
blue_columns = ['blue' , 'blue_height', 'blue_reach', 'blue_stance']

# adapted from https://www.glicko.net/glicko/glicko2.pdf
# assumes every fight changes rating; does not have concept of rating period
def updateGlicko(r, rd, opp_r, opp_rd, v, result):
    # step 1: Set volatility contraint constant
    tau = 0.5 

    # step 2: convert fighter stats to glicko2 scale
    mu = (r - 1500)/173.7178
    phi = rd/173.7178
    opp_mu = (opp_r - 1500)/173.7178
    opp_phi = opp_rd/173.7178

    # step 3: compute estimated variance (nu)
    g = 1/math.sqrt(1 + (3*(opp_phi**2)/(math.pi**2)))
    E = 1/(1 + math.exp(-1*g*(mu - opp_mu)))
    nu = 1/((g**2) * E * (1 - E))

    # step 4: compute estimated change in rating
    delta = nu * g * (result - E)

    # step 5: compute new volatility (sigma)
    # step 5.1:
    def f(x):
        a = math.exp(x) * (delta**2 - phi**2 - nu - math.exp(x))
        b = 2 * ((phi**2 + nu + math.exp(x))**2)
        c = (x - math.log(v**2))/(tau**2)

        return (a/b) - c

    # step 5.2: initialize values for Illinois algorithm
    A = math.log(v**2)
    B = None
    if (delta**2 > phi**2 + nu): 
        B = math.log(delta**2 - phi**2 - nu)
    else:
        k = 1
        while (f(A - k*tau) < 0):
            k += 1
        
        B = A - k*tau

    # step 5.3
    f_A = f(A)
    f_B = f(B)

    # step 5.4: run Illinois algorithm
    epsilon = 0.000001 # convergence tolerance
    while (abs(B - A) > epsilon):
        C = A + ((A - B)*f_A)/(f_B - f_A)
        f_C = f(C)

        if (f_C * f_B <= 0):
            A = B
            f_A = f_B
        else:
            f_A /= 2

        B = C
        f_B = f_C

    sigma_p = math.exp(A/2) 

    # step 6:
    phi_star = math.sqrt(phi**2 + sigma_p**2)

    # step 7: 
    phi_p = 1/math.sqrt(1/(phi_star**2) + 1/nu)
    mu_p = mu + phi_p**2 * g * (result - E)

    # step 8: scale stats back to glicko
    new_r = 173.7178*mu_p + 1500
    new_rd = 173.7178*phi_p

    return new_r, new_rd, sigma_p

# Calculates probability that a fighter will beat their opponent
# Adapted from https://www.glicko.net/glicko/glicko.pdf
def expectedGlickoOutcome(r, rd, opp_r, opp_rd):
    q = math.log(10)/400
    g = 1/math.sqrt(1 + ((3*q**2) * (rd**2 + opp_rd**2)/(math.pi**2))) 
    exp = (-g*(r - opp_r))/400

    return 1/(1 + 10**exp)

# Decays fighters rd
def computeDecay(fighter):
    phi = fighter['rd']/173.7178
    phi_p = math.sqrt(phi**2 + fighter['volatility']**2)

    return 173.7178 * phi_p    

# Initializes and updates Glicko2 ratings across all fights
def computeGlicko(fights, fighters):
    # create glicko columns
    fighters[['rating', 'rd', 'volatility', 'last_fight']] = 0.0, 0.0, 0.0, None
    new_fight_cols = ['red_rating', 'red_rd', 'blue_rating', 'blue_rd', 'exp_red_outcome', 
                      'new_red_rating', 'new_blue_rating']
    fights[new_fight_cols] = 0.0
    
    start_date = pd.to_datetime(fights.iloc[0]['date'])
    end_date = start_date + pd.Timedelta(days=365)
    
    # Calculate and update glicko2 ratings from each fight for both fighters
    num_fights = len(fights)
    for i in range(0, num_fights):
        fight = fights.iloc[i]

        # Compute decay for fighters who haven't fought in last year once end_date has passed 
        if (pd.to_datetime(fight['date']) > end_date):
            inactive = (fighters['last_fight'] != None) & (pd.to_datetime(fighters['last_fight']) < start_date)
            fighters.loc[inactive, 'rd'] = fighters.apply(computeDecay, axis=1)

            start_date = end_date
            end_date += pd.Timedelta(days=365)

        # Get glicko stats for both fighters
        red = fight['red']
        blue = fight['blue']

        red_result = fight['red_result']
        blue_result = 1 - red_result

        red_r = fighters[fighters['name'] == red]['rating'].iloc[0]
        red_rd = fighters[fighters['name'] == red]['rd'].iloc[0]
        red_v = fighters[fighters['name'] == red]['volatility'].iloc[0]

        blue_r = fighters[fighters['name'] == blue]['rating'].iloc[0]
        blue_rd = fighters[fighters['name'] == blue]['rd'].iloc[0]
        blue_v = fighters[fighters['name'] == blue]['volatility'].iloc[0]

        # Set default values for fighters if it is their first fight
        if (red_r == 0):
            red_r, red_rd, red_v = 1500.0, 350.0, 0.06
        if (blue_r == 0):
            blue_r, blue_rd, blue_v = 1500.0, 350.0, 0.06

        # add glicko rating before fight to compute outcome odds
        fights.loc[i, ['red_rating', 'red_rd']] = float(red_r), float(red_rd)
        fights.loc[i, ['blue_rating', 'blue_rd']] = float(blue_r), float(blue_rd)

        fights.loc[i, 'exp_red_outcome'] = float(expectedGlickoOutcome(red_r, red_rd, blue_r, blue_rd))

        # compute new glicko ratings
        fighters.loc[fighters['name'] == red, ['rating', 'rd', 'volatility']] = [
            float(x) for x in updateGlicko(red_r, red_rd, blue_r, blue_rd, red_v, red_result)]
        fighters.loc[fighters['name'] == blue, ['rating', 'rd', 'volatility']] = [
            float(x) for x in updateGlicko(blue_r, blue_rd, red_r, red_rd, blue_v, blue_result)]

        # add new glicko rating to fight
        fights.loc[i, 'new_red_rating'] = float(fighters[fighters['name'] == red]['rating'].iloc[0])
        fights.loc[i, 'new_blue_rating'] = float(fighters[fighters['name'] == blue]['rating'].iloc[0])

        # Set last fight date
        fighters.loc[fighters['name'] == red, 'last_fight'] = fight['date']
        fighters.loc[fighters['name'] == blue, 'last_fight'] = fight['date']

    fighters = fighters.drop(['last_fight'], axis=1)

    return fights, fighters

def calculate_totals(df):
    # Sum total for all rounds
    for stat in totals_columns:
        df[f'red_sum_{stat}'] = df[[col for col in df.columns if f'red_{stat}' in col]].sum(axis=1)
        df[f'blue_sum_{stat}'] = df[[col for col in df.columns if f'blue_{stat}' in col]].sum(axis=1)

    return df

def calculate_percentages(df):
    # Calculates Percentages for stats with landed & attempts
    for stat in percents_columns:
        # For red stats
        df[f'red_{stat}_pct'] = df[f'red_sum_{stat}_lnd'] / df[f'red_sum_{stat}_att']
        # Set to 0 if division results in NaN or if sum_red_{stat}_att is 0
        df[f'red_{stat}_pct'] = df[f'red_{stat}_pct'].where(df[f'red_sum_{stat}_att'] != 0, 0)

        # For blue stats
        df[f'blue_{stat}_pct'] = df[f'blue_sum_{stat}_lnd'] / df[f'blue_sum_{stat}_att']
        # Set to 0 if division results in NaN or if avg_blue_{stat}_att is 0
        df[f'blue_{stat}_pct'] = df[f'blue_{stat}_pct'].where(df[f'blue_sum_{stat}_att'] != 0, 0)
    
    return df

def calculate_averages(df):
    # Calculate Career fight data averages for fighters
    for stat in averages_columns:
        df[f'red_avg_{stat}'] = df[f'red_sum_{stat}'] / df['round']
        df[f'blue_avg_{stat}'] = df[f'blue_sum_{stat}'] / df['round']
    return df

def calculate_career_stats(fight_data):
    red_stats = fight_data[[col for col in fight_data.columns if "red" in col]]
    blue_stats = fight_data[[col for col in fight_data.columns if "blue" in col]]
    red_stats = red_stats.drop(
        ['red_result', 'red_rating', 'red_rd', 'exp_red_outcome', 'new_red_rating'], 
        axis=1
    )
    blue_stats = blue_stats.drop(['blue_rating', 'blue_rd', 'new_blue_rating'], axis=1)

    red_stats.columns = career_columns
    blue_stats.columns = career_columns

    career_stats = pd.concat([red_stats, blue_stats], ignore_index=True)
    career_stats = career_stats.groupby('name').mean().reset_index()   

    return career_stats

# Bayesian smoothing average function to counter low fight counts
def calculate_smoothed_means(career_stats, fight_counts, smoothing_k=5):
    smoothed = career_stats.copy()
    stat_cols = career_columns[1:]
    
    global_means = career_stats[stat_cols].mean()

    for col in stat_cols:
        smoothed[col] = (
            fight_counts * career_stats[col] + smoothing_k * global_means[col]
        ) / (fight_counts + smoothing_k)
    
    return smoothed

def main(in_dir1, in_dir2, out_dir1, out_dir2):
    fight_data = pd.read_csv(in_dir1)
    fighters = pd.read_csv(in_dir2)

    # generate fight features
    fight_data = calculate_totals(fight_data)
    fight_data = calculate_percentages(fight_data)
    fight_data = calculate_averages(fight_data)

    # Drop unnecessary columns (i.e., r1_red_kd, r3_blue_tot_str_lnd, etc.)
    fight_data = fight_data.drop(fight_data.columns[range(4, 270)], axis=1)

    # Update fighter ratings after each fight using Glicko2 algorithm
    fight_data, fighters = computeGlicko(fight_data, fighters)

    career_stats = calculate_career_stats(fight_data)
    
    fight_counts = fight_data['red'].value_counts().add(
    fight_data['blue'].value_counts(), fill_value=0
    )
    fight_counts = fight_counts.reindex(career_stats['name']).fillna(0).values

    # Apply smoothing to counter low fight counts
    career_stats = calculate_smoothed_means(career_stats, fight_counts)

    # Merge career stats with fighters
    fighters = fighters.merge(career_stats, on='name')

    # Merge individual fighter stats with fight data
    fight_data = fight_data.merge(
        fighters[['name', 'height', 'reach', 'stance']].set_axis(red_columns, axis=1), 
        on='red' 
    )
    fight_data = fight_data.merge(
        fighters[['name', 'height', 'reach', 'stance']].set_axis(blue_columns, axis=1), 
        on='blue'
    )

    fight_data.to_csv(out_dir1, index=False)
    fighters.to_csv(out_dir2, index=False)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])