from get_main_links import get_main_links
import get_content_legislation
import get_content_treaty_decisions
import os

# PARAMETERS:

GET_SLOVENIA_RELATED_DOCUMENTS = True

def main():
    
    if GET_SLOVENIA_RELATED_DOCUMENTS:
        if 'main_links_SLO.txt' not in os.listdir():
            get_main_links(True)
        
        get_content_legislation.main(filterSLO = True)
        get_content_treaty_decisions.main(filterSLO = True)
    
    else:
        if 'main_links_ALL.txt' not in os.listdir():
            get_main_links(False)
        
        get_content_legislation.main(filterSLO = False)
        get_content_treaty_decisions.main(filterSLO = False)


if __name__ == '__main__':
    main()