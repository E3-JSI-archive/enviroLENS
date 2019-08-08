import json
import plotly.offline as py
import plotly.graph_objs as go
from collections import defaultdict

with open("eurlex_analysis_2_environment.json", 'r') as infile:
    analysis = json.load(infile)

data = analysis["statistics"]

def year_chart_full_text_available():
    
    x_os = [i for i in range(1900,2020)]
    y_os = []
    y_os2 = []

    for i in range(1900, 2020):
        if str(i) not in data:
            y_os.append(0)
            y_os2.append(0)
        else:
            bad = data[str(i)]['text_lengths'].count(67)
            good = len(data[str(i)]['text_lengths']) - bad
            y_os.append(good)
            y_os2.append(bad)
    
    first = go.Bar(
        x = x_os,
        y = y_os,
        name='full text available'
    )

    second = go.Bar(
        x = x_os,
        y = y_os,
        name = 'full text not available'
    )

    layout = go.Layout(
        barmode = 'stack',
        title='full text availability',
        font=dict(size=18, color='#7f7f7f')
    )

    fig = go.Figure(
        data=[first, second],
        layout = layout
    )

    py.plot(fig, filename='stacked.html')

def average_number_of_descriptros():
    x_os = [i for i in range(1930,2020)]
    y_os = []
    y_os2 = []

    for i in range(1940,2020):
        if str(i) not in data:
            y_os.append(0)
            y_os2.append(0)
        else:
            y_os.append(data[str(i)]["num_of_descriptors"]/data[str(i)]["count_docs"])
            y_os2.append(data[str(i)]["num_of_subjects"]/data[str(i)]["count_docs"])

    bar = go.Bar(
        x=x_os,
        y=y_os,
        name='average number of descriptors'
    )

    bar2 = go.Bar(
        x = x_os,
        y = y_os2,
        name = 'average number of subjects'
    )

    layout = go.Layout(
        barmode='overlay',
        title='average number of descriptors/subjects',
        font=dict(size=18)
    )

    figure = go.Figure(
        data = [bar, bar2],
        layout = layout,
    )

    py.plot(figure, filename='average.html')

# year_chart_full_text_available()
average_number_of_descriptros()