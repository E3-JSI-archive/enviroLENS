import psycopg2
import os
import json

FOLDERS = ['jurisprudence', 'legislation', 'treaty', 'treaty decisions', 'literature']

# Database identification parameters
conn_str = {
    'user' : 'postgres',
    'host' : 'localhost',
    'port' : 5432,
    'password' : 'dbpass',
    'dbname' : 'ecolex',
}

def parse_argument_into_correct_form(arg):
    """
    This function will leave None arg as None, but will remove any ' characters from strings
    and also add ' to the front and to the back of the string. That way the arg will be compatible with
    INSERT statement for postgres.
    """
    if arg is None or type(arg) is not str:
        return arg
    
    arg = arg.replace("'", '')
    # arg = "'" + arg + "'"
    return arg

def wrap_argument_into_list(arg):
    """
    This function will receive either a string or a list, but will in the end return a list.
    
    For example: 'cat' -> ['cat'], ['a', 'b'] -> ['a', 'b']

    Parameters:
        arg: list or string
    
    Returns
        arg wrapped into a list
    """
    
    if type(arg) == list:
        return arg
    elif type(arg) == str:
        return [arg]
    elif arg is None:
        return []
    else:
        print('I shouldnt be here', arg)
        return []

def create_ecolex_documents_table():
    """
    This function create documents table in ecolex database.
    This will be a huge table containing combined data of all 5 
    different document types.
    
    The table will consist of:
    """

    command = """
    CREATE TABLE documents (
        document_id INTEGER PRIMARY KEY,
        classification TEXT, 
        fullText TEXT,
        ISBN TEXT,
        ISSN TEXT,
        abstract TEXT,
        basin TEXT,
        category TEXT,
        courtName TEXT,
        date TEXT,
        depository TEXT,
        documentType TEXT,
        entryIntoForce TEXT,
        entryIntoForceNotes TEXT,
        fieldOfApplication TEXT,
        fullTextLink TEXT,
        journalSeries TEXT,
        meetingLink TEXT,
        meetingName TEXT,
        name TEXT,
        pages TEXT,
        placeOfAdoption TEXT,
        placePublication TEXT,
        publisher TEXT,
        referenceNumber TEXT,
        seatOfCourt TEXT,
        sourceID TEXT,
        sourceLink TEXT,
        sourceName TEXT,
        status TEXT, 
        title TEXT,
        treatyLink TEXT,
        treatyName TEXT,
        typeOfCourt TEXT,
        website TEXT,
        websiteLink TEXT
    )
    """

    conn = psycopg2.connect(**conn_str)
    cursor = conn.cursor()
    cursor.execute(command)

    cursor.close()
    conn.commit()
    conn.close()

def create_many_to_many_tables():
    """
    This function creates tables that are many to many or one to many linked with documents.
    For example geographical locations, authors, participants, keywords, subjects and so on.
    """

    commands = [
        """
        CREATE TABLE document_authors (
            document_id INTEGER,
            author TEXT,
            PRIMARY KEY (document_id, author),
            FOREIGN KEY (document_id) REFERENCES documents (document_id)
        )
        """,
        """
        CREATE TABLE document_areas (
            document_id INTEGER,
            area TEXT,
            PRIMARY KEY (document_id, area),
            FOREIGN KEY (document_id) REFERENCES documents (document_id)
        )
        """,
        """
        CREATE TABLE document_judges (
            document_id INTEGER,
            judge TEXT,
            PRIMARY KEY (document_id, judge),
            FOREIGN KEY (document_id) REFERENCES documents (document_id)
        )
        """,
        """
        CREATE TABLE document_keywords (
            document_id INTEGER,
            keyword TEXT,
            PRIMARY KEY (document_id, keyword),
            FOREIGN KEY (document_id) REFERENCES documents (document_id)
        )
        """,
        """
        CREATE TABLE document_languages (
            document_id INTEGER,
            language TEXT,
            PRIMARY KEY (document_id, language),
            FOREIGN KEY (document_id) REFERENCES documents (document_id)
        )
        """,
        """
        CREATE TABLE document_participants (
            document_id INTEGER,
            participant TEXT,
            PRIMARY KEY (document_id, participant),
            FOREIGN KEY (document_id) REFERENCES documents (document_id)
        )
        """,
        """
        CREATE TABLE document_subjects (
            document_id INTEGER,
            subject TEXT,
            PRIMARY KEY (document_id, subject),
            FOREIGN KEY (document_id) REFERENCES documents (document_id)
        )
        """
    ]

    conn = psycopg2.connect(**conn_str)
    cursor = conn.cursor()

    for command in commands:
        cursor.execute(command)
    
    cursor.close()
    conn.commit()
    conn.close()

def insert_document(document, classification, document_id):
    """
    This function inserts all of relevant documents data into the database.

    Parameters:
        document:
            dictionary of documents data
    
    Returns:
        boolean whether insertion was successful
    """

    # Connection and cursor
    conn = psycopg2.connect(**conn_str)
    cursor = conn.cursor()

    # Creating statement for insertion into documents table
    statement = """
    INSERT INTO documents (document_id, classification, fullText, ISBN, ISSN, abstract,
    basin, category, courtName, date, depository, documentType, entryIntoForce,
    entryIntoForceNotes, fieldOfApplication, fullTextLink, journalSeries, meetingLink,
    meetingName, name, pages, placeOfAdoption, placePublication, publisher, referenceNumber,
    seatOfCourt, sourceID, sourceLink, sourceName, status, title, treatyLink, treatyName,
    typeOfCourt, website, websiteLink) VALUES (
    """ + "%s, "*35 + "%s);"

    data = [document_id, classification, None] # classification and fullText
    
    ISBN = document.get('ISBN', None)
    ISSN = document.get('ISSN', None)
    abstract = document.get('abstract', None)
    basin = document.get('basin', None)
    category = document.get('category', None)
    courtName = document.get('courtName', None)
    date = document.get('date', None)
    depository = document.get('depository', None)

    data.extend([ISBN, ISSN, abstract, basin, category, courtName, date, depository])

    documentType = document.get('documentType', None)
    entryIntoForce = document.get('entryIntoForce', None)
    entryIntoForceNotes = document.get('entryIntoForceNotes', None)
    fieldOfApplication = document.get('fieldOfApplication', None)
    fullTextLink = document.get('fullTextLink', None)

    data.extend([documentType, entryIntoForce, entryIntoForceNotes, fieldOfApplication, fullTextLink])

    journalSeries = document.get('journal/series', None)
    meetingLink = document.get('meetingLink', None)
    meetingName = document.get('meetingName', None)
    name = document.get('name', None)
    pages = document.get('pages', None)

    data.extend([journalSeries, meetingLink, meetingName, name, pages])

    placeOfAdoption = document.get('placeOfAdoption', None)
    placePublication = document.get('placePublication', None)
    publisher = document.get('publisher', None)
    referenceNumber = document.get('referenceNumber', None)
    seatOfCourt = document.get('seatOfCourt', None)
    
    data.extend([placeOfAdoption, placePublication, publisher, referenceNumber, seatOfCourt])

    sourceID = document.get('sourceID', None)
    sourceLink = document.get('sourceLink', None)
    sourceName = document.get('sourceName', None)
    status = document.get('status', None)
    title = document.get('title', None)
    treatyLink = document.get('treatyLink', None)
    treatyName = document.get('treatyName', None)
    typeOfCourt = document.get('typeOfCourt', None)
    website = document.get('website', None)
    websiteLink = document.get('websiteLink', None)

    data.extend([sourceID, sourceLink, sourceName, status, title, treatyLink, treatyName, typeOfCourt,
    website, websiteLink])

    data = list(map(parse_argument_into_correct_form, data))

    cursor.execute(statement, data)

    ########################################################################################
    # Statement for document_authors table:

    statement_authors = """
    INSERT INTO document_authors (document_id, author) VALUES (%s, %s);
    """

    authors = document.get('author', [])

    for author in authors:
        cursor.execute(statement_authors, (document_id, author))
    
    ########################################################################################
    # Statement for document_areas table:
    # We need to be careful because something the value is a list of string and othertime
    # it is just a single string.
    
    all_areas = []

    countries = wrap_argument_into_list(document.get('country/Territory', []))
    geo = wrap_argument_into_list(document.get('geographicalArea', []))

    all_areas += countries + geo

    statement_area = """
    INSERT INTO document_areas (document_id, area) VALUES (%s, %s);
    """

    for area in all_areas:
        cursor.execute(statement_area, (document_id, area))
    
    #######################################################################################
    # Statement for document judges

    judges = wrap_argument_into_list(document.get('judge', []))

    statement_judge =  """
    INSERT INTO document_judges (document_id, judge) VALUES (%s, %s);
    """
    for judge in judges:
        cursor.execute(statement_judge, (document_id, judge))
    
    #######################################################################################
    # Statement keywords

    keyword = wrap_argument_into_list(document.get('keyword', []))
    keywords = wrap_argument_into_list(document.get('keywords', []))

    all_keywords = keyword + keywords

    statement_keyword = """
    INSERT INTO document_keywords (document_id, keyword) VALUES (%s, %s);
    """

    for key in all_keywords:
        cursor.execute(statement_keyword, (document_id, key))  
    
    ########################################################################################
    # Statement languages

    languages = wrap_argument_into_list(document.get('language', []))

    statement_language = """
    INSERT INTO document_languages (document_id, language) VALUES (%s, %s);
    """

    for language in languages:
        cursor.execute(statement_language, (document_id, language))

    #######################################################################################
    #  Statement participants
    
    ## Participants are actually dictionaries ...
    
    # participants = wrap_argument_into_list(document.get('participants', []))

    # print(participants)
    # statement_participant = """
    # INSERT INTO document_participants (document_id, participant) VALUES (%s, %s);
    # """

    # for participant in participants:
    #     cursor.execute(statement_participant, (document_id, participant))
    
    ######################################################################################
    # Statement subjects

    subject = wrap_argument_into_list(document.get('subject', []))
    subjects = wrap_argument_into_list(document.get('subjects', []))

    all_subjects = subject + subjects

    statement_subjects = """
    INSERT INTO document_subjects(document_id, subject) VALUES (%s, %s);
    """

    for subject in all_subjects:
        cursor.execute(statement_subjects, (document_id, subject))

        
    # Closing the connection
    cursor.close()
    conn.commit()
    conn.close()



if __name__ == '__main__':

    ## UNCOMMENT if table are not already created
    create_ecolex_documents_table()
    create_many_to_many_tables()

    count = 0

    current_path = os.getcwd()
    for folder in FOLDERS:
        folder_path = os.path.join(current_path, folder)

        for filename in os.listdir(folder_path):
            with open(os.path.join(folder_path, filename), 'r') as infile:
                document = json.load(infile)
                insert_document(document, folder, count)

                count += 1 
                if count % 100 == 0:
                    print(count)
