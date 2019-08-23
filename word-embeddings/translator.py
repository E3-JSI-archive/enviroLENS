class Translator():
    """
    Class that can be used to translate unlimited text using Google's free API.
    """

    def __init__(self):
        self.base_url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl="
    

    def translate_query(self, source_language, target_language, text):
        """
        Function that will translate text from source to target language.

        Given source and target language and text the function will make an 
        API call to google endpoint that is free for unilimited use.
        See https://ctrlq.org/code/19909-google-translate-api for clearer explanation.

        Example of a Google API response:
        
        text: sladoled
        source_language: sl
        target_language: en

        [[['ice cream', 'sladoled', None, None, 3, None, None, None,
        [[['42dfd4d688fe6894ea0ebbf6149b3d3e', 'SouthSlavicB_bebgbshrslsruk_en_2019q2.md']]]]],
        None, 'sl']


        Parameters:
            source_language : str
                2 character string representing language. Example : 'sl' - slovene, 'en' - english
            target_language : str
                2 character string representing language. Example : 'sl' - slovene, 'en' - english
            text : str
                String containing text that we wish to translate.
        
        Returns:
            string
                string containing text translated into target language.
        """

    url = self.base_url + source_language + "&tl=" + target_language + "&dt=t&q=" + text
    
    request = requests.get(url)

    try:
        # JSON response is split into sentences. Each sentence is translated separately.
        return ''.join(e[0] for e in request.json()[0])
    except:
        return False



