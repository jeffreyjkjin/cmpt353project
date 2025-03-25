import pandas as pd
import requests

from bs4 import BeautifulSoup

total_padding = [None for _ in range(0, 12)]
strike_padding = [None for _ in range(0, 14)]

# scrapes fight data from the provided URL
def scrapeFight(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    data = []

    # names of fighters
    fighters = soup.find_all('div', class_='b-fight-details__person')
    red_fighter = fighters[0].find('a', class_='b-link b-fight-details__person-link').text.strip()
    blue_fighter = fighters[1].find('a', class_='b-link b-fight-details__person-link').text.strip()
    data.extend([red_fighter, blue_fighter])

    # result for each fighter 
    red_result = fighters[0].find('i').text.strip()
    blue_result = fighters[1].find('i').text.strip()
    data.extend([red_result, blue_result])

    # win method, round, time, format
    details = soup.find('div', class_='b-fight-details__content')
    method = details.find('i', class_='b-fight-details__text-item_first').find_all('i')[1].text.strip()
    data.append(method)
    details = details.find_all('i', class_='b-fight-details__text-item')
    rounds = details[0].text.strip()[-1]
    data.append(rounds)
    time = details[1].text.strip()
    time = time[len(time)-4:len(time)]
    data.append(time)
    format = details[2].text.strip()
    format = format[len(format)-17:len(format)]
    data.append(format)

    sections = soup.find_all('section', class_='b-fight-details__section js-fight-section')
    
    # red stats first, blue stats second
    totals = sections[2].find_all('tr', class_='b-fight-details__table-row')[1:]
    for total in totals:
        stats = total.find_all('td', class_='b-fight-details__table-col')

        kd = stats[1].text.strip().split(' ')
        data.extend([kd[0], kd[-1]])

        td = stats[5].text.strip().split(' ')
        data.extend([td[0], td[2], td[-3], td[-1]])

        sub_att = stats[7].text.strip().split(' ')
        data.extend([sub_att[0], sub_att[-1]])
        
        rev = stats[8].text.strip().split(' ')
        data.extend([rev[0], rev[-1]])

        ctrl = stats[9].text.strip().split(' ')
        data.extend([ctrl[0], ctrl[-1]])

    # pad data with dummy values if fight is not 5 rounds
    while(len(data) != 68):
        data.extend(total_padding)

    # red fighter landed/red fighter attempt/blue fighter landed/blue fighter attempt
    strikes = sections[2].find_all('tr', class_='b-fight-details__table-row')[1:]
    for strike in strikes:
        stats = strike.find_all('td', class_='b-fight-details__table-col')

        total_strikes = stats[2].text.strip().split(' ')
        data.extend([total_strikes[0], total_strikes[2], total_strikes[-3], total_strikes[-1]])

        head_strikes = stats[4].text.strip().split(' ')
        data.extend([head_strikes[0], head_strikes[2], head_strikes[-3], head_strikes[-1]])

        body_strikes = stats[5].text.strip().split(' ')
        data.extend([body_strikes[0], body_strikes[2], body_strikes[-3], body_strikes[-1]])

        leg_strikes = stats[6].text.strip().split(' ')
        data.extend([leg_strikes[0], leg_strikes[2], leg_strikes[-3], leg_strikes[-1]])

        dist_strikes = stats[7].text.strip().split(' ')
        data.extend([dist_strikes[0], dist_strikes[2], dist_strikes[-3], dist_strikes[-1]])

        clinch_strikes = stats[8].text.strip().split(' ')
        data.extend([clinch_strikes[0], clinch_strikes[2], clinch_strikes[-3], clinch_strikes[-1]])

        ground_strikes = stats[9].text.strip().split(' ')
        data.extend([ground_strikes[0], ground_strikes[2], ground_strikes[-3], ground_strikes[-1]])

    # pad data with dummy values if fight is not 5 rounds
    while (len(data) != 208):
        data.extend(strike_padding)

    return data

# scrapes every fight from the provided URL of a UFC card
def scrapeCard(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    fight_table = soup.find('tbody')
    fights = fight_table.find_all('a', class_='b-flag b-flag_style_green')

    card_data = []
    for fight in fights:
        card_data.append(scrapeFight(fight['href']))

    return card_data

def main():
    # scrape link and date for every ufc event card
    # URL = 'http://ufcstats.com/statistics/events/completed' # last ~24 cards
    URL = 'http://ufcstats.com/statistics/events/completed?page=all' # every card
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    card_table = soup.find('tbody')
    cards = card_table.find_all('i', class_='b-statistics__table-content')[1:]

    data = []
    for card in cards:
        card_link = card.find('a', class_='b-link b-link_style_black')['href']

        data.extend(scrapeCard(card_link))

    df = pd.DataFrame(data)
    df.to_csv('fight_data.csv')

if __name__ == '__main__':
    main()