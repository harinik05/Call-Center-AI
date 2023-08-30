import os
import azure.functions as func
from azure.storage.blob import BlobServiceClient, ContentSettings
from blob_storage import AzureBlobStorageClient

'''
Singleton design pattern involves creating a class with a private
instance variable and a method to retrieve the instance. 

Optimized the code by creating only one singleton client to minimize 
this overhead, resulting in faster interactions with the Azure blob storage

This also involves the use of encapsulation
'''
class SingletonAzureBlobStorageHandler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingletonAzureBlobStorageHandler, cls).__new__(cls)
            # Initialize the handler only once
            cls._instance.handler = AzureBlobStorageClient()
        return cls._instance

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Retrieve the singleton instance
    handler = SingletonAzureBlobStorageHandler()

    # Use the handler to perform operations
    handler.handler.upload_file("iphone_user_guide_apple.pdf", "uploaded_manual.pdf")

    # Get information about all files in the container
    files_info = handler.handler.get_all_files()
    for file_info in files_info:
        print(file_info)

    # Delete a file from the container
    handler.handler.delete_file('uploaded_file.pdf')

    # Parse the request and get the file content
    file_content = req.get_body()

    # Update blob metadata
    metadata = {'author': 'John Doe', 'category': 'PDF'}
    handler.handler.update_blob_metadata('uploaded_file.pdf', metadata)

    # Generate a SAS URL for the container
    container_sas_url = handler.handler.generate_container_sas()
    print(f'Container SAS URL: {container_sas_url}')

    # Generate a SAS URL for a specific blob
    blob_name = 'uploaded_file.pdf'
    blob_sas_url = handler.handler.generate_blob_sas(blob_name)
    print(f'Blob SAS URL: {blob_sas_url}')

    return func.HttpResponse("File uploaded successfully.", status_code=200)
 