import re
import requests
import json
from bs4 import BeautifulSoup
from time import time

# get_content(url, print_data=False) funkcija, ki bo pobrala metapodatke za dokumente "LEGISLATION"

base_link = r'https://www.ecolex.org'

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

    # DATE, tip zapisa je niz (letnica)

    re_date = re.compile(r'title="Date">(.*?)<')
    data['date'] = get_value_or_none(re_date, page_text)

    # SOURCE - NAME, tip zapisa je niz

    re_sourceName = re.compile(r'Source<\/dt>\s*<dd>\s*(.*?),')
    data['sourceName'] = get_value_or_none(re_sourceName, page_text)

    # SOURCE LINK, tip zapisa je niz

    re_sourceLink = re.compile(r'Source<\/dt>\s*<dd>\s*.*\s*.*?href="(.*?)"')
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

    re_abstract = re.compile(r'Abstract<\/dt>\s*<dd>(.*?)<\/dd')
    abstract_text = get_value_or_none(re_abstract, page_text)

    if abstract_text is not None:

        all_tags = re.compile(r'<.*?>')
        cleaned_text = re.sub(all_tags, '', abstract_text)

        data['abstract'] = cleaned_text
    else:
        data['abstract'] = None

    # FULL TEXT LINK, tip zapisa je niz

    re_fullTextLink = re.compile(r'Full text<\/dt>\s*<dd>\s*<a href="(.*?)"')
    data['fullTextLink'] = get_value_or_none(re_fullTextLink, page_text)

    # COUNTRY/TERRITORY, tip zapisa je seznam nizov

    re_countryTerritory = re.compile(r'Country\/Territory<\/dt>\s*<dd>(.*?)<')
    data['Country/Territory'] = get_value_or_none(re_countryTerritory, page_text)
    if data['Country/Territory'] is not None:
        data['Country/Territory'] = data['Country/Territory'].split(',')
    
    # GEOGRAPHICAL AREA, tip zapisa je seznam nizov

    re_geographicalArea = re.compile(r'Geographical area<\/dt>\s*<dd>(.*?)<')
    data['geographicalArea'] = get_value_or_none(re_geographicalArea, page_text)
    if data['geographicalArea'] is not None:
        data['geographicalArea'] = data['geographicalArea'].split(',')

    # ENTRY INTO FORCE NOTES, tip zapisa je niz

    re_entryIntoForceNotes = re.compile(r'Entry into force notes<\/dt>\s*<dd>(.*?)<\/dd')
    data['entryIntoForceNotes'] = get_value_or_none(re_entryIntoForceNotes, page_text)

    ########################################################################################
    ########################################################################################

    """
    Tu spodaj pobiramo vse reference. Zaradi drugačnega zapisa html si bomo pomagali s knjižnico 
    BeautifulSoup.

    - Podatki o posameznem dokumentu so zapisani v html tagu "<article>"
    - Podatki o referencah so zapisani v tagu "<section, id='legislation-references'>"
    - Reference so grupirane po njihovem tipu (Amends, implements, implemented by, ...). Vsaka grupa je shranjena v 
      <dl> tagu.
    - Znotraj vsakega <dl> taga je v tagu <dt> zapisan tip reference, nato pa v vsakem <dd> tagu sledijo podatki za
      vsako referenco

    Z BeautifulSoup si pomagamo, da pride do posameznih <dd> tagov, nato pa z regexom poberemo podatke znotraj le tega.

    Podatki bomo shranili v zgornji slovar pod ključ 'references'. Vanj bomo shranili nov slovar, ki bo imel za ključe
    tipe referenc, vsak od teh pa bo imel za vrednost seznam referenc tega tipa skupaj s podatki.

    data -> 'references' -> 'Amends' -> [slovarji s podatki o posamezni referenci ]

    """

    soup = BeautifulSoup(page_text, 'html.parser')
    ref_section = soup.find('article').find('section', {'id' : 'legislation-references'})
    if ref_section is not None:
        ref_section = ref_section.find_all('dl')

    data['references'] = dict()

    if ref_section is not None:

        for tip_reference in ref_section:
            tip = tip_reference.dt.text
            data['references'][tip] = []

            for posamezna_referenca in tip_reference.find_all('dd'):

                reftekst = str(posamezna_referenca)
                
                single_reference = dict()

                re_refLink = re.compile(r'title">\s*<.*?="(.*?)"')
                single_reference['refLink'] = get_value_or_none(re_refLink, reftekst)

                re_refName = re.compile(r'search-result-title">\s*.*\s*.*?>(.*?)<')
                single_reference['refName'] = get_value_or_none(re_refName, reftekst)

                re_refCountry = re.compile(r'title="Country\/Territory">(.*)<')
                single_reference['refCountry'] = get_value_or_none(re_refCountry, reftekst)

                re_refDate = re.compile(r'title="Date">(.*)')
                single_reference['refDate'] = get_value_or_none(re_refDate, reftekst)

                re_refKeywords = re.compile(r'keywords">(.*?)<')
                single_reference['refKeywords'] = get_value_or_none(re_refKeywords, reftekst)
                if single_reference['refKeywords'] is not None:
                    single_reference['refKeywords'] = single_reference['refKeywords'].split(',')

                re_refSourceLink = re.compile(r'Source.*\s*.*? href="(.*?)"')
                single_reference['refSourceLink'] = get_value_or_none(re_refSourceLink, reftekst)

                re_refSourceName = re.compile(r'Source.*\s*.*?>(.*?)<')
                single_reference['refSourceName'] = get_value_or_none(re_refSourceName, reftekst)

                data['references'][tip].append(single_reference)


    ########################################################################
    ########################################################################

    if print_data:
        for key in data:
            print(key  + ' : ' + str(data[key]))
    
    with open('legislation\\' + data['name'][:150] + '.json', 'w') as outfile:
        json.dump(data, outfile)

linksALL = 'main_links_ALL.txt'
linksSLO = 'main_links_SLO.txt'

links = open(linksSLO, 'r')

count_all = 0
count_good = 0
count_fails = 0

FAILS = []

START_TIME = time()

for line in links:
    url = line.strip()

    ## tu preverimo, če je željena datoteka tipa "TREATYY DECISION"
    ## V primeru da je, jo v tej datoteki sparsamo.
    rtip = re.compile(r'\/details\/(.*?)\/')
    tip = re.findall(rtip, url)[0]

    if tip != 'legislation':
        continue

    count_all += 1

    try:
        get_content(url, print_data=False)
        count_good += 1
    except KeyboardInterrupt:
       break
    except Exception as e:
       print('FAIL', count_all, url)
       FAILS.append(line)
       count_fails += 1
       print(e)
    
    # KO TESTIRAMO POBIRAMO SAMO PRVIH NEKAJ STRANI. 
    # ČE ŽELIŠ VSE PODATKE IZBRIŠI SPODNJI VRSTICI
    if count_all > 200:
        break

    if count_all % 100 == 0:
        print(count_all, time() - START_TIME)

print('Successfully taken data from {} out of {} pages'.format(count_good, count_all))

print(count_good)




