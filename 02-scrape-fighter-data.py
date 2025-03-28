import pandas as pd
import requests

from bs4 import BeautifulSoup

columns = ['name', 'height', 'weight', 'reach', 'stance', 'wins', 'losses', 'draws']

# scrape individual fighter stats for every ufc fighter
def main():
    data = []

    # loop through every ufc fighter page alphabetically
    for i in range(0, 26):
        letter = chr(ord('a')+i)
        URL = f'http://ufcstats.com/statistics/fighters?char={letter}&page=all'

        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        fighters = soup.find_all('tr', class_='b-statistics__table-row')[2:]
        for fighter in  fighters:
            stats = fighter.find_all('td', class_='b-statistics__table-col')
            
            # get stats
            name = f'{stats[0].text.strip()} {stats[1].text.strip()}'
            ht = stats[3].text.strip()
            wt = stats[4].text.strip()
            reach = stats[5].text.strip()
            stance = stats[6].text.strip()
            wins = stats[7].text.strip()
            losses = stats[8].text.strip()
            draws = stats[9].text.strip()

            data.append([name, ht, wt, reach, stance, wins, losses, draws])

    df = pd.DataFrame(data, columns=columns)
    df.to_csv('fighter_data.csv')

if __name__ == '__main__':
    main()