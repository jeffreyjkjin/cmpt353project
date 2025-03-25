import pandas as pd
import requests

from bs4 import BeautifulSoup

columns = ['date', 'red', 'blue', 'red_result', 'blue_result', 'outcome', 'round', 'time', 
           'format', 'r1_red_kd', 'r1_blue_kd', 'r1_red_tot_str_lnd', 'r1_red_tot_str_att', 
           'r1_blue_tot_str_lnd', 'r1_blue_tot_str_att', 'r1_red_td_lnd', 'r1_red_td_att', 
           'r1_blue_td_lnd', 'r1_blue_td_att', 'r1_red_sub_att', 'r1_blue_sub_att', 'r1_red_rev', 
           'r1_blue_rev', 'r1_red_ctrl', 'r1_blue_ctrl', 'r2_red_kd', 'r2_blue_kd', 
           'r2_red_tot_str_lnd', 'r2_red_tot_str_att', 'r2_blue_tot_str_lnd', 
           'r2_blue_tot_str_att', 'r2_red_td_lnd', 'r2_red_td_att', 'r2_blue_td_lnd', 
           'r2_blue_td_att', 'r2_red_sub_att', 'r2_blue_sub_att', 'r2_red_rev', 'r2_blue_rev', 
           'r2_red_ctrl', 'r2_blue_ctrl', 'r3_red_kd', 'r3_blue_kd', 'r3_red_tot_str_lnd', 
           'r3_red_tot_str_att', 'r3_blue_tot_str_lnd', 'r3_blue_tot_str_att', 'r3_red_td_lnd', 
           'r3_red_td_att', 'r3_blue_td_lnd', 'r3_blue_td_att', 'r3_red_sub_att', 
           'r3_blue_sub_att', 'r3_red_rev', 'r3_blue_rev', 'r3_red_ctrl', 'r3_blue_ctrl', 
           'r4_red_kd', 'r4_blue_kd', 'r4_red_tot_str_lnd', 'r4_red_tot_str_att', 
           'r4_blue_tot_str_lnd', 'r4_blue_tot_str_att', 'r4_red_td_lnd', 'r4_red_td_att', 
           'r4_blue_td_lnd', 'r4_blue_td_att', 'r4_red_sub_att', 'r4_blue_sub_att', 'r4_red_rev', 
           'r4_blue_rev', 'r4_red_ctrl', 'r4_blue_ctrl', 'r5_red_kd', 'r5_blue_kd', 
           'r5_red_tot_str_lnd', 'r5_red_tot_str_att', 'r5_blue_tot_str_lnd', 
           'r5_blue_tot_str_att', 'r5_red_td_lnd', 'r5_red_td_att', 'r5_blue_td_lnd', 
           'r5_blue_td_att', 'r5_red_sub_att', 'r5_blue_sub_att', 'r5_red_rev', 'r5_blue_rev',
           'r5_red_ctrl', 'r5_blue_ctrl', 'r1_red_sig_str_lnd', 'r1_red_sig_str_att', 
           'r1_blue_sig_str_lnd', 'r1_blue_sig_str_att', 'r1_red_head_sig_str_lnd', 
           'r1_red_head_sig_str_att', 'r1_blue_head_sig_str_lnd', 'r1_blue_head_sig_str_att', 
           'r1_red_body_sig_str_lnd', 'r1_red_body_sig_str_att', 'r1_blue_body_sig_str_lnd', 
           'r1_blue_body_sig_str_att', 'r1_red_leg_sig_str_lnd', 'r1_red_leg_sig_str_att', 
           'r1_blue_leg_sig_str_lnd', 'r1_blue_leg_sig_str_att', 'r1_red_dist_sig_str_lnd', 
           'r1_red_dist_sig_str_att', 'r1_blue_dist_sig_str_lnd', 'r1_blue_dist_sig_str_att', 
           'r1_red_clch_sig_str_lnd', 'r1_red_clch_sig_str_att', 'r1_blue_clch_sig_str_lnd', 
           'r1_blue_clch_sig_str_att', 'r1_red_gnd_sig_str_lnd', 'r1_red_gnd_sig_str_att', 
           'r1_blue_gnd_sig_str_lnd', 'r1_blue_gnd_sig_str_att', 'r2_red_sig_str_lnd', 
           'r2_red_sig_str_att', 'r2_blue_sig_str_lnd', 'r2_blue_sig_str_att', 
           'r2_red_head_sig_str_lnd', 'r2_red_head_sig_str_att', 'r2_blue_head_sig_str_lnd', 
           'r2_blue_head_sig_str_att', 'r2_red_body_sig_str_lnd', 'r2_red_body_sig_str_att', 
           'r2_blue_body_sig_str_lnd', 'r2_blue_body_sig_str_att', 'r2_red_leg_sig_str_lnd', 
           'r2_red_leg_sig_str_att', 'r2_blue_leg_sig_str_lnd', 'r2_blue_leg_sig_str_att', 
           'r2_red_dist_sig_str_lnd', 'r2_red_dist_sig_str_att', 'r2_blue_dist_sig_str_lnd', 
           'r2_blue_dist_sig_str_att', 'r2_red_clch_sig_str_lnd', 'r2_red_clch_sig_str_att', 
           'r2_blue_clch_sig_str_lnd', 'r2_blue_clch_sig_str_att', 'r2_red_gnd_sig_str_lnd', 
           'r2_red_gnd_sig_str_att', 'r2_blue_gnd_sig_str_lnd', 'r2_blue_gnd_sig_str_att', 
           'r3_red_sig_str_lnd', 'r3_red_sig_str_att', 'r3_blue_sig_str_lnd', 
           'r3_blue_sig_str_att', 'r3_red_head_sig_str_lnd', 'r3_red_head_sig_str_att', 
           'r3_blue_head_sig_str_lnd', 'r3_blue_head_sig_str_att', 'r3_red_body_sig_str_lnd', 
           'r3_red_body_sig_str_att', 'r3_blue_body_sig_str_lnd', 'r2_blue_body_sig_str_att', 
           'r3_red_leg_sig_str_lnd', 'r3_red_leg_sig_str_att', 'r3_blue_leg_sig_str_lnd', 
           'r3_blue_leg_sig_str_att', 'r3_red_dist_sig_str_lnd', 'r3_red_dist_sig_str_att', 
           'r3_blue_dist_sig_str_lnd', 'r3_blue_dist_sig_str_att', 'r3_red_clch_sig_str_lnd', 
           'r3_red_clch_sig_str_att', 'r3_blue_clch_sig_str_lnd', 'r3_blue_clch_sig_str_att',
           'r3_red_gnd_sig_str_lnd', 'r3_red_gnd_sig_str_att', 'r3_blue_gnd_sig_str_lnd',
           'r3_blue_gnd_sig_str_att', 'r4_red_sig_str_lnd', 'r4_red_sig_str_att', 
           'r4_blue_sig_str_lnd', 'r4_blue_sig_str_att', 'r4_red_head_sig_str_lnd', 
           'r4_red_head_sig_str_att', 'r4_blue_head_sig_str_lnd', 'r4_blue_head_sig_str_att',
           'r4_red_body_sig_str_lnd', 'r4_red_body_sig_str_att', 'r4_blue_body_sig_str_lnd', 
           'r4_blue_body_sig_str_att', 'r4_red_leg_sig_str_lnd', 'r4_red_leg_sig_str_att', 
           'r4_blue_leg_sig_str_lnd', 'r4_blue_leg_sig_str_att', 'r4_red_dist_sig_str_lnd', 
           'r4_red_dist_sig_str_att', 'r4_blue_dist_sig_str_lnd', 'r4_blue_dist_sig_str_att',
           'r4_red_clch_sig_str_lnd', 'r4_red_clch_sig_str_att', 'r4_blue_clch_sig_str_lnd', 
           'r4_blue_clch_sig_str_att', 'r4_red_gnd_sig_str_lnd', 'r4_red_gnd_sig_str_att', 
           'r4_blue_gnd_sig_str_lnd', 'r4_blue_gnd_sig_str_att', 'r5_red_sig_str_lnd', 
           'r5_red_sig_str_att', 'r5_blue_sig_str_lnd', 'r5_blue_sig_str_att',
           'r5_red_head_sig_str_lnd', 'r5_red_head_sig_str_att', 'r5_blue_head_sig_str_lnd', 
           'r5_blue_head_sig_str_att', 'r5_red_body_sig_str_lnd', 'r5_red_body_sig_str_att', 
           'r5_blue_body_sig_str_lnd', 'r5_blue_body_sig_str_att', 'r5_red_leg_sig_str_lnd', 
           'r5_red_leg_sig_str_att', 'r5_blue_leg_sig_str_lnd', 'r5_blue_leg_sig_str_att',
           'r5_red_dist_sig_str_lnd', 'r5_red_dist_sig_str_att', 'r5_blue_dist_sig_str_lnd', 
           'r5_blue_dist_sig_str_att', 'r5_red_clch_sig_str_lnd', 'r5_red_clch_sig_str_att', 
           'r5_blue_clch_sig_str_lnd', 'r5_blue_clch_sig_str_att', 'r5_red_gnd_sig_str_lnd', 
           'r5_red_gnd_sig_str_att', 'r5_blue_gnd_sig_str_lnd', 'r5_blue_gnd_sig_str_att']

total_padding = [None for _ in range(0, 16)]
sig_strike_padding = [None for _ in range(0, 28)]

# scrapes fight data from the provided URL
def scrapeFight(URL, date):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    data = [date]

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
    format = format[len(format)-17:len(format)].strip()
    data.append(format)

    sections = soup.find_all('section', class_='b-fight-details__section js-fight-section')
    
    # red stats first, blue stats second
    totals = sections[2].find_all('tr', class_='b-fight-details__table-row')[1:]
    for total in totals:
        stats = total.find_all('td', class_='b-fight-details__table-col')

        kd = stats[1].text.strip().split(' ')
        data.extend([kd[0].strip(), kd[-1].strip()])

        total_strikes = stats[4].text.strip().split(' ')
        data.extend([total_strikes[0].strip(), total_strikes[2].strip(), 
                     total_strikes[-3].strip(), total_strikes[-1].strip()])

        td = stats[5].text.strip().split(' ')
        data.extend([td[0].strip(), td[2].strip(), td[-3].strip(), td[-1].strip()])

        sub_att = stats[7].text.strip().split(' ')
        data.extend([sub_att[0].strip(), sub_att[-1].strip()])
        
        rev = stats[8].text.strip().split(' ')
        data.extend([rev[0].strip(), rev[-1].strip()])

        ctrl = stats[9].text.strip().split(' ')
        data.extend([ctrl[0].strip(), ctrl[-1].strip()])

    # pad data with dummy values if fight is not 5 rounds
    while(len(data) != 89): data.extend(total_padding)

    # red fighter landed/red fighter attempt/blue fighter landed/blue fighter attempt
    strikes = sections[4].find_all('tr', class_='b-fight-details__table-row')[1:]
    for strike in strikes:
        stats = strike.find_all('td', class_='b-fight-details__table-col')

        sig_strikes = stats[1].text.strip().split(' ')
        data.extend([sig_strikes[0].strip(), sig_strikes[2].strip(), 
                     sig_strikes[-3].strip(), sig_strikes[-1].strip()])

        head_strikes = stats[3].text.strip().split(' ')
        data.extend([head_strikes[0].strip(), head_strikes[2].strip(), 
                     head_strikes[-3].strip(), head_strikes[-1].strip()])

        body_strikes = stats[4].text.strip().split(' ')
        data.extend([body_strikes[0].strip(), body_strikes[2].strip(), body_strikes[-3].strip(), body_strikes[-1].strip()])

        leg_strikes = stats[5].text.strip().split(' ')
        data.extend([leg_strikes[0].strip(), leg_strikes[2].strip(), leg_strikes[-3].strip(), leg_strikes[-1].strip()])

        dist_strikes = stats[6].text.strip().split(' ')
        data.extend([dist_strikes[0].strip(), dist_strikes[2].strip(), dist_strikes[-3].strip(), dist_strikes[-1].strip()])

        clinch_strikes = stats[7].text.strip().split(' ')
        data.extend([clinch_strikes[0].strip(), clinch_strikes[2].strip(), clinch_strikes[-3].strip(), clinch_strikes[-1].strip()])

        ground_strikes = stats[8].text.strip().split(' ')
        data.extend([ground_strikes[0].strip(), ground_strikes[2].strip(), ground_strikes[-3].strip(), ground_strikes[-1].strip()])

    # pad data with dummy values if fight is not 5 rounds
    while (len(data) != 229): data.extend(sig_strike_padding)

    return data

# scrapes every fight from the provided URL of a UFC card
def scrapeCard(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    fight_table = soup.find('tbody')
    fights = fight_table.find_all('a', class_='b-flag b-flag_style_green')

    details = soup.find('li', class_='b-list__box-list-item')
    date = details.text.strip()[5:].lstrip()

    card_data = []
    for fight in fights:
        card_data.append(scrapeFight(fight['href'], date))

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

    df = pd.DataFrame(data, columns=columns)
    df.to_csv('fight_data.csv')

if __name__ == '__main__':
    main()