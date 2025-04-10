# cmpt353project

## Setup
Before you begin, you must install all of the required dependencies to run our programs. Our programs use the following libraries:
- BeautifulSoup
- Pandas
- Requests
- ...

To install the required libraries, use the following:
```
pip3 install -r requirements.txt
```

## Scraping Data
All of our projects data is scraped from the official [UFC Stats](http://www.ufcstats.com/statistics/events/completed) website. We scraped data for every single UFC fight as well as the individual stats for each UFC fighter.

To scrape the fight data, use the following:
```
python3 01-scrape-fight-data.py outputFights.csv
python3 01-scrape-fight-data.py > fights # saves output to file as backup
```
where `outputFights` is the name of the CSV where the scraped fight data will be stored. A sample output file is provided at `/sample-data/01-fight-data.csv`. We recommend using the sample fight data rather than scraping it again as it can take around 5-6 hours to fully scrape.

To scrape the fighter data, use the following:
```
python3 02-scrape-fighter-data.py outputFighters.csv
python3 02-scrape-fighter-data.py > fighters # saves output to file as backup
```
where `outputFighters` is the name of the CSV where the scraped fighter data will be stored. A sample output file is provided at `/sample-data/02-fighter-data.csv`.

## Cleaning Data
To clean the fight data, use the following:
```
python3 03-clean-fight-data.py inputFights.csv outputFights.csv
python3 03-clean-fight-data.py sample-data/01-fight-data.csv outputFights.csv # use sample data
```
where `inputFights` is the name of the CSV file containing the raw fight data and `outputFights` is where the cleaned fight data will be stored. A sample output file is provided at `/sample-data/03-fight-data.csv`.

To clean the fighter data, use the following:
```
python3 04-clean-fighter-data.py inputFighters outputFighters
python3 04-clean-fighter-data.py sample-data/02-fighter-data.csv outputFighters # use sample data
```
where `inputFighters` is the name of the CSV file containing the raw fighter data and `outputFights` is where the cleaned fighter data will be stored. A sample output file is provided at `/sample-data/04-fight-data.csv`.

## Generating Features
To generate features with both fight and fighter data, use the following:
```
python3 05-generate-features.py inputFights.csv inputFighters.csv outputFights.csv outputFighters.csv
python3 05-generate-features.py sample-data/03-fight-data.csv sample-data/04-fighter-data.csv outputFights.csv outputFighters.csv # use sample data
```
where `inputFights` and `inputFighters` are the names of the CSV files containing the cleaned fight and fighter data respectively, and `outputFights` and `outputFighters` are where the generated features will be stored. The sample outputs files are provided at `/sample-data/05-fight-data.csv` and `/sample-data/05-fighter-data.csv` accordingly.

## Training Model

## Predictor

## Analyzing Data