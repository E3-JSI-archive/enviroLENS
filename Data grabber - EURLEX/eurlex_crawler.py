import requests
from time import time
import re
import os
import json

def save_crawler_config(year, page):
    """
    Save the current year and current page into a json file. So the next time we run the script
    we will know from which points onwards we should continue our crawling.
    """

    with open('crawler_config.json', 'w') as outfile:
        json.dump(
            {
                'year' : year,
                'page' : page},
            outfile,
            indent=1
        )

def save_celex_numbers(celex_numbers):
    """
    Saves current celex numbers into json file. Since the script will take long time 
    to execute it is better to make intermediate copies.
    """

    with open('celex_numbers.json', 'w') as outfile:
        json.dump(list(celex_numbers), outfile, indent=1)

start_time  = time()

current_celex_numbers = set()

#: We load previously collected celex numbers
if 'celex_numbers.json' in os.listdir(os.getcwd()):
    with open('celex_numbers.json', 'r') as infile:
        current_celex_numbers = set(json.load(infile))

#: We read the year and page of the last checkpoint from the config file:
with open('crawler_config.json', 'r') as config_data:
    config = json.load(config_data)

#: Regex pattern that will find all CELEX numbers present on the page.
regex_celex = re.compile(r'CELEX number: <\/dt><dd>(.*?)<')

#: template URL, we need to fill it with YEAR and PAGE
URL = 'https://eur-lex.europa.eu/search.html?&scope=EURLEX&type=quick&lang=en&DD_YEAR={}&page={}'

#: If either of those warnings is present, we should continue our crawling on the next year rather than 
#: the next page.
WARNING_MESSAGE = 'Please choose a smaller number of pages'
WARNING_MESSAGE_2 = 'No results found'

current_year = config['year']
current_page = config['page']

while current_year < 2020:

    # While loop through all the pages.
    while True:

        # We fill YEAR and PAGE into template URL
        url_page = URL.format(current_year, current_page)

        #: Request the page and find all celex number and add it to our collection of celex numbers
        page = requests.get(url_page)

        find_celex_nums = re.findall(regex_celex, page.text)

        for celex in find_celex_nums:
            current_celex_numbers.add(celex)

        #: If we get a warning, we should break our loop through pages.
        if WARNING_MESSAGE in page.text:
            break

        if WARNING_MESSAGE_2 in page.text:
            break
        
        current_page += 1

        #: We do intermediate saves
        if current_page % 10 == 0:

            save_crawler_config(current_year, current_page)

        print('YEAR : {} - PAGE : {} - TIME : {}'.format(current_year, current_page, round(time() - start_time,3)))
        print(len(current_celex_numbers))

    current_year += 1
    current_page = 1

    # After every year, we save all of our so far collected celex numbers.
    save_celex_numbers(current_celex_numbers)
