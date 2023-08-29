'''
Import the necessary modules to run this function:
logging: Logging module in python
json: Working with and manupulating JSON file/data
os: Reading and handling environment variables
azure.functions: imports the Azure Function module for creating
functions in Azure
QueueClient: Class in azure fro Queue Storage
LLMHelper: External class for helper functions
'''
import logging, json, os
import azure.functions as func
from azure.storage.queue import QueueClient, BinaryBase64EncodePolicy
from utilities.helper import LLMHelper

'''
Reads the name of Azure Queue Storage queue from an 
environment variable
'''
queue_name = os.environ['QUEUE_NAME']

'''
Main function which is an entry point of Azure function
@input: HTTP Request
@output: HTTP Response
'''
def main(req: func.HttpRequest) -> func.HttpResponse:

    '''
    Logs informational message indicating that the function has
    been requested to start processing the documents
    '''
    logging.info('Requested to start processing all documents received')
    
    '''
    create an object from the LLMHelper() class
    '''
    llm_helper = LLMHelper()
    
    '''
    Calls a method using the blob_client object to retrieve 
    information about all the files in Azure Blob storage
    '''
    files_data = llm_helper.blob_client.get_all_files()
    
    '''
    Filters the list of files that only includes the files where the embeddings 
    have not yet been added. This is based on the metadata field that is added 
    to the files. 
    '''
    files_data = list(filter(lambda x : not x['embeddings_added'], files_data)) if req.params.get('process_all') != 'true' else files_data

    '''
    Converts the list of files into a list of dictionaries, each containing the 
    "filename" field. This is done to prepare the data for adding to the Queue
    '''
    files_data = list(map(lambda x: {'filename': x['filename']}, files_data))
    
    '''
    Creates an instance of QueueClient to interact with Azure Queue Storage specified
    by "queue name". It uses the connection string from he llm_helper.blob_client
    to establish the connection. Then, the message is encoded using BinaryBase64EncodePolicy
    '''
    queue_client = QueueClient.from_connection_string(llm_helper.blob_client.connect_str, queue_name, message_encode_policy=BinaryBase64EncodePolicy())
    
    '''
    Iterates through the file dictionary and sends each file dictionary as JSON-encoded
    message to Azure Queue Storage queue. Encoded in UTF-8 before sending
    '''
    for fd in files_data:
        queue_client.send_message(json.dumps(fd).encode('utf-8'))
    
    '''
    Returns an HTTP response indicating that the conversion has started for 
    some documents
    '''
    return func.HttpResponse(f"Conversion started successfully for {len(files_data)} documents.", status_code=200)