# Python WebScraper for online retail stores

This python webscraper was created to constantly monitor the price of items on online retailers and alert you via e-mail when a new low price is found or when the current price is below your target price for buying.

This project currently only works with brazillian store Centauro. Future versions will include other stores.


## Installation

You will need the following packages installed (conda environment is suggested):

- bs4 import BeautifulSoup
- selenium
- webdriver_manager
- datetime
- pandas
- time
- smtplib
- ssl
- email

This script also uses Google Chrome as its browser to open the webpages.

Please place all the supporting files (Log.txt, shopping_list.csv, itens.xlsx) in the same directory as the script.

## Files
- itens.xlsx: stores each color/model of each item scraped, logging the last price found, date of last price, highest price found, date of highest price, lowest price found and date of lowest price.
- log.txt: log with timestamp of added itens, new low prices found, malfunctioning links and script exceptions.
- run_webscraper_v1.py: first version of script (see "Project Versions" section for further explanation)
- run_webscraper_v2.py: second version of script (see "Project Versions" section for further explanation)
- shopping_list.csv: file used to feed run_webscraper_v2.py. Columns "link" (url of the item to scrape), "size(s)" (your prefered sizes for the items, separated by ",") and "buy_below" (value of item to trigger email alert)

## Project Versions
V1 - Uses the "urls" list on line 20 as source for webpages to scrape. Open each link, waits for it to fully load, iterates through different colors/models of the product. Then scrapes each HTML code and saves to itens.xlsx the relevant info. Also sends email for new low prices found. 

V2 - Uses the "shopping_list.csv" file as source for webpages to scrape. Open each link, waits for it to fully load, iterates through different colors/models of the product. Then scrapes each HTML code and saves to itens.xlsx the relevant info. Also sends email for new low prices found. 

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/#)
