"""
Performs analysis and visualization on UFC fighter data.
- Identifies top 10 fighters by rating
- Tracks rating trends over time
- Analyzes stance-based win advantage
- Compares win rates of strikers vs. grapplers
"""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn
import sys

from scipy import stats

seaborn.set_theme()

def getTop10Fighters(fight_data, fighter_data):
    print('***Collecting Top 10 Fighters by Rating***')
    fighter_data = fighter_data.sort_values(by='rating', ascending=False)

    # Get most recent fight for all fighters
    red_fights = fight_data[['date', 'red']]
    red_fights.columns = ['last_fight', 'name']
    blue_fights = fight_data[['date', 'blue']]
    blue_fights.columns = ['last_fight', 'name']

    recent_fights = pd.concat([red_fights, blue_fights])
    recent_fights = recent_fights.sort_values(by='last_fight', ascending=False)
    recent_fights = recent_fights.groupby('name').first()

    # Only select top 10 fighters who have fought in the last year
    fighter_data = fighter_data.join(recent_fights, on='name')
    within_year = pd.to_datetime(fighter_data['last_fight']) > pd.Timestamp.now()-pd.Timedelta(days=365)
    fighter_data = fighter_data[within_year]
    fighter_data = fighter_data[['name', 'rating', 'rd']]
    fighter_data = fighter_data.iloc[0:10]
    fighter_data.index = pd.RangeIndex(1, 11)

    print(fighter_data)
    print('')

    fighter_data.to_csv('08-top-10-fighters.csv')

def ratingChangesOverTime(fight_data):
    print('***Fighter Rating Changes Over Time***')

    # Collect all fighters and ratings
    red_fighters = fight_data[['date', 'red', 'new_red_rating']]
    red_fighters.columns = ['date', 'name', 'rating']
    blue_fighters = fight_data[['date', 'blue', 'new_blue_rating']]
    blue_fighters.columns = ['date', 'name', 'rating']

    # Average fighters ratings at the end of the year
    fighter_ratings = pd.concat([red_fighters, blue_fighters])
    fighter_ratings = fighter_ratings.sort_values('date', ascending=False)
    fighter_ratings['year'] = pd.to_datetime(fighter_ratings['date']).dt.year
    fighter_ratings = fighter_ratings.groupby(['name', 'year']).first()

    fighter_ratings = fighter_ratings.groupby('year').mean('rating').reset_index()

    # Perform linear regression on yearly average ratings
    reg = stats.linregress(fighter_ratings['year'], fighter_ratings['rating'])

    print(f'Linear Regression p-value: {reg.pvalue}')
    print(f'Correlation coefficient: {reg.rvalue}')

    fighter_ratings['prediction'] = reg.slope * fighter_ratings['year'] + reg.intercept
    fighter_ratings['residual'] = fighter_ratings['rating'] - fighter_ratings['prediction']

    # Normality on residuals
    res_norm = stats.normaltest(fighter_ratings['residual'])

    print(f'Normality test on residuals: {res_norm.pvalue}')
    print('')

    # Plot scatterplot of ratings over time
    plt.figure()
    plt.xlabel('Year')
    plt.ylabel('Rating')
    plt.title('UFC Fighter Ratings Over Time')
    plt.scatter(fighter_ratings['year'], fighter_ratings['rating'])
    plt.plot(fighter_ratings['year'], fighter_ratings['prediction'], c='r')
    plt.legend(['Ratings', 'Linear Regression'])
    plt.savefig('08-ratings-over-time.png')

    # Plot histogram distribution of residuals to check normality
    plt.figure()
    plt.xlabel('Residuals')
    plt.ylabel('Frequency')
    plt.title('Residual Frequency from Linear Regression on UFC Fighter Ratings')
    plt.hist(fighter_ratings['residual'])
    plt.savefig('08-rating-residuals.png')

    fighter_ratings.to_csv('08-average-yearly-rating.csv', index=False)

def stanceAdvantage(fight_data):
    print('**Stance Advantage**')

    stance_dict = {
        1: 'Orthodox',
        2: 'Southpaw',
        3: 'Switch'
    }

    # Collect fighter stances and results
    red_results = fight_data[['red_stance', 'red_result']]
    red_results.columns = ['stance', 'result']
    
    blue_results = fight_data[['blue_stance', 'red_result']]
    blue_results.loc[:, 'red_result'] = 1 - blue_results['red_result']
    blue_results.columns = ['stance', 'result']

    fight_results = pd.concat([red_results, blue_results])
    fight_results['stance'] = fight_results['stance'].apply(lambda s: stance_dict[s])

    # Run chi-square test on stance vs. win/loss outcomes
    result_table = pd.crosstab(fight_results['stance'], fight_results['result'])
    chi2 = stats.chi2_contingency(result_table)

    print(f'Chi-Square p-value: {chi2.pvalue}')

    # win rates of each stance
    result_table['winrate'] = result_table[1.0] / result_table.sum(axis=1)

    print(f'Fighter stance and results contingency table')
    print(result_table)
    print('')

def strikersVersusGrapplers(fight_data, fighter_data):
    print('**Strikers Vs. Grapplers**')

    # Label fighters as grapplers if high takedown/control stats, default is striker
    fighter_data['style'] = 'striker'
    grappler_filter = (fighter_data['avg_td_lnd'] > 0.3) & (fighter_data['avg_ctrl'] > 30)
    fighter_data.loc[grappler_filter, 'style'] = 'grappler'

    # Collect fighter results
    red_results = fight_data[['red', 'red_result']]
    red_results.columns = ['name', 'result']
    
    blue_results = fight_data[['blue', 'red_result']]
    blue_results.loc[:, 'red_result'] = 1 - blue_results['red_result']
    blue_results.columns = ['name', 'result']

    fight_results = pd.concat([red_results, blue_results])

    # Add fight styles to results
    fight_results = fight_results.merge(fighter_data[['name', 'style']], on='name')

    # Chi square test
    result_table = pd.crosstab(fight_results['style'], fight_results['result'])
    chi2 = stats.chi2_contingency(result_table)

    print(f'Chi-Square p-value: {chi2.pvalue}')

    # Win rates of each style
    result_table['winrate'] = result_table[1.0] / result_table.sum(axis=1)

    print(f'Fighter style and results contingency table')
    print(result_table)

    fighter_data[['name', 'style']].to_csv('08-fighter-style.csv', index=False)

def main(fight_dir, fighter_dir):
    fights = pd.read_csv(fight_dir)
    fighters = pd.read_csv(fighter_dir)

    getTop10Fighters(fights, fighters)
    ratingChangesOverTime(fights)
    stanceAdvantage(fights)
    strikersVersusGrapplers(fights, fighters)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])