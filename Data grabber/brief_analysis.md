# Brief data analysis

In total 202842 documents on environmental law were collected from [Ecolex](https://www.ecolex.org/). Those are split into 5 main categories and their representations are the following:

* Legislation - 151046
* Literature - 39383
* Treaty decisions - 7882
* Jurisprudence - 2441
* Treaty - 2090

For each of them we have collected various metadata depending on what was available to extract. What we have collected includes: Date, source, meeting/treaty at which the document was discussed, main subjects of the document, general keywords, list of countries / geographical areas to which the document refers on and so on. In many cases (157631) a link to the complete text of the document is available. 

Some of the information can be nicely visualized and is also interesting to see. Below we can see a histogram of document distribution depending on a year in which it was published.

![distribution by year](pictures\year_histogram.png)

As we can see there is a huge increase in number of documents past year 1989. Increase can be explained by increased awareness about our environment and negative impact it may have if we don't act on it. Here we must also consider that some of the growth is here because of popularization of the internet and our tendency to have everything available online.

As expected most of documents are in English. It is the language of over 70% of documents. English is followed by German, French, Spanish and Russian. The other 56 languages represented accumulate to a share of 4.2%.

![language_represenation](\pictures\languages_pie_chart.png)

Below we can find a chart of 30 most common subjects (out of 433). It is worth noting that most of the documents have one main subject, but that is not always the case. Therefore summing all occurences of subjects will exceed the total number of documents.

![popular_subjects](\pictures\subjects.png)

Interesting aspect of data to look at is popularity of various keywords. 

![popular_keywords](\pictures\keywords.png)

In total there are 482 different keywords but they  are distributed much more "equally" in difference to subject distribution. Main reason of course is that for each of document we usually have many different keywords. We can see some correlation between top subjects and top keywords. For example Food & nutrition and inspection, food quality control/food safety both score high in their respective charts. 

Lastly we will check document distribution depending on countries / geographical areas it refers to. 

![geo_area](\pictures\geo_areas.png)
![countries](\pictures\countries.png)

As expected more developed territories and countries have a much higher share of documents with Europe/European Union topping both charts.