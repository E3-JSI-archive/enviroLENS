import json
import plotly.offline as py
import plotly.graph_objs as go
from collections import defaultdict

# with open("eurlex_docs_analysis.json", 'r') as infile:
#     analysis = json.load(infile)
with open("eurlex_analysis_environment.json", 'r') as infile:
    analysis = json.load(infile)

print(analysis.keys())

def make_date_distribution_bar_chart():
    dates = defaultdict(int)

    for k,v in analysis['dates'].items():
        try:
            d,m,y = list(map(int, k.split('/')))
            dates[y] += v
        except:
            pass

    for key in dates:
        print(key, dates[key])

    ordered_keys = sorted(list(dates.keys()))
    # Minimal document year
    min_year = 1940

    X_AXIS = []
    Y_AXIS = []
    for year in range(min_year, 2020):
        X_AXIS.append(('{}'.format(year)))
        if year in dates:
            Y_AXIS.append(dates[year])
        else:
            Y_AXIS.append(0)

    print(len(X_AXIS))
    print(len(Y_AXIS))

    data = go.Bar(
        x = X_AXIS,
        y = Y_AXIS,
    )

    layout = go.Layout(
        title = 'Distribution of documents by year',
        font= dict(size=18)
    )

    figure = {
        'data' : [data],
        'layout' : layout,
    }

    py.plot(figure, filename='date_distribution.html')

def make_text_lengths_histogram():

    lengths = analysis['text_lengths']

    with_text = lengths.count(67)
    print(len(lengths) - with_text)


    print(max(lengths))
    valid_text = [min(e,10**5) for e in lengths if e != 67]
    print(len(valid_text))

    print(sum(valid_text)/len(valid_text))

    hist = go.Histogram(
        x = valid_text,
        nbinsx = 100)
    layout = go.Layout(
        title = 'Histogram of text lengths (in number of characters)',
        xaxis = dict(title='number of characters'),
        y_axis = dict(title='number of documents')
    ,)

    figure = {
        'data' : [hist],
        'layout' : layout,
    }

    py.plot(figure, filename='text_length_histogram.html')

def print_markdown_table_descriptors():

    sort_eurovoc = []
    for k,v in analysis['EUROVOC_descriptors'].items():
        sort_eurovoc.append((v,k))

    sort_eurovoc.sort(reverse=True)

    print(len(analysis['EUROVOC_descriptors']))
    cnt = 0
    for e in analysis['EUROVOC_descriptors']:
        if analysis['EUROVOC_descriptors'][e] > 10:
            cnt += 1

    print(cnt)
    niz = """
    |  |  |
    |---|:-:|
    """

    for a,b in sort_eurovoc[:200]:
        niz += '|{}|{}|\n'.format(b,a)

    print(niz)

def make_descriptors_bar_chart():
    sort_eurovoc = []
    for k,v in analysis['EUROVOC_descriptors'].items():
        sort_eurovoc.append((v,k))

    sort_eurovoc.sort(reverse=True)

    data = go.Bar(
        y = [e[1] for e in sort_eurovoc[:20]][::-1],
        x = [e[0] for e in sort_eurovoc[:20]][::-1],
        orientation = 'h',
        marker = dict(
            color = 'orange',
        )
    )
    layout = go.Layout(
        title='Occurences of descriptors',
        margin=go.layout.Margin(
            l=300,
            r=300,
            b=100,
            t=100,
        ),
        font=dict(size=18)
    )

    figure = {
        'data' : [data],
        'layout' : layout
    }

    py.plot(figure, filename='descriptor distribution.html')

def print_markdown_table_subjects():
    print(len(analysis['subject_matter']))

    subj_sort = []
    for k,v in analysis['subject_matter'].items():
        subj_sort.append((v,k))

    subj_sort.sort(reverse=True)
    for k in range(100):
        print(subj_sort[k])

    niz2 = """
    |  |  |
    |---|:-:|
    """

    for a,b in subj_sort[:50]:
        niz2 += '|{}|{}|\n'.format(b,a)

    print(niz2)

def make_subjects_bar_chart():
    sort_subjects = []
    for k,v in analysis['subject_matter'].items():
        sort_subjects.append((v,k))

    sort_subjects.sort(reverse=True)

    data = go.Bar(
        y = [e[1] for e in sort_subjects[:20]][::-1],
        x = [e[0] for e in sort_subjects[:20]][::-1],
        orientation = 'h',
        marker = dict(
            color = 'orange',
        )
    )
    layout = go.Layout(
        title='Occurences of subjects',
        margin=go.layout.Margin(
            l=500,
            r=300,
            b=100,
            t=100,
        ),
        font=dict(size=18)
    )

    figure = {
        'data' : [data],
        'layout' : layout
    }

    py.plot(figure, filename='descriptor distribution.html')

# make_subjects_bar_chart()
# make_date_distribution_bar_chart()
make_descriptors_bar_chart()