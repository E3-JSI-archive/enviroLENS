import re
import requests
import json

# TODO 
# Vsakič preveri če regex najde kakšne zadetke. + preverit, kakšne vse metapodatke še lahko imajo datoteke.

base_link = r'https://www.ecolex.org'

test_link = r'/details/decision/mercury-waste-3e5a9068-0c42-44e1-81dd-d94a9a91220c/?xcountry=Slovenia&amp;page=1'

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
    page_text = get_page.text

    # CATEGORY, tip zapisa je niz

    re_category = re.compile(r'record-icon">\s*<.*?title="(.*?)"')
    data['category'] = re.findall(re_category, page_text)[0]

    # NAME, tip zapisa je niz

    re_name = re.compile(r'<h1>(.*?)<')
    data['name'] = re.findall(re_name, page_text)[0]

    # DOCUMENT TYPE, tip zapisa je niz

    re_documentType = re.compile(r'Document type<\/dt>\s?<dd>(.*?)<')
    data['documentType'] = re.findall(re_documentType, page_text)[0]

    # REFERENCE NUMBER, tip zapisa je niz

    re_referenceNumber = re.compile(r'Reference number<\/dt>\s?<dd>(.*?)<')
    data['referenceNumber'] = re.findall(re_referenceNumber, page_text)[0]

    # DATE, tip zapisa je niz oblike MMM DD, YYYY, kjer MMM pomeni prve 3 črke imena meseca

    re_date = re.compile(r'Date<\/dt>\s?<dd>(.*?)<')
    data['date'] = re.findall(re_date, page_text)[0]

    # SOURCE - NAME, tip zapisa je niz

    re_sourceName = re.compile(r'Source<\/dt>\s?<dd>(.*?),')
    data['sourceName'] = re.findall(re_sourceName, page_text)[0]

    # SOURCE LINK, tip zapisa je niz

    re_sourceLink = re.compile(r'Source<\/dt>\s?<dd>.*?href="(.*?)"')
    data['sourceLink'] = re.findall(re_sourceLink, page_text)[0]

    # STATUS, tip zapisa je niz

    re_status = re.compile(r'Status<\/dt>\s?<dd>(.*?)<')
    data['status'] = re.findall(re_status, page_text)[0]

    # SUBJECT, tip zapisa je seznam nizov

    re_subject = re.compile(r'Subject<\/dt>\s*<dd>(.*?)<')
    data['subject'] = re.findall(re_subject, page_text)[0].split(',')

    # KEYWORD, tip zapisa je seznam nizov

    re_keyword = re.compile(r'span class="tag">(.*?)<')
    data['keyword'] = re.findall(re_keyword, page_text)

    # TREATY - LINK, tip zapisa je niz

    re_treatyLink = re.compile(r'Treaty<\/dt>\s*<dd>\s*<a href="(.*)"')
    data['treatyLink'] = re.findall(re_treatyLink, page_text)[0]

    # TREATY - NAME, tip zapisa je niz

    re_treatyName = re.compile(r'Treaty<\/dt>\s*<dd>\s*.*?>\s*(.*)')
    data['treatyName'] = re.findall(re_treatyName, page_text)[0]

    # MEETING - NAME, tip zapisa je niz

    re_meetingName = re.compile(r'Meeting<\/dt>\s*<dd>\s*.*\s*.*?>(.*?)<')
    data['meetingName'] = re.findall(re_meetingName, page_text)[0]

    # MEETING - LINK, tip zapisa je niz

    re_meetingLink = re.compile(r'Meeting<\/dt>\s*<dd>\s*<a href="(.*)"')
    data['meetingLink'] = re.findall(re_meetingLink, page_text)[0]

    # WEBSITE, tip zapisa je niz 

    re_website = re.compile(r'Website<\/dt>\s*<dd>\s*<a href="(.*)"')
    data['webiste'] = re.findall(re_website, page_text)[0]

    # ABSTRACT, tip zapisa je niz
    # Zaenkrat mu odstranimo vse html tage, smiselno bi bilo, da se mogoče ohranijo tagi za odstavke 

    re_abstract = re.compile(r'Abstract<\/dt>\s*<dd>\s*<div.*?>(.*?)<\/div>')
    abstract_text = re.findall(re_abstract, page_text)[0]

    all_tags = re.compile(r'<.*?>')
    cleaned_text = re.sub(all_tags, '', abstract_text)

    data['abstract'] = cleaned_text

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

    print(count_good)

    count_all += 1

    url = line.strip()

    get_content(url)
    count_good += 1
    # except:
    #     print('FAIL', count_all, url)
    #     FAILS.append(line)
    #     count_fails += 1

print('Successfully taken data from {} out of {} pages'.format(count_good, count_all))

print(count_good)






