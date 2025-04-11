import sys
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

# Returns the probability that fighter1 (red) wins
def predict_winner(fighter1, fighter2, model, column_list, scaler):
    fighter1_name = fighter1['name']
    fighter2_name = fighter2['name']
    
    fighter1 = fighter1.to_frame().T
    fighter2 = fighter2.to_frame().T 
    
    # Drop unnecessary columns
    fighter1 = fighter1.drop(columns=['name', 'volatility'])
    fighter2 = fighter2.drop(columns=['name', 'volatility'])
    
    # Add prefix to columns
    fighter1 = fighter1.add_prefix('red_')
    fighter2 = fighter2.add_prefix('blue_')
    
    fighter1.reset_index(drop=True, inplace=True)
    fighter2.reset_index(drop=True, inplace=True)
    
    # Concatenate the two fighters into a single DataFrame
    fighter_data = pd.concat([fighter1, fighter2], axis=1)
    
    fighter_data = fighter_data[column_list]
    
    print(fighter_data)
    
    # Scale the data
    fighter_data = scaler.transform(fighter_data)
    # Convert back to DataFrame to keep the column names
    fighter_data = pd.DataFrame(fighter_data, columns=column_list)
    
    prediction = model.predict(fighter_data)
    
    print("Winner: ", fighter1_name if prediction[0] >=0.5 else fighter2_name)
    print(f'{fighter1_name} win probability: {prediction[0]:.2f}')
    print(f'{fighter2_name} win probability: {1 - prediction[0]:.2f}')



def main(model_path, fighter_data, input_path, output_path):
    # Load the model
    model, column_list, scaler = joblib.load(model_path)

    # Fighter list
    names = []

    # Open the file and read line by line
    with open(input_path, 'r') as file:
        for line in file:
            names.append(line.strip())
    print(names)
            
    # Check if the number of fighters is a power of 2 and more than 2 players
    if len(names) < 2 or (len(names) & (len(names) - 1)) != 0:
        print("Error: The number of fighters must be 2 or greater or a power of 2.")
        return

    # Read the full fighter data
    df = pd.read_csv(fighter_data)

    # Collect recognized and unrecognized names
    recognized_names = [name for name in names if name in df['name'].values]
    unrecognized_names = [name for name in names if name not in df['name'].values]

    # Filter rows based on recognized names
    fighters = df[[name in recognized_names for name in df['name']]]
    fighters = df.set_index('name').loc[recognized_names].reset_index()
    print(fighters)

    # Print unrecognized names
    if unrecognized_names:
        print(f"Cannot find the following fighters: {', '.join(unrecognized_names)}")
        return
        
    predict_winner(fighters.iloc[0], fighters.iloc[1], model, column_list, scaler)
        
if __name__ == '__main__':
    """
    Usage: python 07-predictor.py <model_path> <fighter_data> <input_path> <output_path>
    """
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])