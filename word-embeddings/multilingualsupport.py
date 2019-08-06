import requests

def translate_query(text, source_language, target_language):
    """
    Function that takes text, source language and target language as parameters and returns the translation 
    of text from source language to target language.

    See https://ctrlq.org/code/19909-google-translate-api for clearer explanation.
    API endpoint on the link below is free for unlimited translations. We construct a query and get a json file 
    as a response.

    Here is an example of API response:

    text: sladoled
    source_language: sl
    target_language: en

    [[['ice cream', 'sladoled', None, None, 3, None, None, None,
     [[['42dfd4d688fe6894ea0ebbf6149b3d3e', 'SouthSlavicB_bebgbshrslsruk_en_2019q2.md']]]]],
      None, 'sl']

    """

    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=" + source_language + \
        "&tl=" + target_language + "&dt=t&q=" + text
    
    request = requests.get(url)

    try:
        # JSON response is split into sentences. Each sentence is translated separately.
        return ''.join(e[0] for e in request.json()[0])
    except:
        return False

translation = translate_query('Pred tremi meseci so v Nemčiji elektrificirali del avtoceste A5, ki ima skrajno desni pas namenjen za vožnjo hibridnih tovornjakov. Gre za pet kilometrov dolg odsek med krajema Langen in Weiterstadt. Tri mesece pozneje se tam le redko pelje električni tovornjak, a se bo frekvenca v prihodnjih letih povečala, obljubljajo.', 'sl', 'en')

print(translation)