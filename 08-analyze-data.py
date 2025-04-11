import matplotlib.pyplot as plt
import pandas as pd
import seaborn
import sys

from scipy import stats

seaborn.set_theme()

def getTop10(fight_data, fighter_data):
    print('***Collecting Top 10 Fighters by Rating***')
    fighter_data = fighter_data.sort_values(by='rating', ascending=False)

    # get most recent fight for all fighters
    red_fights = fight_data[['date', 'red']]
    red_fights.columns = ['last_fight', 'name']
    blue_fights = fight_data[['date', 'blue']]
    blue_fights.columns = ['last_fight', 'name']

    recent_fights = pd.concat([red_fights, blue_fights])
    recent_fights = recent_fights.sort_values(by='last_fight', ascending=False)
    recent_fights = recent_fights.groupby('name').first()

    # only select top 10 fighters who have fought in the last year
    fighter_data = fighter_data.join(recent_fights, on='name')
    within_year = pd.to_datetime(fighter_data['last_fight']) > pd.Timestamp.now()-pd.Timedelta(days=365)
    fighter_data = fighter_data[within_year]
    fighter_data = fighter_data.iloc[0:10]

    fighter_data.to_csv('08-top-10.csv', index=False)

def ratingChangesOverTime(fight_data):
    print('***Fighter Rating Changes Over Time***')

    # collect all fighters and ratings
    red_fighters = fight_data[['date', 'red', 'new_red_rating']]
    red_fighters.columns = ['date', 'name', 'rating']
    blue_fighters = fight_data[['date', 'blue', 'new_blue_rating']]
    blue_fighters.columns = ['date', 'name', 'rating']

    # average fighters ratings at the end of the year
    fighter_ratings = pd.concat([red_fighters, blue_fighters])
    fighter_ratings = fighter_ratings.sort_values('date', ascending=False)
    fighter_ratings['year'] = pd.to_datetime(fighter_ratings['date']).dt.year
    fighter_ratings = fighter_ratings.groupby(['name', 'year']).first()

    fighter_ratings = fighter_ratings.groupby('year').mean('rating').reset_index()

    # linear regression
    reg = stats.linregress(fighter_ratings['year'], fighter_ratings['rating'])
    print(f'Linear regression p-value: {reg.pvalue}')
    print(f'Correlation coefficient: {reg.rvalue}')

    fighter_ratings['prediction'] = reg.slope * fighter_ratings['year'] + reg.intercept
    fighter_ratings['residual'] = fighter_ratings['rating'] - fighter_ratings['prediction']

    # normality on residuals
    res_norm = stats.normaltest(fighter_ratings['residual'])
    print(f'Normality test on residuals: {res_norm.pvalue}')

    # scatterplot of ratings over time
    plt.figure()
    plt.xlabel('Year')
    plt.ylabel('Rating')
    plt.title('UFC Fighter Ratings Over Time')
    plt.scatter(fighter_ratings['year'], fighter_ratings['rating'])
    plt.plot(fighter_ratings['year'], fighter_ratings['prediction'], c='r')
    plt.legend(['Ratings', 'Linear Regression'])
    plt.savefig('ratings-over-time.png')

    # histogram
    plt.figure()
    plt.xlabel('Residuals')
    plt.ylabel('Frequency')
    plt.title('Residual Frequency from Linear Regression on UFC Fighter Ratings')
    plt.hist(fighter_ratings['residual'])
    plt.savefig('rating-residuals.png')

def main(fight_dir, fighter_dir):
    fights = pd.read_csv(fight_dir)
    fighters = pd.read_csv(fighter_dir)

    getTop10(fights, fighters)
    ratingChangesOverTime(fights)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])