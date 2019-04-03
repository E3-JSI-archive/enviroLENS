import requests
import re
import json
from helper_functions import *
from bs4 import BeautifulSoup
import time

LANGUAGES = [
    'BG', 'ES', 'CS', 'DA', 'DE', 'ET', 'EL', 'EN', 'FR', 'GA', 'HR', 'IT', 'LV', 'LT',
    'HU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SL', 'FI', 'SV'
]

def get_available_languages(celex_number):
    """
    Function that will take celex_number as input and return us all the languages in which this particular
    document is avaiable.

    :output: list of available languages
    :example output: ['EN', 'CS', 'DE']
    """

    url = r'https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:{}'.format(celex_number)

    # We will redo request until we get a successful one
    page = requests.get(url)
    while page.status_code != 200:
        page = requests.get(url)
        time.sleep(0.3)

    page_text = page.text

    # We use BeautifulSoup to navigate to html block in which language data is written.

    soup = BeautifulSoup(page_text, 'html.parser')
    soup = soup.find('body')
    soup = soup.find('div', {'class' : 'Wrapper clearfix'})
    soup = soup.find('div', {'class' : 'container-fluid'})
    soup = soup.find('div', {'id' : 'MainContent'})
    soup = soup.find('div', {'class' : 'row row-offcanvas'})
    soup = soup.find('div', {'id' : 'documentView', 'class' : 'col-md-9'})
    soup = soup.find('div', {'class' : 'EurlexContent'})
    soup = soup.find('div', {'class' : 'panel-group'})
    soup = soup.find('div', {'id' : 'multilingualPoint'})

    available_lang_part = soup.find('div', {'id' : 'PP2Contents'})
    available_lang_part = available_lang_part.find('div', {'class' : 'PubFormats'})
    available_lang_part = available_lang_part.find('ul', {'class' : 'dropdown-menu PubFormatVIEW'})

    available_languages = []

    # <li> tags that have class name 'disabled' are the li tags of non available languages.
    for child in available_lang_part.find_all('li'):
        if 'disabled' not in child.get('class'):
            available_languages.append(child.get_text().strip())
    
    return available_languages




def get_document_data_fixed_language(celex_number, language='EN'):
    """
    Requests the url of a dcoument with CELEX NUMBER = celex_number on eur-lex.europa.eu and extracts
    relevant information. Extracted information is saved into a dictionary and is then returned.
    """

    url = r'https://eur-lex.europa.eu/legal-content/{}/ALL/?uri=CELEX:{}'.format(language, celex_number)

    # We will redo requests every 0.3 seconds until we get a successful one 
    page = requests.get(url)
    while page.status_code != 200:
        page = requests.get(url)
        time.sleep(0.3)
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

    # Full document text is inside <div id='text'> tag. We navigate into it, collect its content and do some cleanup.
    # We erase multiple spaces and newlines.        

    document_text_lang = soup.find('div', {'id' : 'text'}).get_text().replace('  ', '').replace('\n', '')
    document_data['text'] = document_text_lang

    return document_data

def collect_data(celex):
    """
    Function that will extract all data about the document in all the available languages. 
    Document is uniquely determined by its celex number. Collected data will be stored into a
    dictionary and then into a json file named -> (celex_number_of_document).json 

    Keys of a dictionary will be different parameter names with language suffix at the end.
    examples:
        * translatedTitle_EN
        * classification_BG
        * classification_EN
        ...
    
    """

    # If you want all the available languages comment out the second line:

    available_languages = get_available_languages(celex)
    available_languages = [L for L in ['EN', 'SL', 'DE'] if L in available_languages]

    document_data = {}

    for language in available_languages:

        try:
            # Collecting data in fixed language
            data_lang = get_document_data_fixed_language(celex, language)

            # Changing the keys to have the language suffix and adding them into our main dictionary
            for parameter_name, value in data_lang.items():
                document_data[parameter_name + '_' + language] = value
            
            time.sleep(0.5)

            print(celex, language)
        except:
            print('FAIL at Celex Number: {}'.format(celex))
    
    with open('eurlex_docs\\' + celex + '.json', 'w') as outfile:
        json.dump(document_data, outfile, indent = 1)




if __name__ == '__main__':

    test_link = r'https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32018R0644'
    test_link = r'https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32018R0196'
    test_link = r'https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32018D0051'

    language = 'EN'
    celex = '32018D0051'
    # celex = '32018R0644'
    # celex = '62018CC0095'
    # celex = '62018CC0095'

    print(get_available_languages(celex))
    collect_data(celex)
