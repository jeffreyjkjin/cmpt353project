import math
import pandas as pd
import sys

# calculates new glicko rating of a fighter
# adapted from https://www.glicko.net/glicko/glicko2.pdf
def calculateGlicko(r, rd, opp_r, opp_rd, v, result):
    tau = 0.5 # volatility contraint constant

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


def main(in_dir1, in_dir2, out_dir1, out_dir2):
    fight_data = pd.read_csv(in_dir1)
    fighters = pd.read_csv(in_dir2)

    # Calculate Career fight data averages for fighters
    red_columns = [col for col in fight_data.columns if "red" in col]
    blue_columns = [col for col in fight_data.columns if "blue" in col]
    red_df = fight_data[red_columns].copy()
    red_df = red_df.drop('red_result', axis=1)
    blue_df = fight_data[blue_columns].copy()
    
    red_df.columns = ['Fighter', 'avg_kd', 'avg_tot_str_lnd', 'avg_tot_str_att', 'avg_td_lnd', 'avg_td_att', 
                    'avg_sub_att', 'avg_rev', 'avg_ctrl', 'avg_sig_str_lnd', 'avg_sig_str_att', 
                    'avg_head_sig_str_lnd', 'avg_head_sig_str_att', 'avg_body_sig_str_lnd', 
                    'avg_body_sig_str_att', 'avg_leg_sig_str_lnd', 'avg_leg_sig_str_att', 
                    'avg_dist_sig_str_lnd', 'avg_dist_sig_str_att', 'avg_clch_sig_str_lnd', 
                    'avg_clch_sig_str_att', 'avg_gnd_sig_str_lnd', 'avg_gnd_sig_str_att', 
                    'tot_str_per', 'td_per', 'sig_str_per', 'head_sig_str_per', 'body_sig_str_per', 
                    'leg_sig_str_per', 'dist_sig_str_per', 'clch_sig_str_per', 'gnd_sig_str_per']
    
    blue_df.columns = ['Fighter', 'avg_kd', 'avg_tot_str_lnd', 'avg_tot_str_att', 'avg_td_lnd', 'avg_td_att', 
                    'avg_sub_att', 'avg_rev', 'avg_ctrl', 'avg_sig_str_lnd', 'avg_sig_str_att', 
                    'avg_head_sig_str_lnd', 'avg_head_sig_str_att', 'avg_body_sig_str_lnd', 
                    'avg_body_sig_str_att', 'avg_leg_sig_str_lnd', 'avg_leg_sig_str_att', 
                    'avg_dist_sig_str_lnd', 'avg_dist_sig_str_att', 'avg_clch_sig_str_lnd', 
                    'avg_clch_sig_str_att', 'avg_gnd_sig_str_lnd', 'avg_gnd_sig_str_att', 
                    'tot_str_per', 'td_per', 'sig_str_per', 'head_sig_str_per', 'body_sig_str_per', 
                    'leg_sig_str_per', 'dist_sig_str_per', 'clch_sig_str_per', 'gnd_sig_str_per']
    
    career_fighter_stats_df = pd.concat([red_df, blue_df], ignore_index=True)
    career_fighter_stats_df = career_fighter_stats_df.groupby('Fighter').mean().reset_index()


    # TODO: create heuristic to determine whether a fighter is a grappler or striker

    # set default glicko values
    fighters['rating'] = 1500
    fighters['rd'] = 350
    fighters['volatility'] = 0.06
    
    # calculate and update glicko2 ratings from each fight for both fighters
    for _, fight in fight_data[::-1].iterrows():
        # get glicko stats for both fighters
        red = fight['red']
        blue = fight['blue']

        red_result = fight['red_result'] == 'W'
        blue_result = fight['blue_result'] == 'W'

        red_r = fighters[fighters['name'] == red]['rating'].iloc[0]
        red_rd = fighters[fighters['name'] == red]['rd'].iloc[0]
        red_v = fighters[fighters['name'] == red]['volatility'].iloc[0]

        blue_r = fighters[fighters['name'] == blue]['rating'].iloc[0]
        blue_rd = fighters[fighters['name'] == blue]['rd'].iloc[0]
        blue_v = fighters[fighters['name'] == blue]['volatility'].iloc[0]

        # compute new glicko ratings
        fighters.loc[fighters['name'] == red, ['rating', 'rd', 'volatility']] = calculateGlicko(
            red_r, red_rd, blue_r, blue_rd, red_v, red_result
        )

        fighters.loc[fighters['name'] == blue, ['rating', 'rd', 'volatility']] = calculateGlicko(
            blue_r, blue_rd, red_r, red_rd, blue_v, blue_result
        )

    fighters.to_csv(out_dir2, index=False)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])