import pandas as pd
import sys
import re

def standardize_format(fight_format):
    if 'No Time Limit' in fight_format:
        return '1 Rnd + 0OT (10)'
    elif 'nd + OT (5-5-5-5)' in fight_format:
        return '3 Rnd + 1OT (5-5-5-5)'
    elif 'nd + 2OT (15-3-3)' in fight_format:
        return '1 Rnd + 2OT (15-3-3)'
    elif 'nd + 2OT (24-3-3)' in fight_format:
        return '1 Rnd + 2OT (24-3-3)'
    
    # Match general format and capture rounds and overtime parts
    match = re.match(r'(\d+|nd) Rnd(?: \+ OT)? \((.*)\)', fight_format)
    
    if match:
        rounds = match.group(1)
        time_str = match.group(2)
        
        # Handle OT (Overtime)
        ot_match = re.search(r'(\d+)OT', fight_format)
        if ot_match:
            ot = ot_match.group(1)
        else:
            ot = 0
        
        # Convert to standard format: "# RND + #OT (#-#-#-#...)"
        return f"{rounds} Rnd + {ot}OT ({time_str})"
    
    # Return original if no match is found
    return fight_format

def standardize_result(result):
    if (result == 'W'):
        return 1
    elif (result == 'L'):
        return 0
    elif (result == 'D'):
        return 0.5


def calculate_fight_time(row):
    # Extract round information from the format
    match = re.match(r'(\d+) Rnd \+ (\d+)OT \((.*?)\)', row['format'])
    
    if match:
        rounds = int(match.group(1))
        ot_rounds = int(match.group(2))
        round_times = list(map(int, match.group(3).split('-')))
        
        # Regular round time and overtime round time
        regular_round_time = round_times[0]
        overtime_round_time = round_times[-1] if ot_rounds > 0 else 0
        
        # Calculate total time based on the number of rounds
        total_time_minutes = (rounds-1) * regular_round_time + ot_rounds * overtime_round_time
        
        # Extract the time for the final round
        final_round_time = row['time']
        final_minutes, final_seconds = map(int, final_round_time.split(':'))
        final_time_seconds = final_minutes * 60 + final_seconds
        
        # Adjust the total time to account for the final round
        total_time_seconds = total_time_minutes * 60 + final_time_seconds
        
        return total_time_seconds
    else:
        # Case for format without overtime
        match_no_ot = re.match(r'(\d+) Rnd \((.*?)\)', row['format'])
        
        if match_no_ot:
            rounds = int(match_no_ot.group(1))
            round_times = list(map(int, match_no_ot.group(2).split('-')))
            regular_round_time = round_times[0]
            
            # Calculate total time based on the number of rounds
            total_time_minutes = (rounds-1) * regular_round_time
            
            # Extract the time for the final round
            final_round_time = row['time']
            final_minutes, final_seconds = map(int, final_round_time.split(':'))
            final_time_seconds = final_minutes * 60 + final_seconds
            
            total_time_seconds = total_time_minutes * 60 + final_time_seconds
            
            return total_time_seconds
        
    # Return None if the format doesn't match
    return None  

def main(in_dir, out_dir):
    df = pd.read_csv(in_dir)

    # Removing No Contest Fights - Fight did not happen
    df = df[df['red_result'] != 'NC']

    # Fill empty entries with 0s
    df = df.fillna(0)

    df['date'] = pd.to_datetime(df['date'], format='%d-%b-%y')
    df = df.sort_values(by='date')

    df['format'] = df['format'].apply(standardize_format)

    df['red_result'] = df['red_result'].apply(standardize_result)

    df['total_fight_time'] = df.apply(calculate_fight_time, axis=1)

    # Rename one of the Bruno Silvas to Bruno Bulldog Silva by manually finding Bulldog's Fights
    dates_to_check = pd.to_datetime([
        '2024-12-14',
        '2024-07-20',
        '2023-03-11',
        '2021-05-22',
        '2021-03-20',
        '2020-10-10',
        '2020-03-14',
        '2019-10-05'
    ])

    df_filtered = df[df['date'].isin(dates_to_check)]

    df.loc[df_filtered.index, 'red'] = df_filtered['red'].replace('Bruno Silva', 'Bruno Bulldog Silva')
    df.loc[df_filtered.index, 'blue'] = df_filtered['blue'].replace('Bruno Silva', 'Bruno Bulldog Silva')
    df.update(df_filtered)

    columns_to_keep = [col for col in df.columns if col not in ['outcome', 'time', 'round', 'format', 'blue_result']]
    df = df[columns_to_keep]

    df.to_csv(out_dir, index=False)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
