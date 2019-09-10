import requests

def  downloadFile(url,fileName):
    """
        This functions takes and url of a file on website, downloads it and saves it.
        Works for binary files (PDF's, audio file, image, etc.)
        For dowloading text files (HTML, etc.): change 'response.content' to 'respond.text'

        :param url:       url to a file on web.
                          Example: 'https://www.informea.org/sites/default/files/decisions/ramsar/cop12_resolutions_pdf_e.pdf'
        :param fileName:  set a name for the file.
                          Example: 'name.pdf' If you want to save it in a different folder in your dir -> 'Folder1/name.pdf'
    """
    response = requests.get(url)
    with open(fileName, 'wb') as f:
        f.write(response.content)
