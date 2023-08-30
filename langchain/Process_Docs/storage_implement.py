import os
import azure.functions as func
from azure.storage.blob import BlobServiceClient, ContentSettings
from blob_storage import AzureBlobStorageClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Parse the request and get the file content
    file_content = req.get_body()

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
