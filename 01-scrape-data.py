import requests

from bs4 import BeautifulSoup

def main():
    # scrape link and date for every ufc event card
    URL = 'http://ufcstats.com/statistics/events/completed?page=all'
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    card_table = soup.find('tbody')
    cards = card_table.find_all('i', class_='b-statistics__table-content')[1:]

    for card in cards:
        card_link = card.find('a', class_='b-link b-link_style_black')['href']
        card_date = card.find('span', class_='b-statistics__date').text.strip()

        # todo: write helper function to scrape every fight from each card link

if __name__ == '__main__':
    main()