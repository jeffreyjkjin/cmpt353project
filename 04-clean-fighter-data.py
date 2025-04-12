import pandas as pd
import sys

weight_classes = [0, 115, 125, 135, 145, 155, 170, 185, 205, 265, float('inf')]

def main(in_dir, out_dir):
    df = pd.read_csv(in_dir)
    # Step 0. Replace missing values with NaN
    df.replace('--', pd.NA, inplace=True)
    
    # Step 1. Convert height and reach to integers (in inches)
    df['height'] = pd.to_numeric(df['height'].apply(ft_to_in))
    df['reach'] =  pd.to_numeric(df['reach'].apply(strip_quotes))
    
    # Step 2a. Use height = reach if either is missing
    df['height'] = df.apply(
        lambda row: row['reach'] if pd.isna(row['height']) else row['height'], axis=1
    )
    df['reach'] = df.apply(
        lambda row: row['height'] if pd.isna(row['reach']) else row['reach'], axis=1
    )
    
    # Step 2b. Use mode of weight class if it is missing, then convert to int
    mode_weight = df['weight'].mode()[0]
    df['weight'] = df['weight'].fillna(mode_weight).apply(
        lambda x: int((x.rstrip(' lbs.'))) if isinstance(x, str) else x
    )
    
    # Step 2c. Use average of height and reach in weight class if both are missing
    # First, assign each fighter to a weight class
    df['weight_class'] = pd.cut(df['weight'], bins=weight_classes, right=False)
    
    # Calculate the average height and reach for each weight class
    avg_height = pd.to_numeric(df['height'].groupby(df['weight_class'], observed=True).mean())
    avg_reach = pd.to_numeric(df['reach'].groupby(df['weight_class'], observed=True).mean())

    # Fill NaN values with the mean of the column
    df['height'] = df['height'].fillna(df['weight'].map(avg_height))
    df['reach'] = df['reach'].fillna(df['weight'].map(avg_reach))
    
    # Step 2d. Assume Orthodox stance if it is missing
    df['stance'] = df['stance'].fillna('Orthodox')
    
    # Step 3. Convert height and reach to integers
    df['height'] = df['height'].round().astype(int)
    df['reach'] = df['reach'].round().astype(int)
    
    # Step 4. Remove fighters with no fights
    df = df[(df['wins'] > 0) | (df['losses'] > 0) | (df['draws'] > 0)]
    
    # Step 5. Handle fighters with the same name
    df = df.apply(handle_duplicate_name, axis=1)
    df = df[df['name'] != '(Drop)']
    
    # Step 6. Drop weight, weight_classes, and fight record
    df.drop(columns=['weight_class', 'weight', 'wins', 'losses', 'draws'], inplace=True)
    
    df['stance'] = df['stance'].replace('Open Stance', 'Switch')
    df['stance'] = df['stance'].replace('Sideways', 'Switch')
    df['stance'] = df['stance'].apply(stance_to_num)

    # Output the cleaned data to a new CSV file
    df.to_csv(out_dir, index=False)
    
def strip_quotes(str):
    """
    Remove trailing double quote from string and convert to int.
    """
    if pd.isna(str):
        return pd.NA
    return int(float(str.rstrip('"')))
    
def ft_to_in(str):
    """
    Convert height or reach string to inches in int.
    """
    if pd.isna(str):
        return pd.NA
    str = str.replace(' ', '')
    str = str.replace('"', '')
    feet, inches = map(int, str.split("'"))
    return int(feet * 12 + inches)

def handle_duplicate_name(row):
    """
    Handle duplicate names by assigning nicknames to the less well-known fighter.
    """
    # Bruno Silva case
    if row['name'] == 'Bruno Silva' and row['height'] == 64:
        row['name'] = 'Bruno \'Bulldog\' Silva'
    
    # Jean Silva case
    if row['name'] == 'Jean Silva' and row['height'] == 66:
        row['name'] = 'Jean \'White Bear\' Silva'
        
    # Michael McDonald case
    if row['name'] == 'Michael McDonald' and row['height'] == 71:
        row['name'] = 'Michael \'The Black Sniper\' McDonald'
    
    # Joey Gomez case
    if row['name'] == 'Joey Gomez' and row['weight'] == 155:
        row['name'] = 'Joey \'The Tasmanian Devil\' Gomez'
        
    # Mike Davis case
    if row['name'] == 'Mike Davis' and row['wins'] == 2 and row['losses'] == 0 and row['draws'] == 0:
        row['name'] = '(Drop)'
    
    return row

def stance_to_num(stance):
    """ Convert stance string to numeric """
    stance_mapping = {'Orthodox': 1, 'Southpaw': 2, 'Switch': 3}
    return stance_mapping.get(stance, 0)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])