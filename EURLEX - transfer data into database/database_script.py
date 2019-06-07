import os
import json
import psycopg2
from time import time

START_TIME = time()

# Database identification parameters
conn_str = {
    'user' : 'postgres',
    'host' : 'localhost',
    'port' : 5432,
    'password' : 'dbpass',
    'dbname' : 'eurlex',
}

# Folder in which documents are stored.
datafolder = 'testdata'

def parse_date(date):
    if date is None:
        return date
    
    day, month, year = date.split('/')
    return '{}-{}-{}'.format(year,month, day)

def parse_argument_into_correct_form(arg):
    """
    This function will leave None arg as None, but will remove any ' characters from strings 
    and also add ' to the front and to the back of the string. That way the arg will be compatible with 
    INSERT statement for postgres.
    """
    if arg is None:
        return arg
    
    arg = arg.replace("'", '')
    # arg = "'" + arg + "'"
    return arg

def create_eurlex_tables():
    """
    With this function we will create tables for eurlex database.
    The databases will be:
    - "documents" with columns [id pk, author, form, date, text]
    - "subjects" with columns [id, name pk]
    - "descriptors" with columns [id, name pk]

    - "document_subjects" with columns [document_id fk, subject_name fk] (document_id, subject_name) Primary key (many to many relation)
    - "document_descriptors" with columns [document_id fk, descriptor_name, fk] (document_id, descriptor_name) Primary key (many to many relation)
    """

    commands = [
        """
        CREATE TABLE subjects (
            subject_id SERIAL,
            subject_name TEXT UNIQUE PRIMARY KEY
        )
        """,
        """
        CREATE TABLE descriptors (
            descriptor_id SERIAL,
            descriptor_name TEXT UNIQUE PRIMARY KEY
        )
        """,
        """
        CREATE TABLE documents (
            document_id SERIAL,
            document_celex_num TEXT PRIMARY KEY,
            document_title TEXT,
            document_author TEXT,
            document_form TEXT,
            document_date DATE,
            document_text TEXT
        )
        """,
        """
        CREATE TABLE document_subjects (
            document_celex_num TEXT,
            subject_name TEXT,
            PRIMARY KEY (document_celex_num, subject_name),
            FOREIGN KEY (document_celex_num) REFERENCES documents (document_celex_num),
            FOREIGN KEY (subject_name) REFERENCES subjects (subject_name)
        )
        """,
        """
        CREATE TABLE document_descriptors (
            document_celex_num TEXT,
            descriptor_name TEXT,
            PRIMARY KEY (document_celex_num, descriptor_name),
            FOREIGN KEY (document_celex_num) REFERENCES documents (document_celex_num),
            FOREIGN KEY (descriptor_name) REFERENCES descriptors (descriptor_name) 
        )
        """
    ]

    # Connect to the database
    conn = psycopg2.connect(**conn_str)
    # Create a cursor
    cursor = conn.cursor()
    # We execute every statement in commands (create tables)
    for command in commands:
        cursor.execute(command)
    
    # We close the cursor
    cursor.close()
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def insert_document_rows():

    conn = psycopg2.connect(**conn_str)
    cursor = conn.cursor()

    current_file_path = os.getcwd()
    data_path = os.path.join(current_file_path, datafolder)

    counter = 0
    count_fails = 0

    for filename in os.listdir(data_path):

        # Checking progress for sanity
        counter += 1
        if counter % 10000 == 0:
            print(counter, count_fails, time() - START_TIME)

        with open(os.path.join(data_path, filename), 'r') as infile:
            document_data = json.load(infile)

        try:
        
            try:
                document_date = document_data['dateEvents_EN']['Date of document'][0]
            except:
                document_date = None
            
            # We transform date into yyyy-mm-dd format or keep it as NULL
            document_date = parse_date(document_date)
            
            # Extract celex number of document from its filename. It is a unique identifier of document.
            document_celex_num = filename[:-5]

            try:
                document_title = document_data['translatedTitle_EN']
            except:
                document_title = None
            
            try:
                document_author = document_data['miscellaneousInformation_EN']['Author'][0]
            except:
                document_author = None
            
            try:
                document_form = document_data['miscellaneousInformation_EN']['Form'][0]
            except:
                document_form = None
            
            try:
                document_text = document_data['text_EN']
            except:
                document_text = None
            
            # We parse all parameters into correct form. ie. leave None values as None, but change
            # strings into 'string'. In that way values passed in INSERT statement are valid with POSTGRES
            # syntax.
            document_celex_num = parse_argument_into_correct_form(document_celex_num)
            document_author = parse_argument_into_correct_form(document_author)
            document_date = parse_argument_into_correct_form(document_date)
            document_form = parse_argument_into_correct_form(document_form)
            document_title = parse_argument_into_correct_form(document_title)
            document_text = parse_argument_into_correct_form(document_text)

            statement = """
            INSERT INTO documents (document_title, document_celex_num, document_author, document_form, document_date, document_text)
            VALUES  (%s, %s, %s, %s, %s, %s);
            """
            
            cursor.execute(statement, (document_title, document_celex_num, document_author, document_form, document_date, document_text))
        
        except:
            count_fails += 1
            print(filename)

    cursor.close()
    conn.commit()
    conn.close()

def insert_subject_descriptor_rows():
    
    conn = psycopg2.connect(**conn_str)
    cursor = conn.cursor()

    current_file_path = os.getcwd()
    data_path = os.path.join(current_file_path, datafolder)

    subjects = set()
    descriptors = set()

    for filename in os.listdir(data_path):
        with open(os.path.join(data_path, filename), 'r') as infile:
            document_data = json.load(infile)

        try:
            subjects = subjects.union(set(document_data['classification_EN']['Subject matter']))
        except:
            pass

        try:
            descriptors = descriptors.union(set(document_data['classification_EN']['EUROVOC descriptor']))
        except:
            pass
    
    statement_subjects = """
    INSERT INTO subjects (subject_name) VALUES 
    """
    for subj in subjects:

        # We remove ' from subject
        subj = parse_argument_into_correct_form(subj)

        statement_subjects += "('{}'), ".format(subj)

    statement_subjects = statement_subjects[:-2] + ';'

    cursor.execute(statement_subjects)

    statement_descriptor = """
    INSERT INTO descriptors (descriptor_name) VALUES 
    """

    for descriptor in descriptors:
        # We remove ' from descriptor
        descriptor = parse_argument_into_correct_form(descriptor)

        statement_descriptor += "('{}'), ".format(descriptor)

    statement_descriptor = statement_descriptor[:-2] + ';'

    cursor.execute(statement_descriptor)

    cursor.close()
    conn.commit()
    conn.close()

def insert_document_subjects_rows():
    
    conn = psycopg2.connect(**conn_str)
    cursor = conn.cursor()

    current_file_path = os.getcwd()
    data_path = os.path.join(current_file_path, datafolder)

    counter = 0
    count_fails = 0

    for filename in os.listdir(data_path):

        # Checking progress for sanity
        counter += 1
        if counter % 1000 == 0:
            print(counter, count_fails, time() - START_TIME)

        with open(os.path.join(data_path, filename), 'r') as infile:
            document_data = json.load(infile)

        document_celex_num = filename[:-5]

        try:
            subjects = document_data['classification_EN']['Subject matter']
        except:
            subjects = []

        statement = """
        INSERT INTO document_subjects (document_celex_num, subject_name) VALUES 
        (%s, %s);
        """

        for subj in subjects:
            subj = parse_argument_into_correct_form(subj)
            cursor.execute(statement, (document_celex_num, subj))

    cursor.close()
    conn.commit()
    conn.close()

def insert_document_descriptors_rows():

    conn = psycopg2.connect(**conn_str)
    cursor = conn.cursor()

    current_file_path = os.getcwd()
    data_path = os.path.join(current_file_path, datafolder)

    counter = 0
    count_fails = 0

    for filename in os.listdir(data_path):

        # Checking progress for sanity
        counter += 1
        if counter % 1000 == 0:
            print(counter, count_fails, time() - START_TIME)

        with open(os.path.join(data_path, filename), 'r') as infile:
            document_data = json.load(infile)

        document_celex_num = filename[:-5]

        try:
            descriptors = document_data['classification_EN']['EUROVOC descriptor']
        except:
            descriptors = []

        statement = """
        INSERT INTO document_descriptors (document_celex_num, descriptor_name) VALUES 
        (%s, %s);
        """

        for descriptor in descriptors:
            descriptor = parse_argument_into_correct_form(descriptor)
            cursor.execute(statement, (document_celex_num, descriptor))
    
    cursor.close()
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_eurlex_tables()
    print('Creating eurlex tables successful.')
    print('Total time passed', time() - START_TIME)
    insert_document_rows()
    print('Populating documents table successful.')
    print('Total time passed', time() - START_TIME)
    insert_subject_descriptor_rows()
    print('Populating descriptors, subjects table successful.')
    print('Total time passed', time() - START_TIME)
    insert_document_subjects_rows()
    print('Populating doc subjects table successful.')
    print('Total time passed', time() - START_TIME)
    insert_document_descriptors_rows()
    print('Populating doc descriptors table successful.')
    print('Total time passed', time() - START_TIME)
