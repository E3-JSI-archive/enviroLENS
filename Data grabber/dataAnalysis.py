import os
import json
from collections import defaultdict
import re

cwd = os.getcwd()

folders = ["/jurisprudence/", "/legislation/", "/literature/", "/treaty/", "/treaty decisions/"]
# folders = ["/literature/"]

# folder = "/jurisprudence/"
# folder = "/legislation/"
# folder = "/literature/"
# folder = "/treaty/"
# folder = "/treaty decisions/"

withSource = 0
withAbstract = 0
allFiles = 0

popularKeywords = defaultdict(int)
popularSubjects = defaultdict(int)
yearHistogram = defaultdict(int)
categories = defaultdict(int)
documentTypes = defaultdict(int)
geoArea = defaultdict(int)
countries = defaultdict(int)

# Only for literature and treaties
languages = defaultdict(int)

regex_get_date_pattern = re.compile(r'\d{4}')

for folder in folders:
    for file in os.listdir(cwd + folder):
        with open(cwd + folder + file, 'r') as f:
            # We extract interesting data from the file
            info = json.load(f)
            if info['fullTextLink'] is not None:
                withSource += 1
            allFiles += 1

            if 'keyword' in info and info['keyword'] is not None:
                for keyword in info['keyword']:
                    popularKeywords[keyword] += 1
            
            if 'keywords' in info and info['keywords'] is not None:
                for keyword in info['keywords']:
                    popularKeywords[keyword] += 1
            
            if 'subject' in info and info['subject'] is not None:
                if type(info['subject']) is list:
                    for subject in info['subject']:
                        popularSubjects[subject] += 1
                else:
                    popularSubjects[info['subject']] += 1

            if 'date' in info and info['date'] is not None:
                year = re.findall(regex_get_date_pattern, info['date'])
                if len(year) > 0:
                    yearHistogram[year[0]] += 1
            
            if 'category' in info and info['category'] is not None:
                categories[info['category']] += 1
            
            if 'documentType' in info and info['documentType'] is not None:
                documentTypes[info['documentType'].strip()] += 1
            
            if 'abstract' in info and info['abstract'] is not None:
                withAbstract += 1

            if 'geographicalArea' in info and info['geographicalArea'] is not None:
                if type(info['geographicalArea']) is list:
                    for area in info['geographicalArea']:
                        geoArea[area.strip()] += 1
                else:
                    geoArea[info['geographicalArea']] += 1
            
            if 'country/Territory' in info and info['country/Territory'] is not None:
                if type(info['country/Territory']) is list:
                    for country in info['country/Territory']:
                        countries[country.strip()] += 1
                else:
                    countries[info['country/Territory'].strip()] += 1
            
            if 'language' in info and info['language'] is not None:
                if type(info['language']) is list:
                    for language in info['language']:
                        languages[language.strip()] += 1
                else:
                    languages[info['language']] += 1
            

    print("Folder completed!", folder)

for keyword in popularKeywords:
    print(keyword, popularKeywords[keyword])

for year in yearHistogram:
    print(year, yearHistogram[year])

print(len(countries))
print(len(geoArea))
print(len(languages))
print(len(categories))

for country in countries:
    print(country, countries[country])

gatheredAnalysis = {
    'countries' : countries,
    'geoArea' : geoArea,
    'languages' : languages,
    'withSource' : withSource,
    'withAbstract' : withAbstract,
    'allFiles' : allFiles,
    'categories' : categories,
    'documentTypes' : documentTypes,
    'yearHistogram' : yearHistogram,
    'popularKeywords' : popularKeywords,
    'popularSubjects' : popularSubjects,
}

with open('analysis.json', 'w') as jsonfile:
    json.dump(gatheredAnalysis, jsonfile)
