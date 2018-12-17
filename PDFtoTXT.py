from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

def PDFtoTxt(PDFname,TxtFileName, pages=None):
    """
        This function takes a PDF file, converts it to string in variable 'text',
        makes a new text file and copies the content in it.

        :param PDFname:     is name of a PDF you'd like to convert to text file
                                example: 'example1.pdf' or if you have it in a different folder in your dir -> 'Folder1/example1.pdf'
        :param TxtFileName: is name of a new file you'd like to save text from pdf in
        :param pages:       list of pages you'd like to covert. If None, it converts all of them.
        :return:            None

        *** Function 'PDFtoTxt' is from website 'https://www.binpress.com/manipulate-pdf-python/'
        but I added a a part to save it in a .txt file ***
    """
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(PDFname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue().encode('ascii', 'replace')  #.encode(...)  is added*
    output.close
    #till that row, in variable 'text' it's string of all content in pdf file
    txt = open(TxtFileName, 'w+')
    txt.write(text.decode())



