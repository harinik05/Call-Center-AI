###########################################
# __init__.py

# Triggered by Azure Functions (HTTP Request) by receiving
# a POST request containing JSON data, parses this dats
# and processes this using LLMHelper (Large Language Model) class. 
# This function returns a HTTP response containing all the 
# information mapped in a dictionary. 
###########################################

'''
Import the required modules 
logging: module to log messages
json: work with JSON data
azure.functions: module to create Azure functions
LLMHelper: External module for helper functions
'''
import logging, json
import azure.functions as func
from utilities.helper import LLMHelper

'''
Function definition (main)- Entry point of Azure function
@input: func.QueueMessage (Message received from the queue)
@output: none
'''
def main(msg: func.QueueMessage) -> None:

    '''
    Logs an informational message indicating that the function
    is processing a queue item. Uses the content of queue message 
    part of log message
    '''
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))

    '''
    Creates an instance of the LLMHelper() class (object)
    '''
    llm_helper = LLMHelper()

    '''
    Extracts the "filename" field from the JSON content of the queue
    message. The message is initially in UTF-8 and parsed as a JSON format
    '''
    filename_info = json.loads(msg.get_body().decode('utf-8'))['filename']

    '''
    Generates a Shared Access Signature (SAS) URL for the file given 
    in the file name. This URL can be used to access the file in the 
    Azure Blob Storage
    '''
    file_sas = llm_helper.blob_client.retrieve_sas_blob(filename_info)

    '''
    Checks if the file extension is txt. If the file has txt extension:
    - It will call the add_embeddings_lc method of llm_helper object to add 
    embeddings oiri process the text content of the file

    if the file extension is not txt:
    Calls a different method to convert the file content and then process the 
    file contents/add embeddings
    '''
    if filename_info.endswith('.txt'):
        # Add the text to the embeddings
        llm_helper.add_embeddings_preprocess(file_sas)
    else:
        # Get OCR with Layout API and then add embeddigns
        llm_helper.file_conversion_add_embeddings_preprocess(file_sas , filename_info)

    '''
    Updates the metadata of the blob in the Azure Blob Storage, setting
    the metadata to sucess message. 
    '''
    llm_helper.blob_client.upsert_blob_metadata(filename_info, {'embeddings_added': 'true'})