import pandas as pd
import requests
import sys

from bs4 import BeautifulSoup

columns = ['date', 'red', 'blue', 'red_result', 'blue_result', 'outcome', 'round', 'time', 
           'format', 'r1_red_kd', 'r1_blue_kd', 'r1_red_tot_str_lnd', 'r1_red_tot_str_att', 
           'r1_blue_tot_str_lnd', 'r1_blue_tot_str_att', 'r1_red_td_lnd', 'r1_red_td_att', 
           'r1_blue_td_lnd', 'r1_blue_td_att', 'r1_red_sub_att', 'r1_blue_sub_att', 'r1_red_rev',
           'r1_blue_rev', 'r1_red_ctrl', 'r1_blue_ctrl', 'r1_red_sig_str_lnd', 
           'r1_red_sig_str_att', 'r1_blue_sig_str_lnd', 'r1_blue_sig_str_att', 
           'r1_red_head_sig_str_lnd', 'r1_red_head_sig_str_att', 'r1_blue_head_sig_str_lnd', 
           'r1_blue_head_sig_str_att', 'r1_red_body_sig_str_lnd', 'r1_red_body_sig_str_att', 
           'r1_blue_body_sig_str_lnd', 'r1_blue_body_sig_str_att', 'r1_red_leg_sig_str_lnd', 
           'r1_red_leg_sig_str_att', 'r1_blue_leg_sig_str_lnd', 'r1_blue_leg_sig_str_att', 
           'r1_red_dist_sig_str_lnd', 'r1_red_dist_sig_str_att', 'r1_blue_dist_sig_str_lnd', 
           'r1_blue_dist_sig_str_att', 'r1_red_clch_sig_str_lnd', 'r1_red_clch_sig_str_att',
           'r1_blue_clch_sig_str_lnd', 'r1_blue_clch_sig_str_att', 'r1_red_gnd_sig_str_lnd', 
           'r1_red_gnd_sig_str_att', 'r1_blue_gnd_sig_str_lnd', 'r1_blue_gnd_sig_str_att', 
           'r2_red_kd', 'r2_blue_kd', 'r2_red_tot_str_lnd', 'r2_red_tot_str_att', 
           'r2_blue_tot_str_lnd', 'r2_blue_tot_str_att', 'r2_red_td_lnd', 'r2_red_td_att', 
           'r2_blue_td_lnd', 'r2_blue_td_att', 'r2_red_sub_att', 'r2_blue_sub_att', 'r2_red_rev', 
           'r2_blue_rev', 'r2_red_ctrl', 'r2_blue_ctrl', 'r2_red_sig_str_lnd', 
           'r2_red_sig_str_att', 'r2_blue_sig_str_lnd', 'r2_blue_sig_str_att', 
           'r2_red_head_sig_str_lnd', 'r2_red_head_sig_str_att', 'r2_blue_head_sig_str_lnd', 
           'r2_blue_head_sig_str_att', 'r2_red_body_sig_str_lnd', 'r2_red_body_sig_str_att', 
           'r2_blue_body_sig_str_lnd', 'r2_blue_body_sig_str_att', 'r2_red_leg_sig_str_lnd', 
           'r2_red_leg_sig_str_att', 'r2_blue_leg_sig_str_lnd', 'r2_blue_leg_sig_str_att', 
           'r2_red_dist_sig_str_lnd', 'r2_red_dist_sig_str_att', 'r2_blue_dist_sig_str_lnd', 
           'r2_blue_dist_sig_str_att', 'r2_red_clch_sig_str_lnd', 'r2_red_clch_sig_str_att',
           'r2_blue_clch_sig_str_lnd', 'r2_blue_clch_sig_str_att', 'r2_red_gnd_sig_str_lnd',
           'r2_red_gnd_sig_str_att', 'r2_blue_gnd_sig_str_lnd', 'r2_blue_gnd_sig_str_att', 
           'r3_red_kd', 'r3_blue_kd', 'r3_red_tot_str_lnd', 'r3_red_tot_str_att', 
           'r3_blue_tot_str_lnd', 'r3_blue_tot_str_att', 'r3_red_td_lnd', 'r3_red_td_att', 
           'r3_blue_td_lnd', 'r3_blue_td_att', 'r3_red_sub_att', 'r3_blue_sub_att', 'r3_red_rev',
           'r3_blue_rev', 'r3_red_ctrl', 'r3_blue_ctrl', 'r3_red_sig_str_lnd', 'r3_red_sig_str_att', 
           'r3_blue_sig_str_lnd', 'r3_blue_sig_str_att', 'r3_red_head_sig_str_lnd', 
           'r3_red_head_sig_str_att', 'r3_blue_head_sig_str_lnd', 'r3_blue_head_sig_str_att', 
           'r3_red_body_sig_str_lnd', 'r3_red_body_sig_str_att', 'r3_blue_body_sig_str_lnd', 
           'r3_blue_body_sig_str_att', 'r3_red_leg_sig_str_lnd', 'r3_red_leg_sig_str_att', 
           'r3_blue_leg_sig_str_lnd', 'r3_blue_leg_sig_str_att', 'r3_red_dist_sig_str_lnd', 
           'r3_red_dist_sig_str_att', 'r3_blue_dist_sig_str_lnd', 'r3_blue_dist_sig_str_att',
           'r3_red_clch_sig_str_lnd', 'r3_red_clch_sig_str_att', 'r3_blue_clch_sig_str_lnd',
           'r3_blue_clch_sig_str_att', 'r3_red_gnd_sig_str_lnd', 'r3_red_gnd_sig_str_att',
           'r3_blue_gnd_sig_str_lnd', 'r3_blue_gnd_sig_str_att', 'r4_red_kd', 'r4_blue_kd',
           'r4_red_tot_str_lnd', 'r4_red_tot_str_att', 'r4_blue_tot_str_lnd', 
           'r4_blue_tot_str_att', 'r4_red_td_lnd', 'r4_red_td_att', 'r4_blue_td_lnd', 
           'r4_blue_td_att', 'r4_red_sub_att', 'r4_blue_sub_att', 'r4_red_rev', 'r4_blue_rev',
           'r4_red_ctrl', 'r4_blue_ctrl', 'r4_red_sig_str_lnd', 'r4_red_sig_str_att', 
           'r4_blue_sig_str_lnd', 'r4_blue_sig_str_att', 'r4_red_head_sig_str_lnd', 
           'r4_red_head_sig_str_att', 'r4_blue_head_sig_str_lnd', 'r4_blue_head_sig_str_att', 
           'r4_red_body_sig_str_lnd', 'r4_red_body_sig_str_att', 'r4_blue_body_sig_str_lnd', 
           'r4_blue_body_sig_str_att', 'r4_red_leg_sig_str_lnd', 'r4_red_leg_sig_str_att', 
           'r4_blue_leg_sig_str_lnd', 'r4_blue_leg_sig_str_att', 'r4_red_dist_sig_str_lnd', 
           'r4_red_dist_sig_str_att', 'r4_blue_dist_sig_str_lnd', 'r4_blue_dist_sig_str_att', 
           'r4_red_clch_sig_str_lnd', 'r4_red_clch_sig_str_att', 'r4_blue_clch_sig_str_lnd', 
           'r4_blue_clch_sig_str_att', 'r4_red_gnd_sig_str_lnd', 'r4_red_gnd_sig_str_att', 
           'r4_blue_gnd_sig_str_lnd', 'r4_blue_gnd_sig_str_att', 'r5_red_kd', 'r5_blue_kd', 
           'r5_red_tot_str_lnd', 'r5_red_tot_str_att', 'r5_blue_tot_str_lnd', 
           'r5_blue_tot_str_att', 'r5_red_td_lnd', 'r5_red_td_att', 'r5_blue_td_lnd', 
           'r5_blue_td_att', 'r5_red_sub_att', 'r5_blue_sub_att', 'r5_red_rev', 'r5_blue_rev', 
           'r5_red_ctrl', 'r5_blue_ctrl', 'r5_red_sig_str_lnd', 'r5_red_sig_str_att', 
           'r5_blue_sig_str_lnd', 'r5_blue_sig_str_att', 'r5_red_head_sig_str_lnd', 
           'r5_red_head_sig_str_att', 'r5_blue_head_sig_str_lnd', 'r5_blue_head_sig_str_att',
           'r5_red_body_sig_str_lnd', 'r5_red_body_sig_str_att', 'r5_blue_body_sig_str_lnd',
           'r5_blue_body_sig_str_att', 'r5_red_leg_sig_str_lnd', 'r5_red_leg_sig_str_att', 
           'r5_blue_leg_sig_str_lnd', 'r5_blue_leg_sig_str_att', 'r5_red_dist_sig_str_lnd', 
           'r5_red_dist_sig_str_att', 'r5_blue_dist_sig_str_lnd', 'r5_blue_dist_sig_str_att', 
           'r5_red_clch_sig_str_lnd', 'r5_red_clch_sig_str_att', 'r5_blue_clch_sig_str_lnd', 
           'r5_blue_clch_sig_str_att', 'r5_red_gnd_sig_str_lnd', 'r5_red_gnd_sig_str_att', 
           'r5_blue_gnd_sig_str_lnd', 'r5_blue_gnd_sig_str_att']

padding = [None for _ in range(0, 44)]

# scrapes fight data from the provided URL
def scrapeFight(URL, date):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    data = [date]

    # names of fighters
    fighters = soup.find_all('div', class_='b-fight-details__person')
    red_name = fighters[0].find('a', class_='b-link b-fight-details__person-link').text.strip()
    blue_name = fighters[1].find('a', class_='b-link b-fight-details__person-link').text.strip()

    # result for each fighter 
    red_result = fighters[0].find('i').text.strip()
    blue_result = fighters[1].find('i').text.strip()

    # win method, round, time, format
    details = soup.find('div', class_='b-fight-details__content')
    method = details.find('i', class_='b-fight-details__text-item_first').find_all('i')[1].text.strip()
    details = details.find_all('i', class_='b-fight-details__text-item')
    rounds = details[0].text.strip()[-1]

    time = details[1].text.strip()
    time = time[len(time)-4:len(time)]

    format = details[2].text.strip()
    format = format[len(format)-17:len(format)].strip()

    data.extend([red_name, blue_name, red_result, blue_result, method, rounds, time, format])

    sections = soup.find_all('section', class_='b-fight-details__section js-fight-section')
    totals = sections[2].find_all('tr', class_='b-fight-details__table-row')[1:]
    strikes = sections[4].find_all('tr', class_='b-fight-details__table-row')[1:]
    # totals should be same size as strikes
    for i in range(len(totals)):
        total_row = totals[i].find_all('td', class_='b-fight-details__table-col')
        strike_row = strikes[i].find_all('td', class_='b-fight-details__table-col')

        # get all stats per round
        kd = total_row[1].text.strip().split(' ')
        red_kd = kd[0].strip()
        blue_kd = kd[-1].strip()

        total_strikes = total_row[4].text.strip().split(' ')
        red_tot_str_lnd = total_strikes[0].strip()
        red_tot_str_att = total_strikes[2].strip()
        blue_tot_str_lnd = total_strikes[-3].strip()
        blue_tot_str_att = total_strikes[-1].strip()

        td = total_row[5].text.strip().split(' ')
        red_td_lnd = td[0].strip()
        red_td_att = td[2].strip()
        blue_td_lnd = td[-3].strip()
        blue_td_att = td[-1].strip()

        sub_att = total_row[7].text.strip().split(' ')
        red_sub_att = sub_att[0].strip()
        blue_sub_att = sub_att[-1].strip()
        
        rev = total_row[8].text.strip().split(' ')
        red_rev = rev[0].strip()
        blue_rev = rev[-1].strip()

        ctrl = total_row[9].text.strip().split(' ')
        red_ctrl = ctrl[0].strip()
        blue_ctrl = ctrl[-1].strip()

        sig_strikes = strike_row[1].text.strip().split(' ')
        red_sig_str_lnd = sig_strikes[0].strip()
        red_sig_str_att = sig_strikes[2].strip()
        blue_sig_str_lnd = sig_strikes[-3].strip()
        blue_sig_str_att = sig_strikes[-1].strip()

        head_strikes = strike_row[3].text.strip().split(' ')
        red_head_str_lnd = head_strikes[0].strip()
        red_head_str_att = head_strikes[2].strip()
        blue_head_str_lnd = head_strikes[-3].strip()
        blue_head_str_att = head_strikes[-1].strip()

        body_strikes = strike_row[4].text.strip().split(' ')
        red_body_str_lnd = body_strikes[0].strip()
        red_body_str_att = body_strikes[2].strip()
        blue_body_str_lnd = body_strikes[-3].strip()
        blue_body_str_att = body_strikes[-1].strip()

        leg_strikes = strike_row[5].text.strip().split(' ')
        red_leg_str_lnd = leg_strikes[0].strip()
        red_leg_str_att = leg_strikes[2].strip()
        blue_leg_str_lnd = leg_strikes[-3].strip()
        blue_leg_str_att = leg_strikes[-1].strip()

        dist_strikes = strike_row[6].text.strip().split(' ')
        red_dist_str_lnd = dist_strikes[0].strip()
        red_dist_str_att = dist_strikes[2].strip()
        blue_dist_str_lnd = dist_strikes[-3].strip()
        blue_dist_str_att = dist_strikes[-1].strip()

        clinch_strikes = strike_row[7].text.strip().split(' ')
        red_clinch_str_lnd = clinch_strikes[0].strip()
        red_clinch_str_att = clinch_strikes[2].strip()
        blue_clinch_str_lnd = clinch_strikes[-3].strip()
        blue_clinch_str_att = clinch_strikes[-1].strip()

        ground_strikes = strike_row[8].text.strip().split(' ')
        red_grn_str_lnd = ground_strikes[0].strip()
        red_grn_str_att = ground_strikes[2].strip()
        blue_grn_str_lnd = ground_strikes[-3].strip()
        blue_grn_str_att = ground_strikes[-1].strip()

        data.extend([red_kd, blue_kd, red_tot_str_lnd, red_tot_str_att, blue_tot_str_lnd,
                     blue_tot_str_att, red_td_lnd, red_td_att, blue_td_lnd, blue_td_att, 
                     red_sub_att, blue_sub_att, red_rev, blue_rev, red_ctrl, blue_ctrl, 
                     red_sig_str_lnd, red_sig_str_att, blue_sig_str_lnd, blue_sig_str_att,
                     red_head_str_lnd, red_head_str_att, blue_head_str_lnd, blue_head_str_att,
                     red_body_str_lnd, red_body_str_att, blue_body_str_lnd, blue_body_str_att,
                     red_leg_str_lnd, red_leg_str_att, blue_leg_str_lnd, blue_leg_str_att,
                     red_dist_str_lnd, red_dist_str_att, blue_dist_str_lnd, blue_dist_str_att,
                     red_clinch_str_lnd, red_clinch_str_att, blue_clinch_str_lnd, 
                     blue_clinch_str_att, red_grn_str_lnd, red_grn_str_att, blue_grn_str_lnd,
                     blue_grn_str_att])

    # pad data with dummy values if fight is not 5 rounds
    while (len(data) < 229): data.extend(padding)

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

def main(out_dir):
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
    df.to_csv(out_dir)

if __name__ == '__main__':
    main(sys.argv[1])