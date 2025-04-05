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

def standardize_outcomes(outcome):
    if (outcome == 'KO/TKO'):
        return 0
    elif (outcome == 'Submission'):
        return 1
    elif (outcome == 'Decision - Unanimous'):
        return 2
    elif (outcome == 'Decision - Split'):
        return 3
    elif (outcome == "TKO - Doctor's Stoppage"):
        return 4
    elif (outcome == 'Decision - Majority'):
        return 5
    elif (outcome == 'DQ'):
        return 6
    elif (outcome == 'Other'):
        return 7

def standardize_result(result):
    if (result == 'W'):
        return 0
    elif (result == 'L'):
        return 1
    elif (result == 'D'):
        return 2

def calculate_max_time(fight_format):
    match = re.match(r'(\d+) Rnd \+ (\d+)OT \((.*)\)', fight_format)
    if match:
        # Extract number of rounds and overtime rounds
        rounds = int(match.group(1))
        overtime = int(match.group(2))
        
        # Extract time values
        time_str = match.group(3)
        time_values = list(map(int, time_str.split('-')))
        
        # Calculate the time for the rounds
        total_regular_time = rounds * time_values[0]
        
        # Calculate the time for overtime (use last time value for OT)
        total_overtime_time = overtime * time_values[-1]
        
        # Total maximum time
        total_time = total_regular_time + total_overtime_time
        return total_time
    
    # Longest No Time Limit fight was below 10 mintes, Set to 10 for Simplicity
    if 'No Time Limit' in fight_format:
        return 10
    
    # Return 0 if no valid format
    return 0  

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

    df['format'] = df['format'].apply(standardize_format)

    df['outcome'] = df['outcome'].apply(standardize_outcomes)

    df['red_result'] = df['red_result'].apply(standardize_result)

    df['max_time'] = df['format'].apply(calculate_max_time)

    df['total_fight_time'] = df.apply(calculate_fight_time, axis=1)

    df.to_csv(out_dir, index=False)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
