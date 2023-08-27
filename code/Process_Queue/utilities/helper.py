import os
from azure.storage.blob import BlobServiceClient, BlobClient, BlobType
import requests
import tempfile
import json
import shutil
import spacy
from PIL import Image
import pytesseract


class LLMHelper:
    def __init__(self):
        # Initialize any necessary resources or connections here
        self.blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
        self.nlp = spacy.load("en_core_web_sm")

    def get_blob_sas(self, container_name, file_name):
        # Generate and return a SAS URL for the specified blob (file) in Azure Blob Storage
        # You can use the Azure SDK for Blob Storage to generate the SAS URL
        # See: https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blob-user-delegation-sas-create-python

        # Get a blob client
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=file_name)

        # Generate a SAS token for read access that expires in 24 hours
        sas_token = blob_client.generate_shared_access_signature(
            permission=BlobType.Read,
            expiry=datetime.utcnow() + timedelta(hours=24)
        )

        # Construct the SAS URL
        sas_url = blob_client.url + "?" + sas_token

        return sas_url

    def add_embeddings_lc(self, file_sas):
        # Add embeddings to a text file specified by the SAS URL (file_sas)
        # Implement the logic for adding embeddings to the text file
        
        # Placeholder for adding embeddings
        # Replace this with the actual implementation
        response = requests.get(file_sas)

        if(response.status_code == 200):
            text = response.text
            doc = self.nlp(text)
            embeddings = [token.vector.tolist() for token in doc]
            return embeddings
        else:
            raise Exception("failed to download file from SAS URL")


    def convert_file_and_add_embeddings(self, file_sas, file_name):
        # Convert the file (e.g., using OCR with Layout API) and then add embeddings
        # You can use external services or libraries for OCR processing, as needed
        
        # Download the file from the SAS URL
        response = requests.get(file_sas)
        if response.status_code == 200:
            # Save the file to a temporary location
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(response.content)
            temp_file.close()

            # Placeholder for file conversion (e.g., using OCR)
            # Replace this with the actual implementation
            converted_text = self.perform_ocr(temp_file.name)

            # Placeholder for adding embeddings to the converted text
            # Replace this with the actual implementation
            self.add_embeddings(converted_text)

            # Clean up the temporary file
            os.remove(temp_file.name)
        else:
            raise Exception("Failed to download file from SAS URL")

    def upsert_blob_metadata(self, container_name, file_name, metadata):
        # Update the metadata of a blob (file) in Azure Blob Storage
        # You can use the Azure SDK for Blob Storage to update blob metadata
        # See: https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python#metadata
        
        # Get a blob client
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=file_name)
        
        # Get the existing blob properties
        blob_properties = blob_client.get_blob_properties()

        # Update the blob metadata with the provided metadata
        blob_properties.metadata.update(metadata)

        # Set the updated metadata back to the blob
        blob_client.set_blob_metadata(metadata=blob_properties.metadata)

    def perform_ocr(self, file_path):
        # Placeholder for performing OCR on the file at the given path
        # Replace this with the actual OCR implementation
        # You may use external OCR libraries or services here
        # perform OCR on the image or pdf file at the given file path
        try:
            with Image.open(file_path) as img:
                ocr_text = pytesseract.image_to_string(img)
                return ocr_text
        except Exception as e:
            print(f"OCR Failed: {str(e)}")
            return ""

    def add_embeddings(self, text):
        # Placeholder for adding embeddings to the provided text
        # Replace this with the actual embedding generation logic
        doc = self.nlp(text)
        embeddings = [token.vector.tolist() for token in doc]
        return embeddings
