from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import os
from dotenv import load_dotenv

class AzureFormRecognizerClient:
    '''
    defines the constructor for the function
    @input: form recognizer endpoint and form recognizer key
    '''
    def __init__(self, form_recognizer_endpoint: str = None, form_recognizer_key: str = None):
        '''
        initialize the env variables from the .env file if it exists
        '''
        load_dotenv()
        
        '''
        initializes several attributes of the class using the values provided as
        parameters or from env variables
        1. pages per embeddings: attribute is set to an integer value obtained from 
        the env variable. If its not defined, then default is 2
        2. session to exclude: initialized as a list of strings containing section nams to 
        exclude. appears to be hard coded and contains sections lkke footnote, etc...
        3. form recognizer endpoint: this attribute is set to the value provided 
        4. key param also established through 
        '''
        self.pages_per_embeddings = int(os.getenv('PAGES_PER_EMBEDDINGS', 2))
        self.section_to_exclude = ['footnote', 'pageHeader', 'pageFooter', 'pageNumber']

        self.form_recognizer_endpoint : str = form_recognizer_endpoint if form_recognizer_endpoint else os.getenv('FORM_RECOGNIZER_ENDPOINT')
        self.form_recognizer_key : str = form_recognizer_key if form_recognizer_key else os.getenv('FORM_RECOGNIZER_KEY')


    '''
    this method performs document analysis using Azure Form Recognizer, extracts content
    from paragraphs and tables in the document's layout, and organizes the content into
    output files based on the self.pages_per_embeddings attribute
    '''
    def analyze_read(self, formUrl):

        '''
        Initialize the DocumentAnalysisClient object, which is used to interact with 
        the Azure Form Recognizer service. Initialized with teh form_recognizer_endpoint and key 
        attributes set in the class constructor
        '''
        document_analysis_client = DocumentAnalysisClient(
            endpoint=self.form_recognizer_endpoint, credential=AzureKeyCredential(self.form_recognizer_key)
        )
        
        '''
        poller initiates the document analysis using the provided URL. The document is 
        analyzed with the prebuilt layout model, which is designed to recognize the layout
        and structure of the documents
        '''
        poller = document_analysis_client.begin_analyze_document_from_url(
                "prebuilt-layout", formUrl)
        
        '''
        results of the document analysis are stored in the layout variable
        '''
        layout = poller.result()

        '''
        the code initializes the empty list called results to store the extracted content
        from the document
        '''
        results = []

        '''
        Iterates through the paragraphs 
        determines the page number in which the paragraph appears in. It also calculates an 
        output file id based on the page number and embeddings attribute. The calculation seems to be used 
        for grouping paragraphs into output files
        rhe paragraphs content is appended into the results list, based on the output file id. If the 
        section role of the paragraph is not in the section to exclude, then we can add into the list
        '''
        for p in layout.paragraphs:
            page_number = p.bounding_regions[0].page_number
            output_file_id = int((page_number - 1 ) / self.pages_per_embeddings)

            if len(results) < output_file_id + 1:
                results.append('')

            if p.role not in self.section_to_exclude:
                results[output_file_id] += f"{p.content}\n"

        '''
        similar idea for tables. determines the page number in which the table is
        present. calculates the output id. processes the cells and puts it into the results array
        '''
        for t in layout.tables:
            page_number = t.bounding_regions[0].page_number
            output_file_id = int((page_number - 1 ) / self.pages_per_embeddings)
            
            if len(results) < output_file_id + 1:
                results.append('')
            previous_cell_row=0
            rowcontent='| '
            tablecontent = ''
            for c in t.cells:
                if c.row_index == previous_cell_row:
                    rowcontent +=  c.content + " | "
                else:
                    tablecontent += rowcontent + "\n"
                    rowcontent='|'
                    rowcontent += c.content + " | "
                    previous_cell_row += 1
            results[output_file_id] += f"{tablecontent}|"
        return results