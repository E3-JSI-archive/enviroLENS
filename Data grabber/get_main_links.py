import re
import requests
from time import time

def get_main_links(filterSLO=True):
    
    # Samo za zadetke, ki se navezujejo na Slovenijo 
    # Strani je trenutno 616
    LINK_SLO = r'https://www.ecolex.org/result/?xcountry=Slovenia&page='

    # Za vse zadetke
    # Strani je trenutno 10636
    LINK_ALL = r'https://www.ecolex.org/result/?page='

    if filterSLO:
        filename = 'main_links_SLO.txt'
        pages = 620
        link = LINK_SLO
    else:
        filename = 'main_links_ALL.txt'
        pages = 10640
        link = LINK_ALL

    file_links = open(filename, 'w')

    reLink = re.compile(r'search-result-title">\s*<a href="(.*?)"')

    start_time = time()

    for page in range(1, pages + 1):
        page_link = link + str(page)

        openpage = requests.get(url=page_link)
        html_text = openpage.text

        hits = re.findall(reLink, html_text)

        for hit in hits:
            file_links.write(hit + '\n')

        if page % 20 == 0:
            print(page, round(time() - start_time, 6))

    file_links.close()


if __name__ == '__main__':
    get_main_links()


