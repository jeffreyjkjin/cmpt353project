import pandas as pd
import sys
import re

def main(in_dir, out_dir):
    df_temp = pd.read_csv(in_dir)
    df = df_temp.copy()

    # Function to filter out proper fight formats (2, 3, or 5 rounds)
    def is_valid_round_format(value):
        return bool(re.match(r"^\d+ Rnd(?: \(\d+-\d+(?:-\d+)?\))?$", str(value).strip()))

    # Filter dataset
    df = df[df['format'].apply(is_valid_round_format)]

    # Convert 'time' to seconds
    def convert_time_to_seconds(time_str):
        minutes, seconds = map(int, time_str.split(":"))
        return minutes * 60 + seconds

    # Calculate the number of rounds
    def calculate_rounds(row):
        round_number = int(row['round'])
        time_in_seconds = convert_time_to_seconds(row['time'])
        return (round_number - 1) + (time_in_seconds / 300)

    df['total_rounds'] = df.apply(calculate_rounds, axis=1)
    
    # Fill on empty entries with 0
    df.infer_objects(copy=False)

    # Convert fight stats to numeric
    stats_columns = [
        'kd', 'tot_str_lnd', 'tot_str_att', 'td_lnd', 'td_att', 'sub_att', 'rev', 'ctrl',
        'sig_str_lnd', 'sig_str_att', 'head_sig_str_lnd', 'head_sig_str_att', 'body_sig_str_lnd',
        'body_sig_str_att', 'leg_sig_str_lnd', 'leg_sig_str_att', 'dist_sig_str_lnd', 'dist_sig_str_att',
        'clch_sig_str_lnd', 'clch_sig_str_att', 'gnd_sig_str_lnd', 'gnd_sig_str_att'
    ]

    for round in range(1, 6):  # Loop through rounds 1-5
        for stat in stats_columns:
            df[f'r{round}_red_{stat}'] = pd.to_numeric(df[f'r{round}_red_{stat}'], errors='coerce').fillna(0)
            df[f'r{round}_blue_{stat}'] = pd.to_numeric(df[f'r{round}_blue_{stat}'], errors='coerce').fillna(0)

    new_rows = []
    i = 0
    while i < len(df):
        total_rounds = df.iloc[i]['total_rounds']
        
        # Red fighter stats
        red_fighter_stats = {
            'fighter_name': df.iloc[i]['red']
        }
        for stat in stats_columns:
            red_fighter_stats[f'avg_{stat}'] = sum(df.iloc[i][f'r{round}_red_{stat}'] for round in range(1, 6)) / total_rounds
        
        new_rows.append(red_fighter_stats)

        # Blue fighter stats
        blue_fighter_stats = {
            'fighter_name': df.iloc[i]['blue']
        }
        for stat in stats_columns:
            blue_fighter_stats[f'avg_{stat}'] = sum(df.iloc[i][f'r{round}_blue_{stat}'] for round in range(1, 6)) / total_rounds
        
        new_rows.append(blue_fighter_stats)

        i += 1

    # Create and save the new DataFrame
    new_df = pd.DataFrame(new_rows)

    # Average Fighter stats across multiple fights
    new_df = new_df.groupby('fighter_name', as_index=False).mean()
    new_df.to_csv(out_dir, index=False)

    # df of fight to be fighters and result
    # min_fight_stat = ['red','blue','red_result']
    # new_fight_df = df_temp[min_fight_stat]
    # new_fight_df = new_fight_df[(new_fight_df['red_result'] == 'L') | (new_fight_df['red_result'] == 'W')]

    # def convert_result(result):
    #     if(result == 'W'):
    #         return 0
    #     return 1
    # new_fight_df['red_result'] = new_fight_df['red_result'].apply(convert_result)

    # print(new_fight_df)



if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
