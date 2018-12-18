import re
import requests
import json

#: get_content(url, print_data=False) is a function that will grab the relevant data for documents of type 'TREATY DECISIONS'

base_link = r'https://www.ecolex.org'

test_link = r'/details/decision/mercury-waste-3e5a9068-0c42-44e1-81dd-d94a9a91220c/?xcountry=Slovenia&amp;page=1'

def get_value_or_none(pattern, text):
    """
    Given a regex pattern and a text, the function will return the match or None if no match will be found.

    :Pattern:   regex pattern of type re.compile(...)
    :text:      type string in which we are searching for a match

    In case a match is found, it returns it, otherwise it returns None.
    """

    temp = re.findall(pattern, text)
    if len(temp) > 0:
        return temp[0]
    else:
        return None

def remove_forbidden_characters(name):
    """ 
    A function that will remove all the forbidden characters out of the string. The forbidden characters are the ones
    that are not allowed to be used in the names of windows files. Those are  --> r'/*=:<>"|\'.

    :name:     a string

    returns the string name without the forbidden characters. 
    """

    new_name = ""
    for znak in name:
        if znak in r'\/*?:<>"|':
            new_name += '_'
        else:
            new_name += znak
    
    return new_name


def get_content(suffix, print_data = False):
    """
    From the page ( 'ecolex.org'+ suffix ) we grab the relevant data that is (type, document Type, name, reference, number,
    date, source name and source link, status, subject, keywords, treaty name and link, meeting name and link, website, abstract,
    ...).
    The data is then saved into a dictionary with parameter names as keys and the grabbed result as the value.

    Example:

    data["category"] = "Treaty decision"
    data["name"] = "Decision XXIX_21 _ Membership of the Implementation Committee"

    In the end the dictionary is saved into a json file named (data["name"] without forbidden characters and 
    length limited to 100).json

    :suffix:        the suffix of the url from which we are extracting the data. The suffix string is everything that comes 
                    after the 'ecolex.org'
    :print_data:    Optional parameter that is by default set to False. In case it is set to True, the function will at the end 
                    also print what it managed to extract from the page.

    returns None
    """

    data = dict()

    get_page = requests.get(base_link + suffix)
    if get_page.status_code != 200:
        print('Request Denied!', suffix)
        #: in case request is denied, we can't do anything
        return
    page_text = get_page.text

    #: Below are all the parameters and regex patterns that a document might have. Since the pattern can vary drastically
    #: it was easier to do for every parameter one by one.

    #: CATEGORY, type : string

    re_category = re.compile(r'record-icon">\s*<.*?title="(.*?)"')
    data['category'] = get_value_or_none(re_category, page_text)

    #: NAME, type : string

    re_name = re.compile(r'<h1>(.*?)<')
    data['name'] = get_value_or_none(re_name, page_text)
    if data['name'] is not None:
        data['name'] = remove_forbidden_characters(data['name'])
    else:
        print('Name of the file not found!', suffix)

    #: DOCUMENT TYPE, type : string

    re_documentType = re.compile(r'Document type<\/dt>\s?<dd>(.*?)<')
    data['documentType'] = get_value_or_none(re_documentType, page_text)

    #: REFERENCE NUMBER, type : string

    re_referenceNumber = re.compile(r'Reference number<\/dt>\s?<dd>(.*?)<')
    data['referenceNumber'] = get_value_or_none(re_referenceNumber, page_text)

    #: DATE, type : string -> "MMM DD, YYYY" where MMM are the first 3 letters of the month. 

    re_date = re.compile(r'Date<\/dt>\s?<dd>(.*?)<')
    data['date'] = get_value_or_none(re_date, page_text)

    #: SOURCE - NAME, type : string

    re_sourceName = re.compile(r'Source<\/dt>\s?<dd>(.*?),')
    data['sourceName'] = get_value_or_none(re_sourceName, page_text)

    #: SOURCE LINK, type : string

    re_sourceLink = re.compile(r'Source<\/dt>\s?<dd>.*?href="(.*?)"')
    data['sourceLink'] = get_value_or_none(re_sourceLink, page_text)

    #: STATUS, type : string

    re_status = re.compile(r'Status<\/dt>\s?<dd>(.*?)<')
    data['status'] = get_value_or_none(re_status, page_text)

    #: SUBJECT, type : List of strings

    re_subject = re.compile(r'Subject<\/dt>\s*<dd>(.*?)<')
    data['subject'] = re.findall(re_subject, page_text)[0].split(',')

    #: KEYWORD, type : list of strings

    re_keyword = re.compile(r'span class="tag">(.*?)<')
    data['keyword'] = re.findall(re_keyword, page_text)

    #: TREATY - LINK, type : string

    re_treatyLink = re.compile(r'Treaty<\/dt>\s*<dd>\s*<a href="(.*?)"')
    data['treatyLink'] = get_value_or_none(re_treatyLink, page_text)
    if data['treatyLink'] is not None:
        data['treatyLink'] = base_link + data['treatyLink']

    #: TREATY - NAME, type : string

    re_treatyName = re.compile(r'Treaty<\/dt>\s*<dd>\s*.*?>\s*(.*)')
    data['treatyName'] = get_value_or_none(re_treatyName, page_text)

    #: MEETING - NAME, type : string

    re_meetingName = re.compile(r'Meeting<\/dt>\s*<dd>\s*.*\s*.*?>(.*?)<')
    data['meetingName'] = get_value_or_none(re_meetingName, page_text)

    #: MEETING - LINK, type : string

    re_meetingLink = re.compile(r'Meeting<\/dt>\s*<dd>\s*<a href="(.*?)"')
    data['meetingLink'] = get_value_or_none(re_meetingLink, page_text)

    #: WEBSITE, type : string 

    re_website = re.compile(r'Website<\/dt>\s*<dd>\s*<a href="(.*?)"')
    data['webiste'] = get_value_or_none(re_website, page_text)

    #: ABSTRACT, type : string
    #: At current implementation all the html tags are removed from the text. It might make sense to keep that <p> paragraph tags. 

    re_abstract = re.compile(r'Abstract<\/dt>\s*<dd>\s*<div.*?>(.*?)<\/div>')
    abstract_text = get_value_or_none(re_abstract, page_text)

    if abstract_text is not None:

        all_tags = re.compile(r'<.*?>')
        cleaned_text = re.sub(all_tags, '', abstract_text)

        data['abstract'] = cleaned_text
    else:
        data['abstract'] = None

    #: FULL TEXT LINK, type : string

    re_fullTextLink = re.compile(r'Full text<\/dt>\s*<dd>\s*<a href="(.*?)"')
    data['fullTextLink'] = get_value_or_none(re_fullTextLink, page_text)

    #: COUNTRY/TERRITORY, type : list of strings

    re_countryTerritory = re.compile(r'Country\/Territory<\/dt>\s*<dd>(.*?)<')
    data['Country/Territory'] = get_value_or_none(re_countryTerritory, page_text)
    if data['Country/Territory'] is not None:
        data['Country/Territory'] = data['Country/Territory'].split(',')
    
    #: GEOGRAPHICAL AREA, type : list of strings

    re_geographicalArea = re.compile(r'Geographical area<\/dt>\s*<dd>(.*?)<')
    data['geographicalArea'] = get_value_or_none(re_geographicalArea, page_text)
    if data['geographicalArea'] is not None:
        data['geographicalArea'] = data['geographicalArea'].split(',')

    ########################################################################
    ########################################################################

    if print_data:
        for key in data:
            print(key  + ' : ' + str(data[key]))
    
    with open('treaty decisions\\' + data['name'][:150] + '.json', 'w') as outfile:
        json.dump(data, outfile)

def main():

    linksALL = 'main_links_ALL.txt'
    linksSLO = 'main_links_SLO.txt'

    links = open(linksSLO, 'r')

    count_all = 0
    count_good = 0
    count_fails = 0

    FAILS = []

    for line in links:
        url = line.strip()

        ## in this file we only grab data from files of type 'TREATY DECISIONS'.
        ## Here we check if the currecnt link is of that type.
        rtip = re.compile(r'\/details\/(.*?)\/')
        tip = re.findall(rtip, url)[0]

        if tip != 'decision':
            continue

        count_all += 1

        try:
            get_content(url, print_data=True)
            count_good += 1
        except KeyboardInterrupt:
            break
        except:
            print('FAIL', count_all, url)
            FAILS.append(line)
            count_fails += 1
        
        # WHEN TESTING HOW THE SCRIPT WORKS WE ONLY GRAB THE FIRST FEW PAGES 
        # IF YOU WANT TO GRAB THE DATA FROM ALL PAGES, COMMENT OUT THE 2 LINES BELOW
        if count_all > 10:
            break

    print('Successfully taken data from {} out of {} pages'.format(count_good, count_all))

    print(count_good)

if __name__ == '__main__':
    main()




