import requests
import re
import json
from helper_functions import *
from bs4 import BeautifulSoup

LANGUAGES = [
    'BG', 'ES', 'CS', 'DA', 'DE', 'ET', 'EL', 'EN', 'FR', 'GA', 'HR', 'IT', 'LV', 'LT',
    'HU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SL', 'FI', 'SV'
]


def get(celex_number, language='EN'):
    """
    Requests the url of a dcoument with CELEX NUMBER = celex_number on eur-lex.europa.eu and extracts
    relevant information. Extracted information is saved into a dictionary
    and then into a JSON file. The name of the JSON file will be the documents CELEX number.
    """

    url = r'https://eur-lex.europa.eu/legal-content/{}/ALL/?uri=CELEX:{}'.format(language, celex_number)

    page = requests.get(url)
    page_text = page.text

    document_data = {}

    # With BeatifulSoup we quickly navigate through html structure to the part where the
    # interesting data is hidden:
    # body
    # div class="Wrapper clearfix"
    # div class="container-fluid"
    # div id="MainContent"
    # div class="row row-offcanvas"
    # div id="documentView" class="col-md-9"
    # div class="EurlexContent"
    # div class="panel-group"

    soup = BeautifulSoup(page_text, 'html.parser')
    soup = soup.find('body')
    soup = soup.find('div', {'class' : 'Wrapper clearfix'})
    soup = soup.find('div', {'class' : 'container-fluid'})
    soup = soup.find('div', {'id' : 'MainContent'})
    soup = soup.find('div', {'class' : 'row row-offcanvas'})
    soup = soup.find('div', {'id' : 'documentView', 'class' : 'col-md-9'})
    soup = soup.find('div', {'class' : 'EurlexContent'})
    soup = soup.find('div', {'class' : 'panel-group'})

    # Extracting metadata: We navigate into div id="multilingualPoint"

    metadata = soup.find('div', {'id' : 'multilingualPoint'})

    string_parameters = {
        'translatedTitle' : r'translatedTitle.*?>(.*?)<',
        'originalTitle' : r'originalTitle.*?>(.*?)<',
    }

    for parameter_name, regex_pattern in string_parameters.items():
        document_data[parameter_name] = get_value_or_none(regex_pattern, str(metadata))
    
    ## EUROVOC descriptors:

    # We find the div tag that containts the descriptor. There is no easy way to find out in which of the div tags it
    # is in. But we are able to identity the right block with the key word 'Classifications'.

    for block in metadata.find_all('div', {'class' : 'panel panel-default PagePanel'}):

        if 'Classifications' in block.text:
            descriptor_block = block.find('div', {'id' : 'PPClass_Contents'})
            descriptor_block = descriptor_block.find('div', {'class' : 'panel-body'})
            descriptor_block = descriptor_block.find('dl', {'class' : 'NMetadata'})
            
            group_labels = []
            descriptors = []

            for child_node in descriptor_block.find_all('dt'):
                group_labels.append(child_node.get_text().strip().strip(':'))
            for child_node in descriptor_block.find_all('dd'):
                itemizer = child_node.find('ul')
                
                descriptors_by_group = []

                for item in itemizer.find_all('li'):
                    descriptors_by_group.append(item.get_text().strip().replace('\n', ''))
                
                descriptors.append(descriptors_by_group)
            
            classification  = {}
            for i in range(len(group_labels)):
                classification[group_labels[i]] = descriptors[i]
            
            document_data['classification'] = classification

        if 'Miscellaneous information' in block.text:

            misc_block = block.find('div', {'id' : 'PPMisc_Contents'})
            misc_block = misc_block.find('div', {'class' : 'panel-body'})
            misc_block = misc_block.find('dl', {'class' : 'NMetadata'})

            misc_info_groups = []
            misc_info_definitions = []

            for child_node in misc_block.find_all('dt'):
                misc_info_groups.append(child_node.get_text().strip().strip(':'))
            for child_node in misc_block.find_all('dd'):
                group_values = []
                for child in child_node.find_all():

                    group_values.append(child.get_text().strip())
                
                misc_info_definitions.append(group_values)

            misc_info = {}

            for i in range(len(misc_info_groups)):
                misc_info[misc_info_groups[i]] = misc_info_definitions[i]
            
            document_data['miscellaneousInformation'] = misc_info
            
        if 'Dates' in block.find('div', {'class' : 'panel-heading'}).get_text():

            dates_block = block.find('div', { 'id' : 'PPDates_Contents'})
            dates_block = dates_block.find('div', { 'class' : 'panel-body'})
            dates_block = dates_block.find('dl', { 'class' : 'NMetadata'})

            date_description = []
            dates = []

            for child_node in dates_block.find_all('dt'):
                date_description.append(child_node.get_text().strip().strip(':'))
            for child_node in dates_block.find_all('dd'):
                event = child_node.get_text().replace('\n', '').split(';')
                dates.append(event)
            
            date_events = {}

            for i in range(len(date_description)):
                date_events[date_description[i]] = dates[i]
            
            document_data['dateEvents'] = date_events
        
    # This is the part where we extract the documents in all possible languages. We first check all the available languages 
    # of our document and then we iterate over all found languages and extract full text of the document.

    available_lang_part = metadata.find('div', {'id' : 'PP2Contents'})
    available_lang_part = available_lang_part.find('div', {'class' : 'PubFormats'})
    available_lang_part = available_lang_part.find('ul', {'class' : 'dropdown-menu PubFormatVIEW'})

    available_languages = []

    # <li> tags that have class name 'disabled' are the li tags of non available languages.
    for child in available_lang_part.find_all('li'):
        if 'disabled' not in child.get('class'):
            available_languages.append(child.get_text().strip())

    for language in available_languages:

        # For each language we do almost exactly the procedure above, except we now just navigate into the block that contains
        # the text of the document and extract data.

        url = r'https://eur-lex.europa.eu/legal-content/{}/ALL/?uri=CELEX:{}'.format(language, celex_number)

        page = requests.get(url)
        page_text = page.text 

        soup = BeautifulSoup(page_text, 'html.parser')
        soup = soup.find('body')
        soup = soup.find('div', {'class' : 'Wrapper clearfix'})
        soup = soup.find('div', {'class' : 'container-fluid'})
        soup = soup.find('div', {'id' : 'MainContent'})
        soup = soup.find('div', {'class' : 'row row-offcanvas'})
        soup = soup.find('div', {'id' : 'documentView', 'class' : 'col-md-9'})
        soup = soup.find('div', {'class' : 'EurlexContent'})
        soup = soup.find('div', {'class' : 'panel-group'})

        document_text_lang = soup.find('div', {'id' : 'text'}).get_text().replace('  ', '').replace('\n', '')
        document_data['text_' + language] = document_text_lang

    with open('eurlex_docs\\' + celex + '.json', 'w') as outfile:
        json.dump(document_data, outfile, indent=1)

    return 


if __name__ == '__main__':

    test_link = r'https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32018R0644'
    test_link = r'https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32018R0196'
    test_link = r'https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32018D0051'

    language = 'EN'
    celex = '32018D0051'
    # celex = '32018R0644'
    # celex = '62018CC0095'
    # celex = '62018CC0095'

    get(celex, language)
