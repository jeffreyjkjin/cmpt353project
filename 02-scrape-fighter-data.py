"""
Scrapes fighter statistics (height, weight, reach, stance, record) from UFCStats.com.
Loops through all fighters A-Z and saves the data to a CSV.
"""

import pandas as pd
import requests
import sys

from bs4 import BeautifulSoup

# Fighter Stats columns to scrape
columns = ['name', 'height', 'weight', 'reach', 'stance', 'wins', 'losses', 'draws']

# Scrape individual fighter stats for every ufc fighter
def main(out_dir):
    data = []

    # Loop through every ufc fighter page alphabetically
    for i in range(0, 26):
        letter = chr(ord('a')+i)
        URL = f'http://ufcstats.com/statistics/fighters?char={letter}&page=all'

        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        fighters = soup.find_all('tr', class_='b-statistics__table-row')[2:]
        for fighter in  fighters:
            stats = fighter.find_all('td', class_='b-statistics__table-col')
            
            # Get fighter stats
            name = f'{stats[0].text.strip()} {stats[1].text.strip()}'.strip()
            ht = stats[3].text.strip()
            wt = stats[4].text.strip()
            reach = stats[5].text.strip()
            stance = stats[6].text.strip()
            wins = stats[7].text.strip()
            losses = stats[8].text.strip()
            draws = stats[9].text.strip()

            data.append([name, ht, wt, reach, stance, wins, losses, draws])

            print(data[-1])

    df = pd.DataFrame(data, columns=columns)
    df.to_csv(out_dir, index=False)

if __name__ == '__main__':
    main(sys.argv[1])