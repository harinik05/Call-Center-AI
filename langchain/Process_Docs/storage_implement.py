import os
import azure.functions as func
from azure.storage.blob import BlobServiceClient, ContentSettings
from blob_storage import AzureBlobStorageClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    
    '''
    initialize the handler with the class name (create an instance to use all its methods)
    '''
    handler = AzureBlobStorageClient()

    '''
    upload a local file to Azure blob storage
    '''
    handler.upload_file("iphone_user_guide_apple.pdf","uploaded_manual.pdf")

    # Get information about all files in the container
    files_info = handler.get_all_files()
    for file_info in files_info:
        print(file_info)

    # Delete a file from the container
    handler.delete_file('uploaded_file.pdf')
    # Parse the request and get the file content
    file_content = req.get_body()

    # Update blob metadata
    metadata = {'author': 'John Doe', 'category': 'PDF'}
    handler.update_blob_metadata('uploaded_file.pdf', metadata)

    # Generate a SAS URL for the container
    container_sas_url = handler.generate_container_sas()
    print(f'Container SAS URL: {container_sas_url}')

    # Generate a SAS URL for a specific blob
    blob_name = 'uploaded_file.pdf'
    blob_sas_url = handler.generate_blob_sas(blob_name)
    print(f'Blob SAS URL: {blob_sas_url}')

    #--

    # Set Azure Blob Storage connection details
    connection_string = os.environ["AzureWebJobsStorage"]
    container_name = "your_container_name"

    # Initialize BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    # Define the blob name and content type
    blob_name = "uploaded_file.pdf"
    content_type = "application/pdf"

    # Upload the file to Blob Storage
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file_content, content_settings=ContentSettings(content_type=content_type))

    return func.HttpResponse("File uploaded successfully.", status_code=200)
