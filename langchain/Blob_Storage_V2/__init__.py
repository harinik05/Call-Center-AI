import os
import azure.functions as func
from azure.storage.blob import BlobServiceClient, ContentSettings
from blob_storage import AzureBlobStorageClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Retrieve the singleton instance
    handler = AzureBlobStorageClient()

    # Use the handler to perform operations
    handler.handler.upload_file_metadata("iphone_user_guide_apple.pdf", "uploaded_manual.pdf")

    # Get information about all files in the container
    files_info = handler.handler.obtain_file_information()
    for file_info in files_info:
        print(file_info)

    # Update blob metadata
    metadata = {'author': 'Apple', 'category': 'PDF'}
    handler.handler.update_blob_metadata('iphone_user_guide_apple.pdf', metadata)

    # Generate a SAS URL for the container
    container_sas_url = handler.handler.retrieve_sas_container()
    print(f'Container SAS URL: {container_sas_url}')

    # Generate a SAS URL for a specific blob
    blob_name = 'uploaded_file.pdf'
    blob_sas_url = handler.handler.retrieve_sas_blob(blob_name)
    print(f'Blob SAS URL: {blob_sas_url}')

    return func.HttpResponse("File uploaded successfully.", status_code=200)
 