import pandas as pd
import sys

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
    
    # Step 2b. Use mode of weight class if it is missing
    mode_weight = df['weight'].mode()[0]
    df['weight'] = df['weight'].fillna(mode_weight)
    
    # Step 2c. Use average of height and reach in weight class if both are missing
    avg_height = pd.to_numeric(df['height'].groupby(df['weight']).mean())
    avg_reach = pd.to_numeric(df['reach'].groupby(df['weight']).mean())
    
    # Clean up NaN values in average height and reach by linear interpolation
    avg_height.interpolate(method='linear', inplace=True)
    avg_reach.interpolate(method='linear', inplace=True)
    
    # Fill NaN values with the mean of the column
    df['height'] = df['height'].fillna(df['weight'].map(avg_height))
    df['reach'] = df['reach'].fillna(df['weight'].map(avg_reach))
    
    # Step 2d. Assume Orthodox stance if it is missing
    df['stance'] = df['stance'].fillna('Orthodox')
    
    # Step 3. Convert height and reach to integers
    df['height'] = df['height'].astype(int)
    df['reach'] = df['reach'].astype(int)
    
    # Step 4. Convert weight to int
    df['weight'] = df['weight'].apply(
        lambda x: int((x.rstrip(' lbs.'))) if isinstance(x, str) else x
    )
    
    # Step 5. Remove fighters with no fights
    df = df[(df['wins'] > 0) | (df['losses'] > 0) | (df['draws'] > 0)]
    
    # Step 6. Assign nicknames to fighters with the same name
    name_counter = {}
    df['name'] = df['name'].apply(make_unique, counter=name_counter)
    
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

def make_unique(value, counter):
    """
    Create nicknames by appending a counter if it already exists.
    """
    if value not in counter:
        counter[value] = 1
        return value
    else:
        counter[value] += 1
        return f"{value}-{counter[value]}" 

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])