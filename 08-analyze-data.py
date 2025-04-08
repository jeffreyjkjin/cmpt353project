import pandas as pd
import sys

def getTop10(fight_data, fighter_data):
    fighter_data = fighter_data.sort_values(by='rating', ascending=False)

    # get most recent fight for all fighters
    red_fights = fight_data[['date', 'red']]
    red_fights.columns = ['last_fight', 'name']
    blue_fights = fight_data[['date', 'blue']]
    blue_fights.columns = ['last_fight', 'name']

    recent_fights = pd.concat([red_fights, blue_fights])
    recent_fights = recent_fights.sort_values(by='date', ascending=False)
    recent_fights = recent_fights.groupby('name').first()

    # only select top 10 fighters who have fought in the last year
    fighter_data = fighter_data.join(recent_fights, on='name')
    within_year = pd.to_datetime(fighter_data['last_fight']) > pd.Timestamp.now()-pd.Timedelta(days=365)
    fighter_data = fighter_data[within_year]
    fighter_data = fighter_data.iloc[0:10]

    fighter_data.to_csv('08-top-10.csv', index=False)

def main(fight_dir, fighter_dir):
    fights = pd.read_csv(fight_dir)
    fighters = pd.read_csv(fighter_dir)

    getTop10(fights, fighters)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])