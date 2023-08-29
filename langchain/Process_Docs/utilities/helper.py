import os,json
from azure.storage.blob import BlobServiceClient, BlobType
from azure.storage.queue import QueueClient, BinaryBase64EncodePolicy

class LLMHelper:
    def __init__(self, storage_connection_string):
        # Initialize Azure Blob Service Client
        self.blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)

        # Initialize Azure Queue Client
        self.queue_client = None  # Initialize as None; will be set up later

    def initialize_queue_client(self, queue_name):
        # Initialize the QueueClient for Azure Queue Storage
        self.queue_client = QueueClient.from_connection_string(
            self.blob_service_client.connection_string,
            queue_name,
            message_encode_policy=BinaryBase64EncodePolicy()
        )

    def get_all_files(self, container_name):
        # Retrieve information about all files in a container in Azure Blob Storage
        # You need to implement this method to list and gather file information.
        # Retrieve information about all files in the specified container
        container_client = self.blob_service_client.get_container_client(container_name)
        
        # Create an empty list to store file information
        files_data = []

        # List all blobs (files) in the container
        blob_list = container_client.list_blobs()
        
        for blob in blob_list:
            # Extract relevant information about each file (blob)
            file_info = {
                "filename": blob.name,
                "content_type": blob.content_settings.content_type,
                "size": blob.size,
                # Add more metadata or properties as needed
            }
            files_data.append(file_info)

        return files_data

    def send_file_to_queue(self, file_info, queue_name):
        # Send file information to an Azure Queue for processing
        # You can use the initialized QueueClient for this.
        # Send file information to the Azure Queue for processing
        
        # Ensure that the QueueClient is initialized
        if self.queue_client is None:
            raise Exception("QueueClient is not initialized. Call initialize_queue_client() first.")

        # Convert the file_info dictionary to a JSON string
        file_info_json = json.dumps(file_info)
        
        try:
            # Send the JSON message to the queue
            self.queue_client.send_message(file_info_json)
        except Exception as e:
            # Handle any exceptions that may occur during message sending
            print(f"Failed to send message to the queue: {str(e)}")

    def mark_file_as_processed(self, container_name, file_name):
        # Mark a file as processed (e.g., by updating its metadata) in Azure Blob Storage
        # Ensure that the BlobServiceClient is initialized
        if self.blob_service_client is None:
            raise Exception("BlobServiceClient is not initialized.")

        # Create a blob client for the file in the specified container
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=file_name)

        try:
            # Get the existing blob properties
            blob_properties = blob_client.get_blob_properties()

            # Update the blob metadata to mark it as processed
            blob_properties.metadata.update({"processed": "true"})

            # Set the updated metadata back to the blob
            blob_client.set_blob_metadata(metadata=blob_properties.metadata)
        except Exception as e:
            # Handle any exceptions that may occur during metadata update
            print(f"Failed to mark the file as processed: {str(e)}")
