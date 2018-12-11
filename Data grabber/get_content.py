import re
import requests
import json

# TODO 
# Vsakič preveri če regex najde kakšne zadetke. + preverit, kakšne vse metapodatke še lahko imajo datoteke.

base_link = r'https://www.ecolex.org'

test_link = r'/details/decision/mercury-waste-3e5a9068-0c42-44e1-81dd-d94a9a91220c/?xcountry=Slovenia&amp;page=1'

def get_value_or_none(pattern, text):
    """
    Poišče vzorec v tekstu in vrne zadetek oziroma, če vzorca ne najde, vrne None.
    """
    temp = re.findall(pattern, text)
    if len(temp) > 0:
        return temp[0]
    else:
        return None

def remove_forbidden_characters(name):
    """
    Iz imena pobriše vse prepovedane znake (znake, ki v windowsu ne smejo biti v imenu datotek)
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
    S strani poberemo vse pomembne metapodatke o dogovoru in jih spravimo v slovar ter nato shranimo v json. Ti so:

    type (Treaty Decision, Legislation, ...)
    document type (Decision, Regulation, Legislation, ...)
    name 
    reference number
    date
    source (ime + link)
    status
    subject
    keywords
    treaty (ime + link)
    meeting (ime + link)
    website 
    abstract
    ...


    """

    data = dict()

    get_page = requests.get(base_link + suffix)
    if get_page.status_code != 200:
        print('Request Denied!', suffix)
    page_text = get_page.text

    # CATEGORY, tip zapisa je niz

    re_category = re.compile(r'record-icon">\s*<.*?title="(.*?)"')
    data['category'] = get_value_or_none(re_category, page_text)

    # NAME, tip zapisa je niz

    re_name = re.compile(r'<h1>(.*?)<')
    data['name'] = get_value_or_none(re_name, page_text)
    if data['name'] is not None:
        data['name'] = remove_forbidden_characters(data['name'])
    else:
        print('Name of the file not found!', suffix)

    # DOCUMENT TYPE, tip zapisa je niz

    re_documentType = re.compile(r'Document type<\/dt>\s?<dd>(.*?)<')
    data['documentType'] = get_value_or_none(re_documentType, page_text)

    # REFERENCE NUMBER, tip zapisa je niz

    re_referenceNumber = re.compile(r'Reference number<\/dt>\s?<dd>(.*?)<')
    data['referenceNumber'] = get_value_or_none(re_referenceNumber, page_text)

    # DATE, tip zapisa je niz oblike "MMM DD, YYYY", kjer MMM pomeni prve 3 črke imena meseca

    re_date = re.compile(r'Date<\/dt>\s?<dd>(.*?)<')
    data['date'] = get_value_or_none(re_date, page_text)

    # SOURCE - NAME, tip zapisa je niz

    re_sourceName = re.compile(r'Source<\/dt>\s?<dd>(.*?),')
    data['sourceName'] = get_value_or_none(re_sourceName, page_text)

    # SOURCE LINK, tip zapisa je niz

    re_sourceLink = re.compile(r'Source<\/dt>\s?<dd>.*?href="(.*?)"')
    data['sourceLink'] = get_value_or_none(re_sourceLink, page_text)

    # STATUS, tip zapisa je niz

    re_status = re.compile(r'Status<\/dt>\s?<dd>(.*?)<')
    data['status'] = get_value_or_none(re_status, page_text)

    # SUBJECT, tip zapisa je seznam nizov

    re_subject = re.compile(r'Subject<\/dt>\s*<dd>(.*?)<')
    data['subject'] = re.findall(re_subject, page_text)[0].split(',')

    # KEYWORD, tip zapisa je seznam nizov

    re_keyword = re.compile(r'span class="tag">(.*?)<')
    data['keyword'] = re.findall(re_keyword, page_text)

    # TREATY - LINK, tip zapisa je niz

    re_treatyLink = re.compile(r'Treaty<\/dt>\s*<dd>\s*<a href="(.*?)"')
    data['treatyLink'] = get_value_or_none(re_treatyLink, page_text)
    if data['treatyLink'] is not None:
        data['treatyLink'] = base_link + data['treatyLink']

    # TREATY - NAME, tip zapisa je niz

    re_treatyName = re.compile(r'Treaty<\/dt>\s*<dd>\s*.*?>\s*(.*)')
    data['treatyName'] = get_value_or_none(re_treatyName, page_text)

    # MEETING - NAME, tip zapisa je niz

    re_meetingName = re.compile(r'Meeting<\/dt>\s*<dd>\s*.*\s*.*?>(.*?)<')
    data['meetingName'] = get_value_or_none(re_meetingName, page_text)

    # MEETING - LINK, tip zapisa je niz

    re_meetingLink = re.compile(r'Meeting<\/dt>\s*<dd>\s*<a href="(.*?)"')
    data['meetingLink'] = get_value_or_none(re_meetingLink, page_text)

    # WEBSITE, tip zapisa je niz 

    re_website = re.compile(r'Website<\/dt>\s*<dd>\s*<a href="(.*?)"')
    data['webiste'] = get_value_or_none(re_website, page_text)

    # ABSTRACT, tip zapisa je niz
    # Zaenkrat mu odstranimo vse html tage, smiselno bi bilo, da se mogoče ohranijo tagi za odstavke 

    re_abstract = re.compile(r'Abstract<\/dt>\s*<dd>\s*<div.*?>(.*?)<\/div>')
    abstract_text = get_value_or_none(re_abstract, page_text)

    if abstract_text is not None:

        all_tags = re.compile(r'<.*?>')
        cleaned_text = re.sub(all_tags, '', abstract_text)

        data['abstract'] = cleaned_text
    else:
        data['abstract'] = None

    if print_data:
        for key in data:
            print(key  + ' : ' + str(data[key]))
    
    with open('data files\\' + data['name'] + '.json', 'w') as outfile:
        json.dump(data, outfile)

linksALL = 'main_links_ALL.txt'
linksSLO = 'main_links_SLO.txt'

links = open(linksSLO, 'r')

count_all = 0
count_good = 0
count_fails = 0

FAILS = []

for line in links:
    count_all += 1

    url = line.strip()

    try:
        get_content(url, print_data=True)
        count_good += 1
    except KeyboardInterrupt:
        break
    except:
        print('FAIL', count_all, url)
        FAILS.append(line)
        count_fails += 1
    
    # KO TESTIRAMO POBIRAMO SAMO PRVIH NEKAJ STRANI. 
    # ČE ŽELIŠ VSE PODATKE IZBRIŠI SPODNJI VRSTICI
    if count_all > 10:
        break

print('Successfully taken data from {} out of {} pages'.format(count_good, count_all))

print(count_good)






