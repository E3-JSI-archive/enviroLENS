import json
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from collections import defaultdict

with open('analysis.json', 'r') as infile:
    analysis = json.load(infile)

# Histogram for year distribution of documents

def bar_graph_for_year_distribution():
    year_dist = analysis['yearHistogram']

    vals = []
    for k,v in year_dist.items():
        vals.append((k,v))

    fig, ax = plt.subplots()

    vals.sort()

    x_line = [e[0] for e in vals]
    y_line = [e[1] for e in vals]    

    ax.bar(x_line, y_line)
    loc = plticker.MultipleLocator(base=5.0) # this locator puts ticks at regular intervals of 10 years
    ax.xaxis.set_major_locator(loc)
    ax.set_xlabel('year')
    ax.set_ylabel('Number of documents')
    plt.show()

def language_representation_pie_chart():
    lang_repr = analysis['languages']

    labels = defaultdict(int)

    for k,v in lang_repr.items():
        if v < 500:
            labels['other'] += v
        else:
            labels[k] += v

    sizes, labs = [], []
    colors = ['gold', 'orange', 'lavender', 'salmon', 'grey', 'yellowgreen']

    for language, count in labels.items():
        sizes.append(count)
        labs.append(language)
    
    fig, ax = plt.subplots()
    
    plt.pie(sizes, labels=labs, colors = colors, shadow=True, autopct='%1.1f%%')
    plt.axis('equal')
    ax.set_title('Language representation')
    plt.show()

def horizontal_bar_chart(data_type):

    doctype = analysis[data_type]

    vals = []

    for k, v in doctype.items():
        vals.append((v,k))
    
    vals.sort(reverse=True)
    
    vals = vals[:30]

    y_line = [e[1].replace('&amp;', '&') for e in vals[::-1]]
    x_line = [e[0] for e in vals[::-1]]

    fig, ax = plt.subplots()

    ax.barh(y_line, x_line, color = ['orange'])

    fig.subplots_adjust(left = 0.25)

    ax.set_title("Most common keywords")
    ax.set_xlabel('# of occurences')

    plt.show()

#bar_graph_for_year_distribution()
# language_representation_pie_chart()
# horizontal_bar_chart('countries')
# horizontal_bar_chart('geoArea')
# horizontal_bar_chart('popularKeywords')
# horizontal_bar_chart('popularSubjects')

print(analysis['allFiles'])
print(len(analysis['languages']))
print(len(analysis['popularSubjects']))
print(len(analysis['popularKeywords']))